# Жужелица II: Write-up

Для понимания этого разбора крайне рекомендуется прочитать [разбор задания Жужелица I](../zhuzhelitsa/WRITEUP.md).

Единственное отличие этого задания от предыдущего заключается в том, что количество раундов увеличено до трёх:

```python
block = input
block = shuffle(block, INV_SHUFFLE[2])
block = transpose(block)
block = permute(block, p_inv) # (1)
block = shuffle(block, INV_SHUFFLE[1])
block = transpose(block)
block = permute(block, p_inv)
block = shuffle(block, INV_SHUFFLE[0]) # (2)
block = transpose(block)
block = permute(block, p_inv) # (3)
output = block
```

Попробуем, как и раньше, подобрать вход так, чтобы к началу шага (1) все байты были равны некоторому фиксированному байту `x`. Тогда после шага (2) мы получаем в `i`-м байте `p_inv[255]`, если в `p_inv[x]` стоит `INV_SHUFFLE[0][i]`-й бит, и `p_inv[0]` иначе:

```python
xx = sum(
    ((p_inv[x] >> INV_SHUFFLE[0][i]) & 1) << i
    for i in range(8)
)
block = [p_inv[255] if xx & 1 else p_inv[0] for i in range(8)]
```

Дальше будет проще рассмотреть конкретный пример. Представим себе, что `xx = 0b01101000`, `p_inv[0] = 0b11101010, p_inv[255] = 0b00101100`. Тогда после шага (2):

```python
block = [
    # В i-й строке стоит p_inv[0] либо p_inv[255] согласно i-му биту в xx
    0b11101010,
    0b11101010,
    0b11101010,
    0b00101100,
    0b11101010,
    0b00101100,
    0b00101100,
    0b11101010,
]
```

а далее:

```python
output = [
    # В i-й строке:
    # - `p_inv[0]`, если в `p_inv[0]` и `p_inv[255]` i-й бит совпадает и равен 0
    # - `p_inv[255]`, если в `p_inv[0]` и `p_inv[255]` i-й бит совпадает и равен 1
    # - `p_inv[xx]`, если в `p_inv[0]` i-й бит 0, а в `p_inv[255]` -- 1
    # - `p_inv[~xx]`, если в `p_inv[0]` i-й бит 1, а в `p_inv[255]` -- 0
    p_inv[0],
    p_inv[~xx],
    p_inv[xx],
    p_inv[255],
    p_inv[0],
    p_inv[255],
    p_inv[~xx],
    p_inv[~xx],
]
```

Из этой картинки уже можно достать `p_inv[0]` или `p_inv[255]`. В самом деле: поскольку хоть какой-то бит в `p_inv[0]` и `p_inv[255]` обязан совпадать (иначе не пройдёт проверка `is_safe_permutation`), константа `p_inv[0]` или `p_inv[255]` в этом списке обязательно будет. Сделаем два запроса с разными `x`, и те позиции, байты на которых не поменялись, будут содержать `p_inv[0]` или `p_inv[255]` (что из них что — непонятно, придётся перебрать, и мы вполне можем найти только один из двух, это тоже нормально).

С `p_inv[xx]` уже проблема: `xx` сам по себе получается из `p_inv[x]`. Если бы было просто `p_inv[p_inv[x]]`, задача бы решалась — вместо перестановки `p_inv` мы бы смогли восстановить её квадрат, а затем перебрать 128 корней и найти среди них нужный. Но из-за операции `shuffle` всё далеко не так просто.

Что ж, идея с `[x] * 8` отыграла свою роль, придётся рассмотреть более сложные конфигурации входных данных. Как насчёт того, чтобы заменить часть из `x` на некий `y` и посмотреть, не добавит ли это нужной степени свободы? Выберем битовую маску `k` (для примера `k = 0b01110101`), где 0 на `INV_SHUFFLE[1][i]`-й позиции означает, что в `i`-й байт мы ставим `x`, а 1 — `y`. Так всё становится сильно интереснее: после (4) в следующем коде:

```python
block = input
block = shuffle(block, INV_SHUFFLE[2])
block = transpose(block)
block = permute(block, p_inv)
block = shuffle(block, INV_SHUFFLE[1])
block = transpose(block) # (4)
block = permute(block, p_inv)
block = shuffle(block, INV_SHUFFLE[0]) # (5)
block = transpose(block)
block = permute(block, p_inv)
output = block
```

мы получаем состояние

```python
block = [
    # В i-м столбце записано p_inv[x] или p_inv[y] в зависимости от i-го бита в k
    p_inv[x] | p_inv[y] | p_inv[y] | p_inv[y] | p_inv[x] | p_inv[y] | p_inv[x] | p_inv[y]
]
# Или, что то же самое,
block = [
    # На i-й строке записано:
    0, # если и в p_inv[x], и в p_inv[y] i-й бит равен 0
    255, # если и в p_inv[x], и в p_inv[y] i-й бит равен 1
    k, # если в p_inv[x] i-й бит равен 0, а в p_inv[y] i-й бит равен 1
    ~k, # если в p_inv[x] i-й бит равен 1, а в p_inv[y] i-й бит равен 0
]
```

которое после (5) переходит в:

```python
block = [
    # На `SHUFFLE[0][i]`-й строке записано:
    p_inv[0], # если и в p_inv[x], и в p_inv[y] i-й бит равен 0
    p_inv[255], # если и в p_inv[x], и в p_inv[y] i-й бит равен 1
    p_inv[k], # если в p_inv[x] i-й бит равен 0, а в p_inv[y] i-й бит равен 1
    p_inv[~k], # если в p_inv[x] i-й бит равен 1, а в p_inv[y] i-й бит равен 0
]
```

Пока всё более-менее понятно, хотя четыре варианта и смущают. Следующие две операции, однако, провести символьно нереально, поэтому зайдем с другой стороны. Зная `output`, какую информацию мы имеем о выхлопе (5)? Поскольку `p_inv` — перестановка, равные байты она переводит в равные, а различные — в различные, т.е. по `output` мы имеем возможность понимать, какие из столбцов битов в выхлопе (5) совпадают, а какие различаются. Даёт ли нам что-то этот оракул?

Проблема в том, что сравнение столбцов сравнивает на равенство сразу все 8 бит. Если нам, допустим, было интересно, равны ли `i`-й и `j`-й биты в `p_inv[k]`, к этому результату еще примиксится проверка на равенство битов в `p_inv[0]` и `p_inv[255]`, что рискует сильно испортить ответ.

Но не всё потеряно, ведь мы можем сравнивать не разные столбцы в одном шифротексте, а один и тот же столбец в шифротекстах для разных `k`. Так, `i`-е столбцы в `block` для `k1` и `block` для `k2` равны тогда и только тогда, когда `i`-е биты в `p_inv[k1]` и `p_inv[k2]` совпадают, а также совпадение есть в `p_inv[~k1]` и `p_inv[~k2]`. Почти идеально: теперь вместо AND из четырёх условий у нас AND из всего двух.

А можно ли ещё один из них выкинуть? Можно! `p_inv[~k]` присутствует в списке только в том случае, если есть бит, который в `p_inv[x]` установлен, а в `p_inv[y]` сброшен. Но `x` и `y` мы вольны выбирать любые, а значит, можно перебрать несколько случайных пар `x` и `y` и наткнуться на то, в которой такого бита нет. Это далеко не такое редкое событие, как кажется: случается оно с вероятностью около 10%.

Наткнувшись на такую удобную пару `(x, y)`, мы получаем возможность сравнивать `i`-е биты на равенство между `p_inv[k1]` и `p_inv[k2]` или, иными словами, считать `p_inv[k1] ^ p_inv[k2]`. В качестве `k1` можно попробовать взять `0` и `255` (напомним, что значения хотя бы одной из величин `p_inv[0]` и `p_inv[255]` нам уже известны, но мы не знаем соответствие), в качестве `k2` перебрать все остальные числа. В результате мы получим перестановку, корректную с неплохим шансом (если мы угадали соответствие и если в `p_inv[x]` и `p_inv[y]` что-то является подмножеством чего-то другого). Чтобы отбросить некорректные перестановки, можно либо обратиться напрямую к серверу, либо зашифровать с таким ключом данные, которые мы ранее отправляли на расшифровку, и проверить результат на совпадение.

Наконец, отметим, что избавляться можно не от `p_inv[~k]`, а от `p_inv[k]`: метод будет максимально похожий и увеличит вероятность успеха, а значит и скорость перебора, в два раза.

Реализацию приведённого решения можно найти в файле [solve.py](solve.py).

Флаг: **ugra_third_times_a_charm_udx4qjbyssp4**

## Постмортем

Первые несколько часов задание не решалось, поскольку сервер не принимал пару API ключа и адреса кошелька.

На текущий момент не вся наша инфраструктура поддерживает конфигурацию, в которой два задания взаимосвязаны и настраиваются одним сервисом и генератором. Технически задания Жужелица I и Жужелица II — два полностью различных задания, и лишь случайно генераторы обоих заданий заводят аккаунты на одном и том же бекенде.

Бекенд был поднят как демон Жужелицы I. Демоны имеют доступ к секретам и умеют генерировать флаги и прочие секреты по токену (в данном задании он для погружения в лор назывался «API key»), и чтобы не поднимать на демоне эндпоинт, принимающий секреты извне (ведь его случайно или специально может вызвать кто-то снаружи), демон генерировал адреса самостоятельно, используя API борды.

Генератор задания Жужелица II использовал то же самое API, но поскольку это разные задачи, у адреса было два источника истины: настройки секретов из задания Жужелица I и настройки секретов из задания Жужелица II, и хранились они в разных файлах. Чтобы аккаунты регистрировались корректно, эти настройки должны совпадать.

Адрес кошелька — это base64 URI-safe строка фиксированной длины. Соответственно, она может включать в себя символы `_` и `-`. Для генерации «фотографии» проектора картинки генерировались автоматически, а спрайты для шрифта были выдернуты руками с реальной установки Windows XP. Про `_` и `-` никто сходу не вспомнил, и убрать из генерируемых адресов `_` и `-` показалось более простой идеей, чем опять запускать реальную машину, чтобы достать два спрайта.

Догадаться о том, что пошло не так при убирании `_-` из регулярки секрета, читателю предлагается самостоятельно.
