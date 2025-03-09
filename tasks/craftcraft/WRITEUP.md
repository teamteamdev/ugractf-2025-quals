# CraftCraft: Write-up

Нам доступна игра, похожая на Minecraft, но единственная доступная из игры механика — крафтинг:

![game.png](writeup/game.png)

Осмотримся. Есть пять базовых элементов, которых доступно бесконечное количество. На них можно кликнуть и взять в курсор. После этого можно либо их выбросить, перетащив в _Trash bin_, либо поставить в слот в инвентаре или верстаке. Работает достаточно много функциональности обычного Minecraft: клики правой кнопкой мыши, двойные клики, клики с зажатым Shift и распределение по нескольким слотам через удерживание кнопки мыши работают как обычно.

Но вот рецепты отличаются от обычного Minecraft очень сильно: базовые рецепты типа кроватей и очей Края работают так же, но добавлено много весёлых крафтов и айтемов, которых в нормальной игре нет.

В условии написано:

> Мне одно яйцо дракона, пожалуйста.

Рецепт для яйца дракона действительно есть: для него нужны 8 кроватей и дракон. Для дракона нужна лава и 8 зажжённых порталов, для зажжённого портала нужен пустой портал и око, для ока нужен жемчуг, для жемчуга пиглины, для пиглинов Pigstep и свиньи, для свиней загон с картошкой, для картошки зомби и алмазный меч… В общем, цепочка длиннющая, и хотелось бы заранее понимать, сколько чего надо накрафтить.


## Анализ

К счастью, в архиве приложен JSON с рецептами. Рецепты упорядочены… по алфавиту; хотелось бы для удобства переупорядочить их в порядке, в котором они понадобятся для крафта. Это называется топологической сортировкой, и в Python она [встроена](https://docs.python.org/3/library/graphlib.html):

```python
from collections import defaultdict
from graphlib import TopologicalSorter
import json


with open("app/static/recipes.json") as f:
    recipes = json.load(f)

graph = defaultdict(list)
recipe_for_item = {}

for recipe in recipes:
    for input in recipe["inputs"]:
        if input is not None:
            graph[recipe["output"]["item"]].append(input)
    recipe_for_item[recipe["output"]["item"]] = recipe

order = list(TopologicalSorter(graph).static_order())

for item in order:
    print(item)
```

```
log
water
lava
dirt
sand
coal
planks
cobblestone
obsidian
...
eye_of_ender
wool
portal_frame
bed
portal_frame_with_eye
dragon
dragon_egg
```

Теперь посчитаем, сколько ресурсов нужно для того, чтобы скрафтить одно яйцо дракона:

```python
obligations = defaultdict(int)
obligations["dragon_egg"] = 1

for item in order[::-1]:
    if item not in recipe_for_item:
        # Элемент из окружения
        continue

    recipe = recipe_for_item[item]
    crafts_needed = math.ceil(obligations[item] / recipe["output"]["amount"])
    for input in recipe["inputs"]:
        if input is not None:
            obligations[input] += crafts_needed

for item in order:
    print(item, obligations[item])
```

```
log 4817
water 580
lava 581
dirt 99
sand 376
coal 245
planks 15346
cobblestone 3387
obsidian 156
...
eye_of_ender 11
wool 24
portal_frame 8
bed 8
portal_frame_with_eye 8
dragon 1
dragon_egg 1
```

Ой, много. На то, чтобы за один раз накрафтить `15346` досок, не хватит даже места в инвентаре.


## Базовая идея метода

Получается, крафтить обязательно нужно по чуть-чуть, причём стараться не забить инвентарь. Хочется выбрать такой порядок крафтов, чтобы за раз добавлялось мало элементов, но при этом крафтились самые сложные элементы, которые на текущий момент возможно скрафтить — это нужно для того, чтобы инвентарь меньше забивался, потому что сложные предметы занимают меньше места, чем требуемые на их крафт ресурсы.

Один из вариантов этого достичь — написать примерно следующий цикл (это псевдокод):

```python
goal = "dragon_egg"
while not can_craft(goal):
    goal = find_missing_dependency(goal)
craft(goal)
```

Так мы на начальных итерациях будем подниматься по графу крафтов до простых элементов и стремиться крафтить именно их. Например, начиная с момента, когда мы спустимся до забора (`fence`), поведение при итеративном повторе этого алгоритма будет следующим:

1. `fence` → `planks` → `log` — достаём `log` из окружения
2. `fence` → `planks` — крафтим `planks`
3. `fence` → `stick` → `planks` → `log` — достаём `log` из окружения
4. `fence` → `stick` → `planks` — крафтим `planks`
5. `fence` → `stick` — крафтим `stick`
6. `fence` — крафтим `fence`

Этот алгоритм соответствует интуитивному пониманию того, как мы крафтили бы такое руками.


## Коммуникация с сервером

Чтобы узнать протокол общения с сервером, можно либо прочитать приложенный в архиве файл [server.py](app/server.py), либо веб-клиент [client.js](app/static/client.js). Первое сделать проще, и оттуда вытекает, что сервер поддерживает следующие операции, которые нужно отправлять в веб-сокет:

- `{"cmd": "pick", "item": "..."}` — берёт элемент из окружения в курсор
- `{"cmd": "move", "from": ..., "to": ..., "amount": ...}` — перемещает сколько-то элементов из одного слота в другой
- `{"cmd": "drop", "full": ...}` — перемещает либо все, либо один элемент из курсора в мусор
- `{"cmd": "craft", "full": ...}` — крафтит либо все элементы в инвертарь, либо один элемент в курсор

При этом у курсора, верстака и инвентаря сквозная нумерация слотов. В ответ на каждое из сообщений сервер присылает новое полное состояние игры, включающее в себя список и количество элементов в каждом слоте.

Напишем вспомогательные функции:

```python
def receive_slots():
    global slots
    while (message := json.loads(ws.recv()))["cmd"] == "advancement":
        pass
    assert message["cmd"] == "slots"
    slots = message["slots"]

def send(message):
    ws.send(json.dumps(message))
    receive_slots()

def get_empty_inventory_slot():
    for slot in range(10, 46):
        if slots[slot] is None:
            return slot
    assert False, "No empty slots found"

def get_inventory_slot_with_item(item):
    for slot in range(10, 46):
        if slots[slot] is not None and slots[slot]["item"] == item:
            return slot
    assert False, f"No slots with {item} found"
```

Чтобы не тратить время, запустим код на локальном сервере:

```python
ws = create_connection("ws://127.0.0.1:3001/mj2i07cv607pi6j0/ws")
receive_slots()

while True:
    # Посмотрим, что есть в инвентаре
    inventory = defaultdict(int)
    for slot in slots:
        if slot is not None:
            inventory[slot["item"]] += slot["amount"]

    goal = "dragon_egg"

    while True:
        recipe = recipe_for_item.get(goal)

        if recipe is None:
            # Это элемент из окружения, его можно получить сразу в количестве 64
            send({
                "cmd": "pick",
                "item": goal,
            })

            # ...и переместить в пустой слот
            target_slot = get_empty_inventory_slot()
            send({
                "cmd": "move",
                "from": 0,
                "to": target_slot,
                "amount": 64,
            })
            break
        else:
            # Посмотрим, хватит ли ресурсов на один крафт
            counts_needed = defaultdict(int)
            for input_item in recipe["inputs"]:
                if input_item is not None:
                    counts_needed[input_item] += 1

            for input_item, amount in counts_needed.items():
                if inventory[input_item] < amount:
                    # Не хватает — требуем накрафтить зависимость
                    goal = input_item
                    break
            else:
                # Хватает — идём крафтить

                # Заполняем слоты верстака
                for i, input_item in enumerate(recipe["inputs"]):
                    if input_item is None:
                        continue
                    crafting_table_slot = 1 + i
                    inventory_slot = get_inventory_slot_with_item(input_item)
                    send({
                        "cmd": "move",
                        "from": inventory_slot,
                        "to": crafting_table_slot,
                        "amount": 1,
                    })

                # Крафтим и позволяем серверу автоматически перенести результат в инвентарь
                send({
                    "cmd": "craft",
                    "full": True,
                })
                break
```

И не зря: мы упёрлись в какой-то лимит.

![times_up.png](writeup/times_up.png)


## Оптимизация

По коду сервера понимаем, что дело не во времени, а в том, что нам разрешено сделать всего `30000` операций. Придётся что-то оптимизировать: видимо, крафтить нужно не по одному элементу, а сразу несколько. Но сразу скрафтить *всё* тоже нельзя — не хватит места... Придётся искать компромисс: попробуем крафтить несколько элементов, но с ограничением. Добавим:

```python
goal = "dragon_egg"
goal_count = 1

...

while True:
    ...
    else:
        ...

        # Крафтим сколько нужно, но не больше LIMIT раз
        craft_count = min(LIMIT, math.ceil(goal_count / recipe["output"]["amount"]))

        for input_item, amount in counts_needed.items():
            if inventory[input_item] < amount * craft_count:
                # Не хватает — требуем накрафтить зависимость, чтобы хватило впритык
                goal = input_item
                goal_count = amount * craft_count - inventory[input_item]
                break
        else:
            # Хватает — идём крафтить

            # Заполняем слоты верстака
            for i, input_item in enumerate(recipe["inputs"]):
                if input_item is None:
                    continue
                crafting_table_slot = 1 + i
                amount = craft_count

                # Перетаскиваем из слотов, сколько можем
                while amount > 0:
                    inventory_slot, count_in_slot = get_inventory_slot_with_item(input_item)
                    send({
                        "cmd": "move",
                        "from": inventory_slot,
                        "to": crafting_table_slot,
                        "amount": min(count_in_slot, amount),
                    })
                    amount -= count_in_slot

            # Крафтим и позволяем серверу автоматически перенести результат в инвентарь
            send({
                "cmd": "craft",
                "full": True,
            })
            break
```

При `LIMIT = 1` поведение эквивалентно текущему. Поиграемся с `LIMIT` и увидим, что при `LIMIT = 16` и слотов хватает, и операций хватает. Осталось запустить [решение](solve.py) на настоящем сервере и получить ачивку:

![solved.png](writeup/solved.png)

Флаг: **ugra_how_did_we_get_here_zs18mtvhkk8v**


## Необязательные оптимизации

У этой задачи есть чуть более оптимальное решение. Дело в том, что сейчас мы не совсем эффективно обрабатываем рецепты майнинга. Например, для получения алмазной руды нужна карта и лазурит, а для получения лазурита тоже нужна карта. Таким образом, в зависимостях алмазной руды присутствует разветвление, которое в обоих путях приводит к карте. Поскольку наш алгоритм всегда спускается только по одному пути, мы увидим только одну карту и накрафтим только одну карту, хотя нам гарантированно понадобится вторая.

Это не критично для решения задания, но если хочется приблизиться к оптимуму, можно подумать над алгоритмом, который позволит спускаться по всем путям параллельно. Для этого можно воспользоваться методом, похожим на код с `obligations` из начала разбора. Будем поддерживать в `obligations` количество элементов, которые нам нужны, включая уже готовые, следующим образом:

```python
obligations = defaultdict(int)
obligations["dragon_egg"] = 1

for item in order[::-1]:
    unsatisfied_obligations = obligations[item] - inventory[item]
    if unsatisfied_obligations <= 0:
        continue

    ...

    craft_count = min(LIMIT, math.ceil(unsatisfied_obligations / recipe_for_item[item]["output"]["amount"]))

    if all(
        inventory[input_item] >= amount * craft_count
        for input_item, amount in counts_needed.items()
    ):
        # Если хватает, крафтим как раньше
        break

    # Не хватает — пробрасываем требования в зависимости
    for input_item, amount in counts_needed.items():
        obligations[input_item] += amount * craft_count
```

По сути мы здесь крафтим последний элемент, который можно скрафтить и который при этом *нужно* скрафтить, где понятие «нужно» искусственно ограничено, чтобы не крафтить настолько много элементов, что они заполнят все слоты.

Но так нам всё равно перестаёт хватать слотов, поэтому сделаем финт ушами. Сейчас у нас практически всегда есть пять слотов в инвентаре, хранящие «мусор» из окружения, который мы в любой момент и так можем получить достаточно легко. Перепишем код так, чтобы каждый раз доставать элементы из окружения напрямую, а не через слоты:

```python
if input_item in recipe_for_item:
    # Перетаскиваем из слотов сколько можем
    while amount > 0:
        inventory_slot, count_in_slot = get_inventory_slot_with_item(input_item)
        send({
            "cmd": "move",
            "from": inventory_slot,
            "to": crafting_table_slot,
            "amount": min(count_in_slot, amount),
        })
        amount -= count_in_slot
else:
    # Пополняем из окружения
    send({
        "cmd": "pick",
        "item": input_item,
    })
    send({
        "cmd": "move",
        "from": 0,
        "to": crafting_table_slot,
        "amount": amount,
    })
    send({
        "cmd": "drop",
        "full": True,
    })
```

Несмотря на неоптимальность этого перемещения, тот факт, что теперь мы отслеживаем сразу все пути зависимостей, ускоряет [это решение](solve2.py) в 2 раза относительно описанного выше.


## Альтернативные подходы

Если правильно написать какую-то оптимизацию не получилось, но ваше решение в целом всё ещё частично работало, просто ему не хватало слотов, то можно было решать задание полуавтоматически. Идеи разной степени полезности:

- Поскольку некоторые рецепты выдают больше 1 элемента, в результате часто остаётся немного мусора, который только забивает слоты. Этот мусор можно чистить, чтобы слоты освободить.

- Бывают элементы, которые понадобятся когда-то в будущем, но их достаточно дёшево если что перекрафтить. Если места не хватает, можно их просто выбросить.

- Можно попросить программу накрафтить не сразу яйцо дракона, а какой-нибудь промежуточный элемент, после чего очистить весь инвентарь, кроме этого элемента. Например, для этой цели хорошо подходили зачарованные книги, которые тупыми решениями крафтились плохо, но на крафт по одиночке места хватало.

- При решении руками можно написать хоткеи для автокрафта часто нужных ресурсов прям в консоли браузера.


## Интересные факты

Большинство спрайтов ввиду лицензионных проблем взяты из [MineClonia](https://codeberg.org/mineclonia/mineclonia/) (конкретика в [COPYING](COPYING)) вместо Minecraft. Парочка недостававших спрайтов была нарисована руками. Разбор писался под Pigstep. Во время подготовки спрайтов обнаружилось, что глаза пиглина — это две мелкие белые точки, а похожие на глаза линии в центре лица — это ноздри (автору до этого казалось, что это глаза, а пигнлины носят шапки-ушанки).
