"""Session 1 (Level 1): do not put all your eggs in one basket.

General education only, not investment advice. The shops and numbers are made up.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: two shops are steadier than one
# **A. Real-world problem.** You have some savings to put into a small business. One shop
# sells umbrellas, another sells ice cream. On rainy days the umbrella shop earns a lot and the
# ice cream shop earns little; on dry days it is the other way round. If you put all your money
# in one shop, your income jumps up and down with the weather. If you split it, the ups of one
# shop cover the downs of the other.
#
# **Safety note.** This is a toy model for learning. It is NOT investment advice. The shops
# are made up, the income numbers are made up, and real markets do not behave like a coin flip
# of weather. Past results never predict the future.
#
# **Plan.** (1) write each shop's income on a rainy and a dry day, (2) simulate 365 days with a
# seeded random generator, (3) measure the average and the swing of the income, (4) split the
# money between the shops and watch the swing shrink.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# income per day, in made-up money units, when all the money is in that shop
UMBRELLA = {"rain": 100.0, "dry": 20.0}
ICE_CREAM = {"rain": 30.0, "dry": 90.0}
P_RAIN = 0.5          # chance that a day is rainy


# %% [markdown]
# ## Step 1: the weather and the shop incomes
# `simulate_weather` gives a list of True (rainy) / False (dry) days from a seeded generator,
# so everyone gets the same days. `shop_income` turns the weather into income.

# %%
def simulate_weather(n_days, seed=1, p_rain=P_RAIN):
    """True for a rainy day, False for a dry day (seeded, repeatable)."""
    rng = np.random.default_rng(seed)
    return rng.random(n_days) < p_rain


def shop_income(shop, rain):
    """Income for each day: shop['rain'] on rainy days, shop['dry'] on dry days."""
    return np.where(rain, shop["rain"], shop["dry"])


# %% [markdown]
# ## Step 2: split the money
# Put a fraction `f` of the money into the umbrella shop and `1 - f` into the ice cream shop.
# Your income each day is the same split of the two shop incomes:
#
#     income = f * umbrella + (1 - f) * ice cream
#
# `f = 1` is "all eggs in the umbrella basket"; `f = 0.5` is half and half.

# %%
def split_income(rain, f):
    return f * shop_income(UMBRELLA, rain) + (1 - f) * shop_income(ICE_CREAM, rain)


# %% [markdown]
# ## Step 3: how steady is the income?
# * **Average** = the sum of the daily incomes divided by the number of days.
# * **Swing** (standard deviation) = the typical distance of a day from the average. A small
#   swing means a steady income. NumPy's `std` computes it.
#
# With only two kinds of day we can also compute both exactly. With rain chance p, the income
# is `R` on rainy days and `D` on dry days, so
# average = p R + (1 - p) D and swing = |R - D| * sqrt(p (1 - p)).

# %%
def exact_mean_std(f, p_rain=P_RAIN):
    rainy = float(split_income(np.array([True]), f)[0])
    dry = float(split_income(np.array([False]), f)[0])
    mean = p_rain * rainy + (1 - p_rain) * dry
    std = abs(rainy - dry) * np.sqrt(p_rain * (1 - p_rain))
    return mean, std


def sample_mean_std(f, n_days=365, seed=1):
    inc = split_income(simulate_weather(n_days, seed), f)
    return float(inc.mean()), float(inc.std())


def zero_swing_split():
    """The split f that makes rainy-day income equal dry-day income (swing = 0).
    Solve f*100 + (1-f)*30 = f*20 + (1-f)*90."""
    a = UMBRELLA["rain"] - ICE_CREAM["rain"] - (UMBRELLA["dry"] - ICE_CREAM["dry"])
    b = ICE_CREAM["dry"] - ICE_CREAM["rain"]
    return b / a


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    rain = simulate_weather(365, seed=1)
    print(f"rainy days in 365: {int(rain.sum())}")
    for name, f in [("all umbrella", 1.0), ("all ice cream", 0.0), ("half and half", 0.5)]:
        m, s = sample_mean_std(f)
        em, es = exact_mean_std(f)
        print(f"{name:14s} sample: mean {m:6.2f} swing {s:5.2f}   exact: mean {em:6.2f} swing {es:5.2f}")
    fz = zero_swing_split()
    print(f"split with zero swing: f = {fz:.4f} (mean {exact_mean_std(fz)[0]:.1f})")

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), sharey=True)
    days = np.arange(1, 31)
    for ax, (name, f) in zip(axes, [("all umbrella", 1.0), ("all ice cream", 0.0), ("half and half", 0.5)]):
        inc = split_income(rain, f)[:30]
        ax.bar(days, inc, color=["#2a6fdb" if r else "#e0a030" for r in rain[:30]])
        ax.set_title(f"{name}: swing {sample_mean_std(f)[1]:.1f}")
        ax.set_xlabel("day (blue = rain, orange = dry)")
    axes[0].set_ylabel("income per day (money units)")
    fig.tight_layout()
    fig.savefig(OUT / "shop_incomes.png", dpi=120)

    fs = np.linspace(0, 1, 101)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(100 * fs, [exact_mean_std(f)[1] for f in fs], label="exact swing")
    ax2.plot(100 * fs[::10], [sample_mean_std(f)[1] for f in fs[::10]], "o", label="365 simulated days")
    ax2.axvline(100 * fz, color="gray", ls=":")
    ax2.set_xlabel("money in the umbrella shop (%)")
    ax2.set_ylabel("swing of daily income (money units)")
    ax2.set_title("The swing is smallest near a 43% umbrella split")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "swing_vs_split.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Real businesses (and real investments) are not perfectly opposite, and their numbers are not
# known in advance. Session 2 measures "how opposite" with a number called correlation.
