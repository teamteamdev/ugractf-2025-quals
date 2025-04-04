# Жужелица I: Write-up

На сайте BBCoin можно скачать архив, где есть два файла: клиент BBCoin ([`client.py`](app/client.py)) и библиотека к криптосистеме Жужелица ([`zhuzhelitsa.py`](app/zhuzhelitsa.py)). Начнем изучать задание с первого.

Клиент создаёт криптокошелек, если он отсутствует, и при этом даёт возможность выбрать, нужно ли использовать «hardened» криптографию. После этого аккаунт создаётся на сервере, а локально сохраняются адрес и приватный ключ. При последующих запусках информация о балансе и типе криптографии достаётся с сервера исключительно с помощью адреса.

Проверим, какой тип криптографии использует разработчик криптовалюты, упомянутый в условии задания, и есть ли на его кошельке деньги. Запустим клиент, позволим ему создать новый аккаунт, а затем в `bbwallet.json` руками заменим адрес на нужный:

```
$ python3 client.py 
Using account umNAIr6rSEjKrqpgvv3i2k
Using default cryptography settings
Your balance: 100 BBCoins
Would you like to buy a flag? [y/n] 
```

Отсюда мы получаем два куска информации: деньги на флаг есть, а hardened-криптография отключена. Но при попытке купить флаг выводится:

```
Would you like to buy a flag? [y/n] y
Wrong decoded hash: expected b'm0\xae\xce\nL\xb0\xeeJD\xbe\x17\x1c\n\xbb\xb8C\x05\xa7L\x83;\xad\x9f)\xa2\n\xc3\xdfu\xeb\x0f', got b'%1\x94\x93/\x8b\xdbYn\x00M\xfc+g\x8dA\xec\x90\xee\xc4^\xea\x17\x9a\xb4\x17\x08+[ \x13\x8c'
```

Итак, нам нужно подобрать приватный ключ. В нормальной ситуации это невозможно, но здесь ситуация необычная по двум причинам:

1. Мы видим много байт информации, которые сервер обычно никому не должен отдавать, а значит, по ним можно попытаться восстановить ключ.
2. Криптография используется своя, а значит, вероятно, уязвима к каким-то атакам.

Отправляемся читать код Жужелицы.

Ключом выступает некая перестановка на 256 элементах (по сути S-box), к которой применяются парочка не очень важных проверок. Есть функции блочного шифрования и дешифрования, применяющие легко обратимые операции (при условии, что S-box известен). Подпись реализована через шифрование SHA-256 хеша строки в режиме ECB, верификация — через расшифровку подписи и сравнение с ожидаемым хешом.

Благодаря тому, что сервер при несовпадении хешей выводит результат дешифровки, мы получаем оракула для [chosen-ciphertext атаки](https://en.wikipedia.org/wiki/Chosen-ciphertext_attack). Общая идея простая: посылая много разных запросов на дешифровку и оценивая результат дешифровки, можно понемного вытащить информацию о ключе и в итоге восстановить его целиком. Этим и займемся.

В default-режиме шифрования процедура дешифровки одного блока выглядит следующим образом:

```python
block = input
block = shuffle(block, INV_SHUFFLE[1])
block = transpose(block)
block = permute(block, p_inv) # (1)
block = shuffle(block, INV_SHUFFLE[0])
block = transpose(block)
block = permute(block, p_inv) # (2)
output = block
```

Здесь:

- `shuffle` переставляет местами байты в 8-байтном блоке `block`, используя перестановку из второго аргумента.
- `transpose` переставляет `i`-й бит `j`-го байта в `j`-й бит `i`-го байта, т.е. транспонирует битовую матрицу.
- `permute` применяет S-box из `p_inv` к байтам из `block` поэлементно

В этой схеме мы можем вставить произвольный `input` и знаем для него `output`, а конечная цель — узнать `p_inv`.

С двумя вызовами `permute` работать сложно, и взаимодействуют они неочевидным образом, поэтому попробуем подобрать вход так, чтобы один из вызовов `permute` превратился или в no-op, или во что-то легко предсказуемое. Можно, например, установить `input` так, чтобы к моменту (1) все байты в `block` совпадали и были равны `x`. Посмотрим, что случится:

```python
# Подобрали операции ровно так, чтобы к моменту (1) в `block` было `[x] * 8`
input = shuffle(transpose([x] * 8), SHUFFLE[1])

...
block = permute(block, p_inv) # (1) <- после этого в `block` лежит `[p_inv[x]] * 8`
block = shuffle(block, INV_SHUFFLE[0]) # ничего не делает, потому что все байты равны
block = transpose(block) # в ячейке `block[i]` лежит `255`, если в `p_inv[x]` стоит бит `i`, и `0` иначе
block = permute(block, p_inv) # (2) <- содержит либо `p_inv[255]`, либо `p_inv[0]` в зависимости от условия выше
output = block
```

Ага! Теперь в `output` все байты имеют одно из двух значений — `p_inv[255]` или `p_inv[0]`:

```
x = 00 -> 4a cd 4a cd 4a 4a cd 4a
x = 01 -> 4a 4a 4a 4a cd 4a cd 4a
x = 02 -> 4a 4a cd 4a cd cd 4a 4a
x = 03 -> cd 4a 4a 4a cd 4a cd 4a
x = 04 -> 4a cd cd 4a 4a 4a 4a cd
...
```

За один раз сервер позволяет дешифровать 32-байтную строку, то есть 4 блока, поэтому за 64 запроса можно выкачать все соответствия.

Осталось понять, какое из двух чисел в выводе — `p_inv[0]`, а какое — `p_inv[255]`. Переберём оба варианта и восстановим две перестановки `p_inv`, обратим их и получим `p`, и запишем по очереди каждую из них как приватный ключ в `bbwallet.json`, после чего купим флаг. Одна из перестановок подойдет.

Решение на Python вместе с оптимизацией, описанной в следующем разделе, можно увидеть в файле [solve.py](solve.py).

Флаг: **ugra_pwned_by_fbi_5jp5mstr8qq5**

## Чуть более оптимальное решение

Выше сказано, что нужно опробовать две перестановки. На самом деле, легко сразу определить, какая из двух подойдет. Следите за руками.

Обозначим произвольный из байтов результата (в примере выше это либо `4a`, либо `cd`) за `a`. Восстановим перестановку-кандидат `q` в предположении, что `a` — это `p_inv[0]`, и вторую перестановку `~q` в предположении, что `a` — это `p_inv[255]`. `~q` она называется потому, что соответствует побайтовой инверсии `q`.

Ясно, что `q` может быть корректна только при условии `q[0] == a`, а `~q` может быть корректна только при `(~q)[255] == a`. Оба этих условия сразу верны быть не могут, ведь тогда бы выполнялось `q[0] ^ 0xff == q[255]`, а функция `is_safe_permutation` такие ключи генерировать не позволяет. Поэтому корректен может быть только один из кандидатов, а какой именно — проверяется сравнением `q[0] == a`.

## Делаем выводы

Давайте подведём промежуточные итоги.

1. В некоторых криптосистемах опасно позволять пользователю дешифровать произвольные данные, выдавая при этом результат. Это так далеко не всегда, но нужно понимать, какие гарантии даёт конкретная криптосистема, которую вы используете.

2. Криптосистема не обязательно хороша, даже если она не уязвима к общим атакам, таким как, например, дифференциальный криптоанализ. Вполне возможно, что есть уязвимость, применимая только к конкретной системе.

3. Раундов в симметричных шифрах много не просто так. В этом задании мы аккуратным подбором входных данных отбросили один раунд, а потом смогли сходу решить второй. Если бы раундов было больше, задача была бы сложнее — см. [Жужелица II](../zhuzhelitsa2/), где раундов 3, а не 2.

## Почему именно `shuffle`, `transpose` и `permute`?

`permute` и случайный S-box — фишка задачи, без неё Жужелица не была бы Жужелицей и решалась бы совсем иначе. Во время разработки задания мы посчитали, что эта идея породит достаточно нестандартную криптосистему, которую будет интересно ломать, но к которой при этом не найдётся готовых подходов.

`transpose` перемешивает энтропию между байтами. Если бы не `transpose`, то каждый байт бы заменялся по какому-то определённому правилу независимо, и вычислить соответствие было бы намного проще. В AES и многих других шифрах есть аналоги функции `transpose`, хотя они обычно выглядят более сложно, чем просто перестановка битов.

Но какую роль выполняет `shuffle`, и почему `permute` и `transpose` недостаточно? В ранней версии задания `shuffle` действительно не было, и раунды выглядели как `block = shuffle(transpose(block), p)`. Но эта схема уязвима к [сдвиговой атаке](https://en.wikipedia.org/wiki/Slide_attack), причём независимо от количества раундов. Следите за руками:

Переберём `p[0]`. Обозначим за `r(block)` применение одного раунда к блоку.

Возьмём теперь блок `a = [0] * 8` и блок `r(a) = [p[0]] * 8`. Второй получается из первого вычислением одного раунда. Теперь применим к обоим из блоков функцию дешифровки, состоящая из `k` раундов. В результате `a` перейдёт в `r(r(...r(a)...))`, где `r` применяется `k` раз, а `r(a)` — в `a`, к которому применили `k + 1` раз по `r`. Легко проверить, что второй блок *всё ещё* получается из первого применением одного раунда, несмотря на то, что оба блока оказались зашифрованы каким-то сложным образом. Прогоняя эту пару блоков через шифрование ещё и ещё, мы получаем всё больше различных пар `(s, r(s))`.

Но это очень похоже на изначальную задачу, только с одним раундом вместо `k`! Мы больше не можем (де)шифровать конкретные данные на ровно один раунд, но у нас есть огромный набор пар `(plaintext, ciphertext)`. Каждая из этих пар позволит нам восстановить по 8 случайных байт (в среднем чуть меньше) перестановки `p`. Генерируем новые пары, пока в `p` есть неизвестные элементы и не было обнаружено противоречий, и задача решена.

Код на Python, демонстрирующий эту атаку, лежит в файле [slide.py](slide.py).

Операции, выглядящие достаточно хорошим перемешиванием по отдельности, могут сыграть злую шутку в комбинации. Если `shuffle` в этой криптосистеме заменить на некоторые более простые операции, например, реверс 8-байтного блока, задание решается ещё проще.

Чтобы инвалидировать такое решение (что не так важно для Жужелицы I, но очень важно для Жужелицы II, которая решается сильно сложнее, чем если бы слайд-атака работала), мы разнообразили раунды, запуская `permute` с разными перестановками на каждом раунде. Помимо этого были испробованы менее инвазивные методы, а именно замена `transpose` в некоторых раундах на *повороты* матриц. Но вот дела: повороты на разных раундах друг друга скомпенсировали, и в итоге проблема никуда не ушла. Подбирать рабочую комбинацию поворотов на глаз мы не рискнули и решили вместо этого вставить более сложную функцию `permute`.
