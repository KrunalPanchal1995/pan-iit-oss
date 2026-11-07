"""Session 2 (Level 2): the cost-volume-profit model of a small bakery.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: profit = (p - v) q - F
# **A. Real-world problem.** A made-up neighbourhood bakery sells loaves. Each month it pays
# rent, an oven lease and wages whether or not anyone buys bread. Each loaf also costs flour
# and energy. The owner asks four things: how many loaves to sell to break even, how far
# sales can fall before the bakery loses money, how many loaves earn a target profit, and
# how risky the whole thing is. This session turns the lemonade stall into equations.
#
# *General education only: the bakery and its numbers are made up, and this is not
# financial advice.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

F = 1200.0        # fixed cost per month, dollars (rent, oven lease, wages)
P = 3.50          # price of one loaf, dollars per loaf
V = 1.40          # variable cost of one loaf, dollars per loaf
Q = 800.0         # expected loaves sold per month
DEMAND_A = 1675.0   # demand estimate: loaves per month at price 0 ...
DEMAND_B = 250.0    # ... minus 250 loaves for every extra dollar of price


# %% [markdown]
# ## Step 1: profit and contribution margin
# Profit = income - cost = p q - (F + v q) = (p - v) q - F.
# The **contribution margin** p - v is what one loaf contributes towards the fixed cost.

# %%
def profit(q, p=P, v=V, fixed=F):
    """Monthly profit in dollars for q loaves."""
    return (p - v) * np.asarray(q, dtype=float) - fixed


def contribution_margin(p=P, v=V):
    return p - v


def contribution_ratio(p=P, v=V):
    """Share of each sales dollar left after variable cost."""
    return (p - v) / p


# %% [markdown]
# ## Step 2: break-even quantity and revenue
# Set profit = 0: q* = F / (p - v). The revenue at that point is p q* = F / (1 - v/p).
# There is no break-even when p <= v. We check the formula by *scanning* q on a fine grid.

# %%
def break_even_qty(fixed=F, p=P, v=V):
    cm = p - v
    if cm <= 0:
        return None
    return fixed / cm


def break_even_revenue(fixed=F, p=P, v=V):
    q = break_even_qty(fixed, p, v)
    return None if q is None else p * q


def scan_break_even(fixed=F, p=P, v=V, q_max=5000.0, step=0.01):
    """First q on a grid where profit >= 0 (numerical check of the formula)."""
    q = np.arange(0.0, q_max + step, step)
    ok = np.nonzero(profit(q, p, v, fixed) >= -1e-9)[0]
    return float(q[ok[0]]) if len(ok) else None


def whole_units(x):
    """Round up to whole loaves (with a tiny tolerance for round-off)."""
    return int(np.ceil(x - 1e-9))


# %% [markdown]
# ## Step 3: margin of safety and the target profit
# Margin of safety = how far sales can fall before profit is zero, as a share of sales:
# (q - q*) / q. For a target profit T: (p - v) q - F = T, so q = (F + T) / (p - v).

# %%
def margin_of_safety(q=Q, fixed=F, p=P, v=V):
    be = break_even_qty(fixed, p, v)
    if be is None or q <= 0:
        return None
    return (q - be) / q


def target_qty(target, fixed=F, p=P, v=V):
    cm = p - v
    if cm <= 0:
        return None
    return (fixed + target) / cm


# %% [markdown]
# ## Step 4: degree of operating leverage
# Fixed costs act like a lever: when sales rise a little, profit rises a lot, and when sales
# fall, profit falls a lot. DOL = (contribution margin * q) / profit = (percent change in
# profit) / (percent change in sales). It is not defined when profit is zero.

# %%
def dol(q=Q, fixed=F, p=P, v=V):
    pr = float(profit(q, p, v, fixed))
    if abs(pr) < 1e-9:
        return None
    return (p - v) * q / pr


def dol_numeric(q=Q, fixed=F, p=P, v=V, change=0.10):
    """Percent change in profit divided by the percent change in sales, by direct recomputation."""
    p0 = float(profit(q, p, v, fixed))
    p1 = float(profit(q * (1 + change), p, v, fixed))
    return ((p1 - p0) / p0) / change


# %% [markdown]
# ## Step 5: a design problem - choose the price
# Suppose the owner estimates that demand falls as the price rises:
# loaves per month = 1675 - 250 * price. Then both the margin and the quantity depend on
# the price. We want a price that gives a target profit.

# %%
def demand(price):
    return np.maximum(DEMAND_A - DEMAND_B * np.asarray(price, dtype=float), 0.0)


def profit_at_price(price, fixed=F, v=V):
    return (np.asarray(price, dtype=float) - v) * demand(price) - fixed


def best_price(v=V):
    """Price with the largest profit: zero slope of (p - v)(a - b p)."""
    return (DEMAND_A / DEMAND_B + v) / 2.0


def prices_for_target(target, fixed=F, v=V):
    """Both prices that give exactly `target` profit (empty list if the target cannot be reached)."""
    b1 = (DEMAND_A + DEMAND_B * v) / DEMAND_B
    c1 = (DEMAND_A * v + fixed + target) / DEMAND_B
    disc = b1 * b1 - 4 * c1
    if disc < 0:
        return []
    r = np.sqrt(disc)
    return [(b1 - r) / 2, (b1 + r) / 2]


def scan_prices_for_target(target, fixed=F, v=V, lo=1.5, hi=6.5, step=0.0005):
    """Numerical check: prices where profit crosses the target (linear interpolation on a grid)."""
    pr = np.arange(lo, hi, step)
    d = profit_at_price(pr, fixed, v) - target
    idx = np.nonzero(np.sign(d[:-1]) * np.sign(d[1:]) <= 0)[0]
    return [float(pr[i] - d[i] * step / (d[i + 1] - d[i])) if d[i + 1] != d[i] else float(pr[i]) for i in idx]


# %% [markdown]
# ## See it
# Left: income and cost lines against loaves, with the break-even point and the margin of
# safety. Right: profit against price for the design problem.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    q_star = break_even_qty()
    print(f"contribution margin {contribution_margin():.2f} $/loaf, ratio {contribution_ratio():.2f}")
    print(f"break-even {q_star:.2f} loaves (scan {scan_break_even():.2f}), whole loaves {whole_units(q_star)}")
    print(f"break-even revenue ${break_even_revenue():.2f}")
    print(f"profit at {Q:.0f} loaves: ${float(profit(Q)):.2f}, margin of safety {100 * margin_of_safety():.2f} %")
    print(f"loaves for $600 profit: {target_qty(600):.2f} (whole: {whole_units(target_qty(600))})")
    print(f"DOL {dol():.2f}, numeric {dol_numeric():.2f}")
    for ch in (0.10, -0.10):
        q2 = Q * (1 + ch)
        print(f"sales {100 * ch:+.0f} % -> {q2:.0f} loaves, profit ${float(profit(q2)):.2f}")
    t = prices_for_target(500)
    print("prices for $500 profit:", np.round(t, 4), " scan:", np.round(scan_prices_for_target(500), 3))
    print("loaves at those prices:", np.round(demand(t), 1))
    print(f"best price {best_price():.2f}, best profit ${float(profit_at_price(best_price())):.2f}")

    q = np.linspace(0, 1500, 301)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(q, P * q, color="#2a9d8f", label="income")
    ax.plot(q, F + V * q, color="#d9534f", label="total cost")
    ax.plot([q_star], [P * q_star], "ko")
    ax.annotate(f"break-even {q_star:.0f} loaves", (q_star, P * q_star), (150, 3500))
    ax.annotate("", xy=(Q, 300), xytext=(q_star, 300), arrowprops={"arrowstyle": "<->"})
    ax.text(q_star + 10, 380, "margin of safety", fontsize=8)
    ax.set_xlabel("loaves sold per month (loaves)")
    ax.set_ylabel("dollars per month ($)")
    ax.set_title("Income, cost and the break-even point")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "cvp_lines.png", dpi=120)

    price = np.linspace(1.5, 6.5, 400)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(price, profit_at_price(price), color="#1f6f8b")
    ax2.axhline(500, color="gray", ls="--", label="target $500")
    ax2.plot(t, [500, 500], "ko")
    ax2.set_xlabel("price (dollars per loaf)")
    ax2.set_ylabel("monthly profit ($)")
    ax2.set_title("Two prices reach the $500 target")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "price_design.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
