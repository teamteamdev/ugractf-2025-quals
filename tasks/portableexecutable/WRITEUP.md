# Portable executable: Write-up

> сомневаюсь

Дан очень небольшой `.exe`-файл (944 байта), который при запуске отдаёт нечто странное:

```shell
$ wine ./flag.exe
??h?e? ?f?l?a?g? ?i?s? ?h?i?d?d?e?n? ?s?o?m?e?w?h?e?r?e?
?
```

Вспоминаем, что Windows использует вариант UTF-16, а не UTF-8, который в терминале, и читаем сообщение правильно:

```shell
$ wine ./flag.exe | iconv -f utf16 -t utf8
The flag is hidden somewhere
```

Отлично, «флаг где-то спрятан». Ничего нового. Посмотрим, что из себя представляет этот бинарь в hex-виде:

![](./writeup/xxd.png)

Ничего интересного — видна строка «The flag is hidden somewhere» в UTF-16 и в самом начале странное «This program can....be run in DOS mode.» По этой строке не гуглится ничего, кроме кучи жалоб на строку «This program cannot be run in DOS mode.», и объяснений, что она просто есть в большинстве EXE-шек.

Portable executable — это ещё и название [формата исполняемых файлов](https://en.wikibooks.org/wiki/X86_Disassembly/Windows_Executable_Files#PE_Files), которые используются для Windows. По этой же ссылке можно найти описание [DOS stub](https://en.wikibooks.org/wiki/X86_Disassembly/Windows_Executable_Files#MS-DOS_header), который есть в каждом PE-файле, чтобы сказать пользователям DOS, что они запускают исполняемый файл не так, как надо.

А тут строка говорит, что в DOS mode запустить можно. Попробуем и получим:

![](./writeup/dosbox.png)

Забираем флаг.

В самом деле, portable executable — можно не только на винде, но и в DOS запустить!

Флаг: **ugra_dos*_stub_is_useful_kgsou0541h0u8ly5sa1z384j**

Альтернативное решение 1: Открыть в IDA и посмотреть на необычный DOS stub:

![](./writeup/ida.png)

Альтернативное решение 2: Попросить cyberchef сбрутить xor с known plaintext "ugra"

![](./writeup/cyberchef.png)

## Интересные факты

Заменять DOS stub с «дефолтного» (который просто выдаёт "This program cannot be run in DOS mode.") на свой `llvm-lld` (свободный компоновщик) научился только с 20-й версии, которая вышла во время соревнования. В связи с этим, и чтобы не переусложнять и без того непростую сборку через `zig cc` в репозитории лежит заранее собранный исполняемый файл с заглушкой вместо флага.
