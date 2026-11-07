"""Session 3 (Level 3): a break-even model that admits it is uncertain.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: break-even with a mix, steps, uncertainty and time
# **A. Real-world problem.** The made-up bakery of Session 2 is more complicated than one
# product with one price. It sells bread *and* cakes, it must buy a second oven when it grows,
# its prices, costs and customers are never exactly what the plan says, and the start-up money
# is paid back slowly, over months. A single break-even number hides all of that. Today you
# build the richer model, check it against a formula, and ask which input matters most.
#
# *General education only: the bakery and its numbers are made up, and this is not
# financial advice.*

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

F, P, V, Q = 1200.0, 3.50, 1.40, 800.0          # as in Session 2
DEMAND_A, DEMAND_B = 1675.0, 250.0              # loaves per month = 1675 - 250 * price
PRODUCTS = {"loaf": (3.50, 1.40), "cake": (18.0, 9.0)}   # (price, variable cost) in dollars each


# %% [markdown]
# ## Step 1: several products and a sales mix
# The **sales mix** says what share of the *units* sold each product has. The weighted
# contribution margin is the mix-weighted average of (p - v). Break-even units for the
# whole bakery: F / weighted margin. Changing the mix changes the answer even if F does not.

# %%
def weighted_cm(mix):
    """Weighted contribution margin, dollars per unit sold; mix = {product: share of units}."""
    if abs(sum(mix.values()) - 1.0) > 1e-9:
        raise ValueError("mix shares must add up to 1")
    return sum(share * (PRODUCTS[name][0] - PRODUCTS[name][1]) for name, share in mix.items())


def multi_break_even(mix, fixed=F):
    """Total break-even units and units of each product (None if the mix earns nothing)."""
    w = weighted_cm(mix)
    if w <= 0:
        return None
    total = fixed / w
    return total, {name: share * total for name, share in mix.items()}


# %% [markdown]
# ## Step 2: step-fixed costs (a second oven)
# One oven bakes at most 700 loaves a month and costs $1200 a month in all. Above 700 loaves a
# second oven adds $900. So the fixed cost jumps, and the profit line jumps down with it.
# That can create *several* crossings of zero. We find them by scanning whole loaves.

# %%
def step_fixed(q, base=F, extra=900.0, cap=700):
    """Fixed cost needed to bake q loaves: base for the first oven, `extra` for each further one."""
    ovens = max(1, int(math.ceil(q / cap - 1e-12)))
    return base + extra * (ovens - 1)


def profit_step(q, p=P, v=V, base=F, extra=900.0, cap=700):
    return (p - v) * q - step_fixed(q, base, extra, cap)


def sign_changes(fn, q_max=1400):
    """Scan q = 0, 1, 2, ... and report each place where 'profit >= 0' flips: (q_before, q_after, 'up' or 'down')."""
    out = []
    prev = fn(0) >= -1e-9
    for q in range(1, q_max + 1):
        now = fn(q) >= -1e-9
        if now != prev:
            out.append((q - 1, q, "up" if now else "down"))
        prev = now
    return out


def step_break_evens(p=P, v=V, base=F, extra=900.0, cap=700, ovens_max=2):
    """Formula for each oven count k: q_k = F_k / (p - v), kept only if it lies inside that step."""
    res = []
    for k in range(1, ovens_max + 1):
        qk = (base + extra * (k - 1)) / (p - v)
        if (k - 1) * cap < qk <= k * cap:
            res.append(qk)
    return res


# %% [markdown]
# ## Step 3: uncertainty (Monte Carlo)
# Price, variable cost and demand are never exactly as planned. We draw 20000 random
# "months" from normal distributions (seeded, so every run gives the same numbers) and
# compute the profit of each one. The share of months with profit < 0 is the loss probability.

# %%
def simulate_profit(n=20000, seed=42, p_mu=P, p_sd=0.20, v_mu=V, v_sd=0.15, d_mu=Q, d_sd=150.0, fixed=F):
    rng = np.random.default_rng(seed)
    price = rng.normal(p_mu, p_sd, n)
    vcost = rng.normal(v_mu, v_sd, n)
    demand = np.maximum(rng.normal(d_mu, d_sd, n), 0.0)
    return (price - vcost) * demand - fixed


def summarize(profits):
    return {"mean": float(np.mean(profits)), "std": float(np.std(profits)),
            "p5": float(np.percentile(profits, 5)), "p50": float(np.percentile(profits, 50)),
            "p95": float(np.percentile(profits, 95)), "loss": float(np.mean(profits < 0))}


def loss_probability_demand_only(d_mu=Q, d_sd=150.0, fixed=F, p=P, v=V):
    """Reference formula when only demand is random: P(q < q*) = Phi((q* - mean) / sd)."""
    z = (fixed / (p - v) - d_mu) / d_sd
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


# %% [markdown]
# ## Step 4: which input matters most (tornado)
# Move one input at a time by -10 % and +10 %, keep the others at plan, and record the profit.
# The input with the widest swing is the one to watch.

# %%
def model_profit(p=P, v=V, q=Q, fixed=F):
    return (p - v) * q - fixed


def tornado(pct=0.10):
    """List of (name, profit_low, profit_high, swing) sorted by swing, largest first."""
    base = {"price": P, "variable cost": V, "demand": Q, "fixed cost": F}
    keys = {"price": "p", "variable cost": "v", "demand": "q", "fixed cost": "fixed"}
    rows = []
    for name, value in base.items():
        lo = model_profit(**{keys[name]: value * (1 - pct)})
        hi = model_profit(**{keys[name]: value * (1 + pct)})
        rows.append((name, lo, hi, abs(hi - lo)))
    return sorted(rows, key=lambda r: -r[3])


# %% [markdown]
# ## Step 5: time value - payback and net present value
# Start-up money is spent now; profit arrives month by month. A dollar next year is worth a
# little less than a dollar today, so we *discount* each month's cash by the monthly rate.
# (The openloan repo converts rates the same way for loans.) Payback = first month in which
# the running total reaches the start-up cost. NPV = discounted cash received - start-up cost.

# %%
def monthly_rate(annual):
    return (1.0 + annual) ** (1.0 / 12.0) - 1.0


def cumulative_cash(startup, flows, annual_rate=0.0):
    """Running total after each month, starting from -startup."""
    r = monthly_rate(annual_rate)
    t = np.arange(1, len(flows) + 1)
    return -startup + np.cumsum(np.asarray(flows, dtype=float) / (1.0 + r) ** t)


def payback_month(startup, flows, annual_rate=0.0):
    """First whole month with running total >= 0 (None if it never pays back in the horizon)."""
    ok = np.nonzero(cumulative_cash(startup, flows, annual_rate) >= -1e-9)[0]
    return int(ok[0]) + 1 if len(ok) else None


def npv(startup, flows, annual_rate):
    return float(cumulative_cash(startup, flows, annual_rate)[-1])


# %% [markdown]
# ## Step 6: failure cases
# (a) If the price is not above the variable cost there is *no* break-even; the planner must
# say so. (b) If demand falls as price rises, there may be two break-even prices, or none.

# %%
def demand(price):
    return np.maximum(DEMAND_A - DEMAND_B * np.asarray(price, dtype=float), 0.0)


def profit_at_price(price, fixed=F, v=V):
    return (np.asarray(price, dtype=float) - v) * demand(price) - fixed


def break_even_prices(fixed=F, v=V):
    """Prices where profit = 0 with linear demand: roots of (p - v)(a - b p) = F. Empty list if none."""
    b1 = (DEMAND_A + DEMAND_B * v) / DEMAND_B
    c1 = (DEMAND_A * v + fixed) / DEMAND_B
    disc = b1 * b1 - 4 * c1
    if disc < 0:
        return []
    r = math.sqrt(disc)
    return [(b1 - r) / 2, (b1 + r) / 2]


def plan(fixed, p, v):
    """What a careful planner says: the break-even, or the reason there is none."""
    if p <= v:
        return f"No break-even: the price {p:.2f} does not cover the variable cost {v:.2f}."
    return f"Break-even at {fixed / (p - v):.1f} units."


# %% [markdown]
# ## Step 7: choose price and capacity (the mini-project engine)
# Three oven sizes: capacity (loaves/month) -> (fixed cost per month, start-up cost).
# Sales = min(demand, capacity). For each choice we report break-even, margin of safety,
# loss probability and payback.

# %%
OPTIONS = {600: (1000.0, 5000.0), 800: (1300.0, 6500.0), 1000: (1600.0, 8000.0)}


def evaluate(price, capacity, n=20000, seed=7, v_mu=V, v_sd=0.15, d_sd=150.0, horizon=36):
    fixed, startup = OPTIONS[capacity]
    rng = np.random.default_rng(seed)
    vcost = rng.normal(v_mu, v_sd, n)
    want = np.maximum(rng.normal(float(demand(price)), d_sd, n), 0.0)
    sold = np.minimum(want, capacity)
    pr = (price - vcost) * sold - fixed
    mean_profit = float(np.mean(pr))
    q_star = fixed / (price - v_mu) if price > v_mu else None
    mean_sold = float(np.mean(sold))
    mos = None if q_star is None else (mean_sold - q_star) / mean_sold
    return {"price": price, "capacity": capacity, "break_even": q_star, "mean_sold": mean_sold,
            "mos": mos, "mean_profit": mean_profit, "loss": float(np.mean(pr < 0)),
            "payback": payback_month(startup, [mean_profit] * horizon)}


def passes(r):
    """Mini-project rule: loss probability <= 5 %, payback within 12 months, margin of safety >= 20 %."""
    return r["loss"] <= 0.05 and r["payback"] is not None and r["payback"] <= 12 and r["mos"] is not None and r["mos"] >= 0.20


# %% [markdown]
# ## See it
# Three figures: the broken-up profit line with its crossings, the Monte Carlo histogram,
# and the tornado chart.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for name, mix in {"80/20": {"loaf": 0.8, "cake": 0.2}, "90/10": {"loaf": 0.9, "cake": 0.1},
                      "60/40": {"loaf": 0.6, "cake": 0.4}}.items():
        tot, parts = multi_break_even(mix)
        print(f"mix loaf/cake {name}: weighted margin {weighted_cm(mix):.2f}, break-even {tot:.1f} units "
              f"({parts['loaf']:.1f} loaves, {parts['cake']:.1f} cakes)")
    print("sign changes:", sign_changes(profit_step), " formula:", [round(x, 2) for x in step_break_evens()])
    prof = simulate_profit()
    s = summarize(prof)
    print({k: round(x, 4) for k, x in s.items()})
    only = simulate_profit(p_sd=0.0, v_sd=0.0)
    print(f"demand only: simulated loss {np.mean(only < 0):.4f}, formula {loss_probability_demand_only():.4f}")
    for row in tornado():
        print(f"tornado {row[0]:14s} low {row[1]:7.1f} high {row[2]:7.1f} swing {row[3]:6.1f}")
    flows = [480.0] * 36
    print("payback", payback_month(6000, flows), "discounted payback", payback_month(6000, flows, 0.12),
          "NPV 24 months", round(npv(6000, flows[:24], 0.12), 2), "undiscounted", round(npv(6000, flows[:24], 0.0), 2))
    print("break-even prices", np.round(break_even_prices(), 3), " F=1800:", break_even_prices(1800.0))
    print(plan(1200, 1.4, 1.4))
    for cap in OPTIONS:
        for price in (3.5, 4.0, 4.25, 4.5):
            r = evaluate(price, cap)
            print(cap, price, round(r["break_even"], 1), round(r["mean_sold"], 1), round(r["mos"], 3),
                  round(r["mean_profit"], 1), round(r["loss"], 3), r["payback"], passes(r))

    # figure 1: step profit
    q = np.arange(0, 1401)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(q, [profit_step(x) for x in q], color="#1f6f8b", lw=1.5)
    ax.axhline(0, color="black", lw=0.8)
    ax.axvline(700, color="gray", ls=":")
    ax.text(705, -1500, "oven full:\nsecond oven needed", fontsize=8)
    for a, b, d in sign_changes(profit_step):
        ax.plot([b], [0], "ro" if d == "down" else "go")
    ax.set_xlabel("loaves sold per month (loaves)")
    ax.set_ylabel("monthly profit ($)")
    ax.set_title("Step-fixed cost: profit crosses zero three times")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "step_profit.png", dpi=120)

    # figure 2: histogram
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.hist(prof, bins=60, color="#2a9d8f", alpha=0.85)
    ax2.axvline(0, color="#d9534f", lw=2)
    ax2.set_xlabel("monthly profit ($)")
    ax2.set_ylabel("number of simulated months (of 20000)")
    ax2.set_title(f"Profit distribution: {100 * s['loss']:.1f} % of months make a loss")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "profit_hist.png", dpi=120)

    # figure 3: tornado
    rows = tornado()[::-1]
    base = model_profit()
    fig3, ax3 = plt.subplots(figsize=(6, 3.6))
    for i, (name, lo, hi, _) in enumerate(rows):
        ax3.barh(i, hi - base, left=base, color="#2a9d8f")
        ax3.barh(i, lo - base, left=base, color="#d9534f")
    ax3.set_yticks(range(len(rows)))
    ax3.set_yticklabels([r[0] for r in rows])
    ax3.axvline(base, color="black", lw=0.8)
    ax3.set_xlabel("monthly profit ($) when the input moves -10 % (red) or +10 % (green)")
    ax3.set_title("Tornado: price matters most")
    ax3.grid(alpha=0.3, axis="x")
    fig3.tight_layout()
    fig3.savefig(OUT / "tornado.png", dpi=120)

    # figure 4: payback
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    months = np.arange(1, 37)
    ax4.plot(months, cumulative_cash(6000, flows), label="no discounting")
    ax4.plot(months, cumulative_cash(6000, flows, 0.12), label="discounted at 12 % a year")
    ax4.axhline(0, color="black", lw=0.8)
    ax4.set_xlabel("months after start-up (months)")
    ax4.set_ylabel("running total ($)")
    ax4.set_title("Payback: 13 months, or 14 with discounting")
    ax4.grid(alpha=0.3)
    ax4.legend()
    fig4.tight_layout()
    fig4.savefig(OUT / "payback.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
