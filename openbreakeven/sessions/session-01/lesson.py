"""Session 1 (Level 1): a lemonade stall, and where income catches up with cost.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: where does income catch up with cost?
# **A. Real-world problem.** You want to run a lemonade stall. Before you sell a single cup
# you must pay for the stall and the pitcher. After that, every cup costs a little to make and
# earns a little more when it is sold. At the start you are behind. How many cups until you
# are even? That number is the *break-even point*.
#
# *General education only: the stall is made up, and this is not financial advice.*
#
# **Plan.** (1) write the cost line, (2) write the income line, (3) find where they meet,
# (4) draw them and read the graph.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

FIXED = 60.0      # dollars paid before the first cup: stall fee 40 + pitcher and sign 20
PRICE = 2.00      # dollars received for one cup
CUP_COST = 0.50   # dollars spent making one cup (lemons, sugar, cup)


# %% [markdown]
# ## Step 1: the cost line
# Two kinds of cost. The **fixed cost** is paid once, whether you sell 0 cups or 100.
# The **variable cost** grows with every cup you make.
#
#     total cost = fixed cost + cost per cup * cups

# %%
def total_cost(cups, fixed=FIXED, cup_cost=CUP_COST):
    """Dollars spent after making `cups` cups."""
    return fixed + cup_cost * np.asarray(cups, dtype=float)


# %% [markdown]
# ## Step 2: the income line and the profit
# Income (also called revenue) is price times cups. Profit is income minus cost. While profit
# is negative you are making a loss; once it is zero or more, you have caught up.

# %%
def income(cups, price=PRICE):
    return price * np.asarray(cups, dtype=float)


def profit(cups, fixed=FIXED, price=PRICE, cup_cost=CUP_COST):
    return income(cups, price) - total_cost(cups, fixed, cup_cost)


# %% [markdown]
# ## Step 3: where the lines meet
# Each cup earns `price - cup cost` dollars towards paying off the fixed cost. So the number
# of cups needed is the fixed cost divided by what one cup earns:
#
#     break-even cups = fixed cost / (price - cup cost)
#
# If a cup earns nothing or less (price <= cup cost), the lines never meet. We return `None`.

# %%
def break_even_cups(fixed=FIXED, price=PRICE, cup_cost=CUP_COST):
    earn = price - cup_cost
    if earn <= 0:
        return None
    return fixed / earn


def first_profitable_cup(fixed=FIXED, price=PRICE, cup_cost=CUP_COST, limit=1000):
    """Count whole cups one by one until income >= cost. Returns None if never within `limit`."""
    cups = np.arange(0, limit + 1)
    ok = np.nonzero(profit(cups, fixed, price, cup_cost) >= -1e-9)[0]
    return int(cups[ok[0]]) if len(ok) else None


# %% [markdown]
# ## Step 4: see it
# Left: the two lines, with the meeting point marked. Right: profit after each batch of cups.
# Below the zero line you are in loss; above it, in profit.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for c in (0, 10, 25, 39, 40, 41, 60):
        print(f"cups {c:3d}: cost {float(total_cost(c)):7.2f}  income {float(income(c)):7.2f}  profit {float(profit(c)):7.2f}")
    q = break_even_cups()
    print("break-even cups:", q, " counted one by one:", first_profitable_cup())
    print("price 0.50 (same as cup cost) ->", break_even_cups(price=0.50))

    cups = np.arange(0, 101)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(cups, total_cost(cups), color="#d9534f", label="total cost")
    ax.plot(cups, income(cups), color="#2a9d8f", label="income")
    ax.plot([q], [float(income(q))], "ko")
    ax.annotate(f"break-even: {q:.0f} cups, ${float(income(q)):.0f}", (q, float(income(q))), (47, 40))
    ax.set_xlabel("cups sold (cups)")
    ax.set_ylabel("dollars ($)")
    ax.set_title("Income catches up with cost")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "stall_lines.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    pr = profit(cups)
    ax2.bar(cups, pr, color=np.where(pr >= 0, "#2a9d8f", "#d9534f"), width=0.9)
    ax2.axhline(0, color="black", lw=0.8)
    ax2.set_xlabel("cups sold (cups)")
    ax2.set_ylabel("profit ($)")
    ax2.set_title("Profit starts at -60 dollars and gains 1.50 dollars per cup")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "stall_profit.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
