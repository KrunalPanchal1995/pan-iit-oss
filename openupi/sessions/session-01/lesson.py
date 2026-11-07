"""Session 1 (Level 1): the cast of a payment and the message flow. Money moves between ledgers.

Run:  python start.py 1

A simplified teaching picture of how a digital payment works. Real systems differ in many details.
"""
# %% [markdown]
# # Session 1: who is in a payment, and what do they say to each other?
# **A. Real-world problem.** You scan a code at a shop, type a PIN, and a second later both
# phones say "success". No coins moved. What actually happened, and who talked to whom?
#
# **Plan.** (1) meet the cast, (2) write the messages as a list, (3) follow the numbers in
# three ledgers, (4) check that no money appears or vanishes on the way, (5) draw the
# sequence diagram.
#
# General education about how such systems are organised; not advice about any real account or app.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the cast
# * **Payer app** and **payee app**: windows on your phones. They hold no money. They only send
#   and show messages.
# * **Payer bank** and **payee bank**: keep the *ledgers*, lists of numbers saying how much each
#   customer is owed by the bank.
# * **Switch** (a shared network in the middle): passes messages between apps and banks and keeps
#   track of a payment while it is on its way. In this repo it is a toy, not any real network.
#
# The key idea: **money moves as changes of numbers in ledgers, not as coins.**

# %%
ACTORS = ["Payer app", "Switch", "Payer bank", "Payee bank", "Payee app"]

# (from, to, what is said). Message k is step k of the flow.
MESSAGES = [
    ("Payer app", "Switch", "pay Rs X to payee (id T1)"),
    ("Switch", "Payer bank", "can you debit Rs X?"),
    ("Payer bank", "Switch", "debited (payer ledger -X)"),
    ("Switch", "Payee bank", "credit Rs X"),
    ("Payee bank", "Switch", "credited (payee ledger +X)"),
    ("Switch", "Payee app", "success (and to payer app)"),
]


# %% [markdown]
# ## Step 2: follow the numbers
# Between step 3 and step 5 the money has left the payer's ledger but has not yet reached the
# payee's ledger. We count it in an **in-flight** box at the switch, so every rupee always has
# exactly one home. `flow_states` returns the three numbers after each step.

# %%
def flow_states(payer, payee, amount):
    """Balances after step 0 (before), 1, ... 6. Each is a dict payer / in_flight / payee (rupees).

    If amount is more than the payer has, the payer bank refuses at step 3 and nothing moves."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    declined = amount > payer
    states = []
    for step in range(7):
        s = {"payer": payer, "in_flight": 0, "payee": payee}
        if not declined and step >= 3:
            s["payer"], s["in_flight"] = payer - amount, amount
        if not declined and step >= 5:
            s["in_flight"], s["payee"] = 0, payee + amount
        states.append(s)
    return states


def total(state):
    return state["payer"] + state["in_flight"] + state["payee"]


def conserved(states):
    """True when the total is the same at every step."""
    return len({total(s) for s in states}) == 1


# %% [markdown]
# ## Step 3: draw the sequence diagram
# Time runs downwards. Each arrow is one message. Under each arrow we print the three numbers.

# %%
def draw_sequence(states, amount, path):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6.2))
    xs = {a: i for i, a in enumerate(ACTORS)}
    for a, x in xs.items():
        ax.plot([x, x], [0, -6.6], color="#9aa5b1", lw=1, zorder=0)
        ax.text(x, 0.25, a, ha="center", va="bottom", fontsize=9, weight="bold")
    for k, (src, dst, text) in enumerate(MESSAGES, start=1):
        y = -k
        ax.annotate("", xy=(xs[dst], y), xytext=(xs[src], y), arrowprops=dict(arrowstyle="->", color="#2a6fdb", lw=1.5))
        ax.text((xs[src] + xs[dst]) / 2, y + 0.1, f"{k}. {text.replace('X', str(amount))}", ha="center", va="bottom", fontsize=8)
        s = states[k]
        ax.text(4.55, y, f"payer {s['payer']}  in flight {s['in_flight']}  payee {s['payee']}", fontsize=7, va="center", color="#444")
    ax.text(4.55, 0.25, "ledger numbers (rupees)", fontsize=8, weight="bold", va="bottom")
    ax.set_xlim(-0.6, 6.6)
    ax.set_ylim(-6.8, 0.9)
    ax.axis("off")
    ax.set_title("A payment as messages (time runs downwards)")
    fig.tight_layout()
    fig.savefig(path, dpi=120)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    states = flow_states(1000, 400, 250)
    print("step  payer  in_flight  payee  total")
    for k, s in enumerate(states):
        print(f"{k:4d} {s['payer']:6d} {s['in_flight']:10d} {s['payee']:6d} {total(s):6d}")
    print("money conserved at every step:", conserved(states))
    dec = flow_states(1000, 400, 1200)
    print("declined (1200 > 1000): final", dec[-1], "conserved:", conserved(dec))
    draw_sequence(states, 250, OUT / "sequence_diagram.png")

    fig, ax = plt.subplots(figsize=(6.5, 4))
    steps = np.arange(7)
    p = [s["payer"] for s in states]
    f = [s["in_flight"] for s in states]
    q = [s["payee"] for s in states]
    ax.bar(steps, p, label="payer ledger", color="#2a6fdb")
    ax.bar(steps, f, bottom=p, label="in flight at switch", color="#e9a23b")
    ax.bar(steps, q, bottom=np.array(p) + np.array(f), label="payee ledger", color="#2a9d8f")
    ax.set_xlabel("step in the flow (0 = before)")
    ax.set_ylabel("rupees")
    ax.set_title("Money moves between ledgers; the total stays 1400")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(OUT / "ledgers_by_step.png", dpi=120)

# %% [markdown]
# ## Where this stops
# We never asked whether the payer really approved the payment, or what to do if a message is
# lost. Session 2 adds the ledger rules; Session 3 adds failures and fraud checks.
