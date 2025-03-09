from collections import defaultdict
from graphlib import TopologicalSorter
import json
import math
from websocket import create_connection


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


# obligations = defaultdict(int)
# obligations["dragon_egg"] = 1

# for item in order[::-1]:
#     if item not in recipe_for_item:
#         # Элемент из окружения
#         continue

#     recipe = recipe_for_item[item]
#     crafts_needed = math.ceil(obligations[item] / recipe["output"]["amount"])
#     for input in recipe["inputs"]:
#         if input is not None:
#             obligations[input] += crafts_needed

# for item in order:
#     print(item, obligations[item])


ws = create_connection("ws://127.0.0.1:3001/mj2i07cv607pi6j0/ws")
# ws = create_connection("wss://craftcraft.q.2025.ugractf.ru/mj2i07cv607pi6j0/ws")

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
            return slot, slots[slot]["amount"]
    assert False, f"No slots with {item} found"


receive_slots()

while True:
    # Посмотрим, что есть в инвентаре
    inventory = defaultdict(int)
    for slot in slots:
        if slot is not None:
            inventory[slot["item"]] += slot["amount"]

    if "dragon_egg" in inventory:
        break

    obligations = defaultdict(int)
    obligations["dragon_egg"] = 1

    for item in order[::-1]:
        unsatisfied_obligations = obligations[item] - inventory[item]
        if unsatisfied_obligations <= 0:
            continue

        recipe = recipe_for_item[item]

        # Посмотрим, хватит ли ресурсов на нужное число крафтов
        counts_needed = defaultdict(int)
        for input_item in recipe["inputs"]:
            if input_item is not None:
                counts_needed[input_item] += 1

        # Крафтим сколько нужно, но не больше 16 раз
        craft_count = min(16, math.ceil(unsatisfied_obligations / recipe["output"]["amount"]))

        if all(
            input_item not in recipe_for_item or inventory[input_item] >= amount * craft_count
            for input_item, amount in counts_needed.items()
        ):
            # Если хватает, крафтим как раньше

            # Заполняем слоты верстака
            for i, input_item in enumerate(recipe["inputs"]):
                if input_item is None:
                    continue

                crafting_table_slot = 1 + i
                amount = craft_count

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

            # Крафтим и позволяем серверу автоматически перенести результат в инвентарь
            send({
                "cmd": "craft",
                "full": True,
            })
            break

        # Не хватает -- пробрасываем требования в зависимости
        for input_item, amount in counts_needed.items():
            obligations[input_item] += amount * craft_count
