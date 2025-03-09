from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass
import json
import os
from quart import Quart, send_from_directory, websocket
import traceback

if "KYZYLBORDA" in os.environ:
    from kyzylborda_lib.secrets import get_flag, validate_token
else:
    def get_flag(token: str) -> str:
        return "ugra_fake_flag"
    def validate_token(token: str) -> bool:
        return True

from recipes import UNSHAPED_RECIPES, SHAPED_RECIPES


GIFTED_ITEMS = {"log", "dirt", "sand", "water", "lava"}
CURSOR_SLOT = 0
FIRST_CRAFTING_SLOT = 1
FIRST_INVENTORY_SLOT = 10
STACK_SIZE = 64
N_SLOTS = 46
TRIAL_LIMIT = 30000


app = Quart(__name__)


@dataclass
class Advancement:
    title: str
    icon: str


with open("advancements.json") as f:
    title_to_advancement: dict[str, Advancement] = {}
    craft_to_advancement: dict[str, Advancement] = {}

    for advancement in json.load(f):
        condition = advancement["condition"]
        if not isinstance(condition, list):
            condition = [condition]

        advancement = Advancement(title = advancement["title"], icon = advancement["icon"])

        title_to_advancement[advancement.title] = advancement
        for item in condition:
            assert item not in craft_to_advancement
            craft_to_advancement[item] = advancement


@dataclass
class Slot:
    item: str
    amount: int


class State:
    def __init__(self):
        self.reset()

    @classmethod
    def load(cls, parsed) -> State:
        state = cls()
        state.slots = [
            None if slot is None else Slot(
                item = slot["item"],
                amount = slot["amount"],
            )
            for slot in parsed["slots"]
        ]
        state.advancements = set(parsed["advancements"])
        state.operations_performed = parsed["operations_performed"]
        state.craft_output = state.match_craft()
        return state

    def save(self):
        return {
            "slots": [
                None if slot is None else {
                    "item": slot.item,
                    "amount": slot.amount,
                }
                for slot in self.slots
            ],
            "advancements": list(self.advancements),
            "operations_performed": self.operations_performed,
        }

    def reset(self):
        self.slots = [None] * N_SLOTS
        self.advancements = set()
        self.operations_performed = 0
        self.craft_output = None

    def pick(self, item: str):
        if item not in GIFTED_ITEMS:
            return
        if self.slots[CURSOR_SLOT] is not None and self.slots[CURSOR_SLOT].item != item:
            return
        self.slots[CURSOR_SLOT] = Slot(
            item = item,
            amount = STACK_SIZE
        )
        self.operations_performed += 1

    def move(self, from_: int, to: int, amount: int):
        if not (0 <= from_ < N_SLOTS and 0 <= to < N_SLOTS) or from_ == to or self.slots[from_] is None:
            return

        amount = min(amount, self.slots[from_].amount)
        if amount <= 0:
            return

        need_to_update_craft_output = 0 <= from_ - FIRST_CRAFTING_SLOT < 9 or 0 <= to - FIRST_CRAFTING_SLOT < 9

        if self.slots[to] is None:
            self.slots[to] = Slot(
                item = self.slots[from_].item,
                amount = amount
            )
        elif self.slots[to].item == self.slots[from_].item:
            amount = min(amount, STACK_SIZE - self.slots[to].amount)
            self.slots[to].amount += amount
        else:
            if amount == self.slots[from_].amount:
                self.slots[from_], self.slots[to] = self.slots[to], self.slots[from_]
                self.operations_performed += 1
                if need_to_update_craft_output:
                    self.craft_output = self.match_craft()
            return

        self.slots[from_].amount -= amount
        if self.slots[from_].amount == 0:
            self.slots[from_] = None
        self.operations_performed += 1
        if need_to_update_craft_output:
            self.craft_output = self.match_craft()

    def drop(self, full: bool):
        if self.slots[CURSOR_SLOT] is None:
            return
        if full:
            self.slots[CURSOR_SLOT] = None
        else:
            self.slots[CURSOR_SLOT].amount -= 1
            if self.slots[CURSOR_SLOT].amount == 0:
                self.slots[CURSOR_SLOT] = None
        self.operations_performed += 1

    def craft(self, full: bool):
        if self.craft_output is None:
            return
        craft_output = self.craft_output

        if full:
            craft_count = min(slot.amount for slot in self.slots[FIRST_CRAFTING_SLOT:FIRST_CRAFTING_SLOT + 9] if slot is not None)
        else:
            craft_count = 1

        if full:
            first_priority = []
            second_priority = []
            for slot in range(N_SLOTS - 1, FIRST_INVENTORY_SLOT - 1, -1):
                if self.slots[slot] is None:
                    second_priority.append(slot)
                elif self.slots[slot].item == craft_output.item:
                    first_priority.append(slot)
            slots = first_priority + second_priority
        else:
            if self.slots[CURSOR_SLOT] is not None and self.slots[CURSOR_SLOT].item != craft_output.item:
                return
            slots = [CURSOR_SLOT]

        total_free_amount = 0
        for slot in slots:
            total_free_amount += STACK_SIZE - (0 if self.slots[slot] is None else self.slots[slot].amount)

        craft_count = min(craft_count, total_free_amount // craft_output.amount)
        if craft_count == 0:
            return
        craft_amount = craft_count * craft_output.amount

        for slot in slots:
            if craft_amount == 0:
                break
            free_amount = STACK_SIZE - (0 if self.slots[slot] is None else self.slots[slot].amount)
            slot_amount = min(free_amount, craft_amount)
            if self.slots[slot] is None:
                self.slots[slot] = Slot(item = craft_output.item, amount = slot_amount)
            else:
                self.slots[slot].amount += slot_amount
            craft_amount -= slot_amount

        for i in range(9):
            slot = self.slots[FIRST_CRAFTING_SLOT + i]
            if slot is not None:
                slot.amount -= craft_count
                if slot.amount == 0:
                    self.slots[FIRST_CRAFTING_SLOT + i] = None

        self.operations_performed += 1

        self.craft_output = self.match_craft()

        advancement = craft_to_advancement.get(craft_output.item)
        if advancement is not None:
            self.advancements.add(advancement.title)

    def match_craft(self) -> Optional[Slot]:
        unshaped_key = frozenset(slot.item for slot in self.slots[FIRST_CRAFTING_SLOT:FIRST_CRAFTING_SLOT + 9] if slot is not None)
        if not unshaped_key:
            return None

        output = UNSHAPED_RECIPES.get(unshaped_key)
        if output is None:
            min_x = 3
            min_y = 3
            max_x = 0
            max_y = 0
            for y in range(3):
                for x in range(3):
                    if self.slots[FIRST_CRAFTING_SLOT + y * 3 + x] is not None:
                        min_x = min(min_x, x)
                        max_x = max(max_x, x)
                        min_y = min(min_y, y)
                        max_y = max(max_y, y)

            shaped_key = [max_y - min_y + 1]
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    slot = self.slots[FIRST_CRAFTING_SLOT + y * 3 + x]
                    shaped_key.append(None if slot is None else slot.item)
            output = SHAPED_RECIPES.get(tuple(shaped_key))

        if output is None:
            return None
        else:
            return Slot(
                amount = output[0],
                item = output[1],
            )


states = defaultdict(State)

try:
    with open("/state/state.json") as f:
        for token, state in json.load(f).items():
            states[token] = State.load(state)
except FileNotFoundError:
    pass

async def sync_states():
    try:
        while True:
            with open("/state/state_tmp.json", "w") as f:
                json.dump({token: state.save() for token, state in states.items()}, f)
            os.replace("/state/state_tmp.json", "/state/state.json")
            await asyncio.sleep(10)
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)


_sync_states = asyncio.create_task(sync_states())


@app.websocket("/<token>/ws")
async def ws(token: str):
    if not validate_token(token):
        return "Invalid token", 404

    state = states[token]

    current_advancements = state.advancements - {"{flag}"}

    while True:
        new_advancements = state.advancements
        for advancement_title in new_advancements - current_advancements:
            advancement = title_to_advancement[advancement_title]
            await websocket.send(json.dumps({
                "cmd": "advancement",
                "title": get_flag(token) if advancement.title == "{flag}" else advancement.title,
                "icon": advancement.icon,
            }))
        current_advancements = set(new_advancements)

        if state.craft_output is None:
            craft_output_json = None
        else:
            craft_output_json = {
                "amount": state.craft_output.amount,
                "item": state.craft_output.item,
            }
        await websocket.send(json.dumps({
            "cmd": "slots",
            "slots": state.save()["slots"],
            "craft_output": craft_output_json,
        }))

        if state.operations_performed >= TRIAL_LIMIT:
            await websocket.send(json.dumps({
                "cmd": "trial"
            }))

        request = json.loads(await websocket.receive())

        if request["cmd"] == "reset":
            state.reset()
            await websocket.send(json.dumps({
                "cmd": "reset"
            }))

        if state.operations_performed < TRIAL_LIMIT:
            if request["cmd"] == "pick":
                item = request["item"]
                if isinstance(item, str):
                    state.pick(item)

            elif request["cmd"] == "move":
                from_ = request["from"]
                to = request["to"]
                amount = request["amount"]
                if isinstance(from_, int) and isinstance(to, int) and isinstance(amount, int):
                    state.move(from_, to, amount)

            elif request["cmd"] == "drop":
                state.drop(bool(request["full"]))

            elif request["cmd"] == "craft":
                state.craft(bool(request["full"]))


@app.route("/<token>/")
async def index(token: str):
    if not validate_token(token):
        return "Invalid token", 404

    return await send_from_directory("static", "index.html")
