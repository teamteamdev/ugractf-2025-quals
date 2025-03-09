from collections import defaultdict
import json
import re

with open("recipes.txt") as f:
    recipes = f.read().strip().split("\n\n")

def parse_item_with_amount(item_with_amount):
    if item_with_amount[0].isdigit():
        amount, item = item_with_amount.split(" ", 1)
        return int(amount), item
    else:
        return 1, item_with_amount

recipe_list = []

for recipe in recipes:
    output = parse_item_with_amount(re.search(r" -> (.*)", recipe)[1])
    inputs = re.sub(r" -> .*", "", recipe)
    if "+" in inputs:
        kind = "unshaped"
        inputs = [input for input in inputs.split(" + ")]
    else:
        kind = "shaped"
        inputs = [[None if cell == "air" else cell for cell in row.split("\t")] for row in inputs.split("\n")]
    recipe_list.append({
        "kind": kind,
        "inputs": inputs,
        "output": output
    })

counts = defaultdict(int)
counts["dragon_egg"] = 1

for recipe in recipe_list[::-1]:
    amount, item = recipe["output"]
    times_to_craft = (counts[item] + amount - 1) // amount
    print(item, times_to_craft)
    if recipe["kind"] == "unshaped":
        inputs = recipe["inputs"]
    else:
        inputs = sum(recipe["inputs"], [])
    for item in inputs:
        if item is None:
            continue
        counts[item] += times_to_craft

print("total crafts:", sum(counts.values()))

unshaped_recipes = {}
shaped_recipes = {}
saved_recipes = []
for recipe in recipe_list:
    if recipe["kind"] == "unshaped":
        table = recipe["inputs"][:]
        table += [None] * (9 - len(table))
        unshaped_recipes[frozenset(recipe["inputs"])] = recipe["output"]
    elif recipe["kind"] == "shaped":
        table = [None] * 9
        for y, row in enumerate(recipe["inputs"]):
            for x, item in enumerate(row):
                table[y * 3 + x] = item
        shaped_recipes[tuple([len(recipe["inputs"]), *sum(recipe["inputs"], [])])] = recipe["output"]
    amount, item = recipe["output"]
    saved_recipes.append({
        "inputs": table,
        "output": {
            "item": item,
            "amount": amount,
        },
    })

with open("app/recipes.py", "w") as f:
    print("UNSHAPED_RECIPES =", unshaped_recipes, file = f)
    print("SHAPED_RECIPES =", shaped_recipes, file = f)

saved_recipes.sort(key = lambda recipe: recipe["output"]["item"])

with open("app/static/recipes.json", "w") as f:
    json.dump(saved_recipes, f)
