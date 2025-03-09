# PNG: Write-up

Дан сломанный PNG-файл. При попытке его открыть некоторые просмотрщики изображения выводят ошибку `Fatal error reading PNG image file: PNG file corrupted by ASCII conversion`. Другие просто говорят, что файл не является PNG. Можно открыть [страницу про PNG в Википедии](https://en.wikipedia.org/wiki/PNG#File_format) и шестнадцатеричный редактор и увидеть, что вместо `0d 0a` в заголовке записано `0a`. Так или иначе, из этих данных и условия очевидно, что файл прогнали через `dos2unix`, чего делать категорически не стоило.

Заменим в заголовке руками первый LF на CRLF и попробуем открыть файл заново. Большинству просмотрщиков он всё равно не нравится, но Chromium, например, справляется с тем, чтобы показать начало файла, где видны символы `ug` (другие команды могли видеть чуть больше текста, но весь флаг не видел никто):

![Chromium](writeup/header_crlf_chromium.png)

GIMP также справляется показать начало файла, но дальше декодировать его не может. Вероятно, декодирование упёрлось в какой-то LF в данных, который на самом деле должен был быть CRLF.

Заменить все LF на CRLF, очевидно, будет некорректно, потому что какие-то (почти все!) из LF изначально и были LF. Перебрать, какие LF заменять на CRLF, можно, но файл имеет длину около 1 мегабайта, и перебирать ≈16 позиций из ≈4096 и проверифицировать каждый файл нереально.

Почитаем больше про формат PNG. Данные разбиты на чанки, из которых самый содержательный — `IDAT`: именно в нём закодированны данные картинки. Также у чанков есть контрольная сумма! Получается, можно восстанавливать чанки независимо.

Начнём с того, что распарсим чанки из файла. У чанков нет маркера конца, но есть длина в байтах. Но замена CRLF на LF сдвинула какие-то байты ближе, поэтому этой длине больше верить нельзя. Как же тогда выдрать чанки? О! 4 символа `IDAT` вряд ли встретятся подряд в данных, поэтому можно просто найти все вхождения подстроки `IDAT` в файле и найти границы чанков таким образом. А после последнего чанка `IDAT` будет чанк `IEND`:

```python
data = open("writeup/flag.png", "rb").read()

iend_i = data.rfind(b"IEND")
idat_i = data.find(b"IDAT")

while idat_i < iend_i:
    next_i = data.find(b"IDAT", idat_i + 4)
    if next_i == -1:
        next_i = iend_i
    chunk = data[idat_i - 4:next_i - 4]
    idat_i = next_i

    print("IDAT chunk of stored length (with header)", len(chunk))
```

```
IDAT chunk of stored length (with header) 65547
IDAT chunk of stored length (with header) 65546
IDAT chunk of stored length (with header) 65547
IDAT chunk of stored length (with header) 65547
IDAT chunk of stored length (with header) 65547
IDAT chunk of stored length (with header) 65548
IDAT chunk of stored length (with header) 65548
IDAT chunk of stored length (with header) 65548
IDAT chunk of stored length (with header) 65547
IDAT chunk of stored length (with header) 65547
IDAT chunk of stored length (with header) 65548
IDAT chunk of stored length (with header) 65548
IDAT chunk of stored length (with header) 65546
IDAT chunk of stored length (with header) 6732
```

Достанем теперь из чанка длину, которую сохранял энкодер. Разность между ней и хранимой длиной — это в точности количество потерянных CR:

```python
stored_length = len(chunk) - 12
expected_length, = struct.unpack(">L", chunk[:4])

print("IDAT chunk with", expected_length - stored_length, "CRs missing,", chunk.count(b'\n'), "LFs present")
```

```
IDAT chunk with 1 CRs missing, 265 LFs present
IDAT chunk with 2 CRs missing, 266 LFs present
IDAT chunk with 1 CRs missing, 234 LFs present
IDAT chunk with 1 CRs missing, 246 LFs present
IDAT chunk with 1 CRs missing, 246 LFs present
IDAT chunk with 0 CRs missing, 225 LFs present
IDAT chunk with 0 CRs missing, 233 LFs present
IDAT chunk with 0 CRs missing, 207 LFs present
IDAT chunk with 1 CRs missing, 260 LFs present
IDAT chunk with 1 CRs missing, 220 LFs present
IDAT chunk with 0 CRs missing, 252 LFs present
IDAT chunk with 0 CRs missing, 245 LFs present
IDAT chunk with 2 CRs missing, 281 LFs present
IDAT chunk with 0 CRs missing, 30 LFs present
```

Другое дело! Перебрать одну или две позиции среди ≈250 совершенно реально:

```python
stored_body = chunk[8:-4]
expected_crc, = struct.unpack(">L", chunk[-4:])

lf_positions = [i for i, c in enumerate(stored_body) if c == b"\n"[0]]

for insert_cr_at in itertools.combinations(lf_positions, expected_length - stored_length):
    fixed_body = stored_body
    for i in insert_cr_at[::-1]:
        fixed_body = fixed_body[:i] + b"\r" + fixed_body[i:]

    if zlib.crc32(b"IDAT" + fixed_body) == expected_crc:
        print("Chunk recovered")
        recovered_idat.append(fixed_body)
        break
else:
    assert False, "Failed to recover chunk"
```

Осталось сгенерировать корректный PNG-файл с чанками `IHDR`, `IDAT` и `IEND`. `IHDR` можно взять прямо из исходного файла, он не поломался:

```python
ihdr_i = data.find(b"IHDR")
ihdr_length, = struct.unpack(">L", data[ihdr_i - 4:ihdr_i])
ihdr = data[ihdr_i - 4:ihdr_i + 8 + ihdr_length]
```

А оставшиеся чанки сформируем вручную:

```python
def write_chunk(type: bytes, content: bytes):
    f.write(struct.pack(">L", len(content)) + type + content + struct.pack(">L", zlib.crc32(type + content)))

with open("recovered.png", "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n")
    f.write(ihdr)
    for idat in recovered_idat:
        write_chunk(b"IDAT", idat)
    write_chunk(b"IEND", b"")
```

И вот картинка восстановлена:

![recovered.png](writeup/recovered.png)

Флаг: **ugra_this_sign_wont_stop_me_because_i_cant_read_geo58l23jcirfqnzpolkpkqz**
