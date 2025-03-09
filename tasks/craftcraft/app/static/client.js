const CURSOR_SLOT = 0;
const FIRST_CRAFTING_SLOT = 1;
const FIRST_INVENTORY_SLOT = 10;
const STACK_SIZE = 64;
const N_SLOTS = 46;

const cursor = document.querySelector(".cursor");
const tooltip = document.querySelector(".tooltip");
const craftingOutput = document.querySelector(".crafting-output");
const advancements = document.querySelector(".advancements");

const slotNodes = [];
for (const slotNode of document.querySelectorAll("[data-slot]")) {
    slotNodes[+slotNode.getAttribute("data-slot")] = slotNode;
}

let realSlots = [];
for (let i = 0; i < N_SLOTS; i++) {
    realSlots.push(null);
}
let realCraftingOutput = null;

let nSpreadingSlots = 0;
let isSpreadingFull = false;
let spreadSlots = [];
for (let i = 0; i < N_SLOTS; i++) {
    spreadSlots.push(false);
}

let currentShownRecipe = null;

document.addEventListener("mousemove", (e) => {
    cursor.style.left = `${e.clientX}px`;
    cursor.style.top = `${e.clientY}px`;
});

const ws = new WebSocket("ws");

ws.addEventListener("message", (e) => {
    const request = JSON.parse(e.data);

    if (request.cmd === "slots") {
        realSlots = request.slots;
        realCraftingOutput = request.craft_output;
        renderSlots();
    } else if (request.cmd === "advancement") {
        showAchievement(request.title, request.icon);
    } else if (request.cmd === "trial") {
        document.querySelector(".trial").style.display = "";
    } else if (request.cmd === "reset") {
        document.querySelector(".trial").style.display = "none";
    }
});

document.querySelector(".trial a").addEventListener("click", () => {
    ws.send(JSON.stringify({
        cmd: "reset",
    }));
});

function getVirtualSlots() {
    if (nSpreadingSlots <= 1) {
        return realSlots;
    }

    let virtualSlots = [...realSlots];

    const amount = isSpreadingFull ? Math.floor(realSlots[CURSOR_SLOT].amount / nSpreadingSlots) : 1;

    let cursorAmount = realSlots[CURSOR_SLOT].amount;
    virtualSlots.forEach((slot, i) => {
        if (!spreadSlots[i]) {
            return;
        }
        let realAmount = slot?.amount ?? 0;
        let actualAmount = Math.min(amount, STACK_SIZE - realAmount);
        cursorAmount -= actualAmount;
        virtualSlots[i] = {
            item: realSlots[CURSOR_SLOT].item,
            amount: realAmount + actualAmount,
            isOverflowing: realAmount + amount > STACK_SIZE,
            isVirtual: true,
        };
    });
    if (cursorAmount === 0) {
        virtualSlots[CURSOR_SLOT] = null;
    } else {
        virtualSlots[CURSOR_SLOT] = {
            item: realSlots[CURSOR_SLOT].item,
            amount: cursorAmount,
        };
    }
    return virtualSlots;
}

function renderSlots() {
    getVirtualSlots().forEach((slot, i) => {
        let j = i - FIRST_CRAFTING_SLOT;
        renderItem(
            slotNodes[i],
            currentShownRecipe !== null && 0 <= j && j < 9
                ? (
                    currentShownRecipe.inputs[j] === null ? null : {
                        item: currentShownRecipe.inputs[j],
                        amount: 1,
                        isVirtual: true,
                    }
                )
                : slot,
        );
    });
    renderItem(
        craftingOutput,
        currentShownRecipe !== null
            ? {
                ...currentShownRecipe.output,
                isVirtual: true,
            }
            : realCraftingOutput,
    );
}

function renderItem(slotNode, slot) {
    slotNode.innerHTML = "";
    slotNode.classList.toggle("item-cell-virtual", (slot && slot.isVirtual) ?? false);
    if (slot === null) {
        return;
    }
    const itemNode = document.createElement("div");
    itemNode.className = "item";
    itemNode.innerHTML = `<img src="/static/items/${slot.item}.webp">`;
    itemNode.setAttribute("data-item", slot.item);
    if (slot.amount !== 1) {
        itemNode.setAttribute("data-amount", slot.amount.toString());
    }
    itemNode.classList.toggle("item-overflowing", slot.isOverflowing ?? false);
    slotNode.appendChild(itemNode);
}

function showAchievement(title, icon) {
    const advancement = document.createElement("div");
    advancement.className = "advancement";
    advancement.innerHTML = `
        <img class="advancement-icon" src="/static/items/${icon}.webp">
        <div class="advancement-body">
            <h2 class="advancement-header">Advancement Made!</h2>
            <h2 class="advancement-text">${title}</h2>
        </div>
    `;
    advancements.appendChild(advancement);
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            advancement.classList.add("advancement-visible");
        });
    });
    setTimeout(() => {
        advancement.classList.remove("advancement-visible");
    }, 9500);
    setTimeout(() => {
        advancement.remove();
    }, 10000);
}

for (const itemNode of document.querySelectorAll(".environment-menu .item")) {
    const item = itemNode.getAttribute("data-item");
    itemNode.addEventListener("click", () => {
        ws.send(JSON.stringify({
            cmd: "pick",
            item,
        }));
    });
}

for (const itemCellNode of document.querySelectorAll(".crafting-menu .item-cell[data-slot]")) {
    let lastClickCursorTake = null;
    const slot = +itemCellNode.getAttribute("data-slot");
    itemCellNode.addEventListener("mousedown", (e) => {
        if (e.button !== 0 && e.button !== 2) {
            return;
        }
        if (e.button === 0) {
            if (e.detail === 2) {
                // Double-click. Don't use `realSlots[CURSOR_SLOT]` here, as the server might not
                // have caught up with the last update yet
                if (lastClickCursorTake === null) {
                    return;
                }
                let amountLeft = STACK_SIZE - lastClickCursorTake.amount;
                for (let slot = FIRST_CRAFTING_SLOT; amountLeft > 0 && slot < N_SLOTS; slot++) {
                    if (realSlots[slot]?.item === lastClickCursorTake.item) {
                        amountLeft -= realSlots[slot].amount;
                        ws.send(JSON.stringify({
                            cmd: "move",
                            from: slot,
                            to: CURSOR_SLOT,
                            amount: realSlots[slot].amount,
                        }));
                    }
                }
                return;
            }
            if (realSlots[CURSOR_SLOT] === null) {
                lastClickCursorTake = realSlots[slot];
            } else {
                lastClickCursorTake = null;
            }
        }
        if (e.button === 0 && e.shiftKey) {
            if (realSlots[slot] === null) {
                return;
            }
            const targetSlots = [];
            if (slot < FIRST_INVENTORY_SLOT) {
                for (let targetSlot = N_SLOTS - 1; targetSlot >= FIRST_INVENTORY_SLOT; targetSlot--) {
                    targetSlots.push(targetSlot);
                }
            } else {
                for (let targetSlot = FIRST_CRAFTING_SLOT; targetSlot < FIRST_INVENTORY_SLOT; targetSlot++) {
                    targetSlots.push(targetSlot);
                }
            }
            const firstPriority = [], secondPriority = [];
            for (const targetSlot of targetSlots) {
                if (realSlots[targetSlot] === null) {
                    secondPriority.push(targetSlot);
                } else if (realSlots[targetSlot].item === realSlots[slot].item) {
                    firstPriority.push(targetSlot);
                }
            }
            let amount = realSlots[slot].amount;
            for (const targetSlot of [...firstPriority, ...secondPriority]) {
                if (amount === 0) {
                    break;
                }
                ws.send(JSON.stringify({
                    cmd: "move",
                    from: slot,
                    to: targetSlot,
                    amount: amount,
                }));
            }
            return;
        }
        if (realSlots[CURSOR_SLOT] === null) {
            if (e.button === 0) {
                ws.send(JSON.stringify({
                    cmd: "move",
                    from: slot,
                    to: CURSOR_SLOT,
                    amount: STACK_SIZE,
                }));
            } else if (realSlots[slot] !== null) {
                ws.send(JSON.stringify({
                    cmd: "move",
                    from: slot,
                    to: CURSOR_SLOT,
                    amount: Math.ceil(realSlots[slot].amount / 2),
                }));
            }
        } else {
            if (realSlots[slot] === null || realSlots[slot].item === realSlots[CURSOR_SLOT].item) {
                nSpreadingSlots = 1;
                isSpreadingFull = e.button === 0;
                spreadSlots[slot] = true;
                renderSlots();
            } else {
                ws.send(JSON.stringify({
                    cmd: "move",
                    from: CURSOR_SLOT,
                    to: slot,
                    amount: STACK_SIZE,
                }));
            }
        }
    });
    itemCellNode.addEventListener("mouseenter", () => {
        if (
            nSpreadingSlots > 0
            && realSlots[CURSOR_SLOT].amount > nSpreadingSlots
            && !spreadSlots[slot]
            && (realSlots[slot] === null || realSlots[slot].item === realSlots[CURSOR_SLOT].item)
        ) {
            spreadSlots[slot] = true;
            nSpreadingSlots++;
            renderSlots();
        }
    });
    itemCellNode.addEventListener("contextmenu", (e) => {
        e.preventDefault();
    });
}

document.body.addEventListener("mouseup", () => {
    if (nSpreadingSlots > 0) {
        const slotCount = spreadSlots.reduce((a, b) => a + b, 0);
        const amount = isSpreadingFull ? Math.floor(realSlots[CURSOR_SLOT].amount / slotCount) : 1;

        realSlots = getVirtualSlots();

        nSpreadingSlots = 0;
        spreadSlots.forEach((isSpread, slot) => {
            if (isSpread) {
                ws.send(JSON.stringify({
                    cmd: "move",
                    from: CURSOR_SLOT,
                    to: slot,
                    amount,
                }));
            }
            spreadSlots[slot] = false;
        });

        renderSlots();
    }
});

craftingOutput.addEventListener("mousedown", (e) => {
    ws.send(JSON.stringify({
        cmd: "craft",
        full: e.shiftKey,
    }));
});

{
    const itemCellNode = document.querySelector(".trash-section .item-cell");
    itemCellNode.addEventListener("click", () => {
        ws.send(JSON.stringify({
            cmd: "drop",
            full: true,
        }));
    });
    itemCellNode.addEventListener("contextmenu", (e) => {
        e.preventDefault();
        ws.send(JSON.stringify({
            cmd: "drop",
            full: false,
        }));
    });
}

(async () => {
    const recipesNode = document.querySelector(".recipes");

    for (const recipe of await (await fetch("/static/recipes.json")).json()) {
        const itemCellNode = document.createElement("div");
        itemCellNode.className = "item-cell";
        renderItem(itemCellNode, {
            item: recipe.output.item,
            amount: 1,
        });
        recipesNode.appendChild(itemCellNode);
        registerItemCell(itemCellNode);
        itemCellNode.addEventListener("mouseenter", () => {
            currentShownRecipe = recipe;
            renderSlots();
        });
        itemCellNode.addEventListener("mouseleave", () => {
            currentShownRecipe = null;
            renderSlots();
        });
    }
})();

function registerItemCell(itemCellNode) {
    itemCellNode.addEventListener("mouseenter", () => {
        const itemNode = itemCellNode.querySelector(".item");
        if (itemNode) {
            tooltip.style.display = "";
            tooltip.textContent = toText(itemNode.getAttribute("data-item"));
        }
    });

    itemCellNode.addEventListener("mouseleave", () => {
        tooltip.style.display = "none";
    });
}

for (const itemCellNode of document.querySelectorAll(".item-cell")) {
    registerItemCell(itemCellNode);
}

function toText(s) {
    return s.split("_").map((word) => {
        if (word === "with" || word === "of" || word === "and") {
            return word;
        } else {
            return word[0].toUpperCase() + word.slice(1);
        }
    }).join(" ");
}

setInterval(() => {
    ws.send(JSON.stringify({
        cmd: "ping",
    }));
}, 1000);
