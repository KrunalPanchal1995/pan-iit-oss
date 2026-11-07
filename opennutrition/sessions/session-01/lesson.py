"""Session 1 (Level 1): food energy in, activity energy out, like a bank balance.

General education only. Not medical or dietary advice. All food and activity values are
rounded textbook values and are APPROXIMATE.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: food energy in, activity energy out
# **A. Real-world problem.** Food carries energy and your body spends energy all day, even
# asleep. If more comes in than goes out, the balance is positive; if less, negative. This
# is exactly a bank balance, and we can compute it. (This is general education, not
# medical or dietary advice. The people below are made up.)
#
# **Plan.** (1) units: kilocalories and kilojoules, (2) energy in from foods, (3) energy out
# from activities, (4) the daily balance and the running total over days.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

KJ_PER_KCAL = 4.184   # 1 kilocalorie (food Calorie) = 4.184 kilojoules


# %% [markdown]
# ## Step 1: two units for the same thing
# Food labels use kilocalories (kcal, also written Calories) or kilojoules (kJ).
# They measure the same quantity, energy: 1 kcal = 4.184 kJ.

# %%
def kcal_to_kj(kcal):
    return kcal * KJ_PER_KCAL


def kj_to_kcal(kj):
    return kj / KJ_PER_KCAL


# %% [markdown]
# ## Step 2: energy in (APPROXIMATE textbook values per typical serving)
# Real foods vary with size, ripeness and recipe. These rounded values are for practice only.

# %%
FOODS = {                      # kcal per typical serving (approximate)
    "banana (1 medium)": 105,
    "boiled egg (1)": 78,
    "slice of bread (1)": 80,
    "cooked rice (1 cup)": 205,
    "apple (1 medium)": 95,
    "milk (1 glass, 250 mL)": 150,
}


def energy_in(items):
    """items: list of (food name, number of servings). Returns kcal."""
    return float(sum(FOODS[name] * n for name, n in items))


# %% [markdown]
# ## Step 3: energy out (APPROXIMATE)
# Activity intensity is often given as a MET value: "how many times the resting rate".
# Rule of thumb used in textbooks: energy (kcal) is about MET x body mass (kg) x time (hours),
# because 1 MET is about 1 kcal per kg per hour. Values below are rounded and approximate.

# %%
MET = {
    "sleeping": 0.95,
    "sitting": 1.3,
    "light chores": 2.3,
    "walking": 3.5,
    "cycling": 6.0,
    "running": 9.0,
}


def energy_out(schedule, mass_kg):
    """schedule: list of (activity, hours). Returns kcal."""
    return float(sum(MET[a] * mass_kg * h for a, h in schedule))


# A made-up person, Meera (60 kg), and a 24 hour day.
MEERA_KG = 60.0
MEERA_DAY = [("sleeping", 8), ("sitting", 11), ("light chores", 3), ("walking", 1.5), ("cycling", 0.5)]
MEERA_MEALS = [("cooked rice (1 cup)", 4), ("boiled egg (1)", 3), ("banana (1 medium)", 2),
               ("milk (1 glass, 250 mL)", 3), ("slice of bread (1)", 6), ("apple (1 medium)", 1)]


# %% [markdown]
# ## Step 4: the balance, like a bank account
# balance = energy in - energy out. A running total over days is the "account statement".

# %%
def daily_balance(kcal_in, kcal_out):
    return kcal_in - kcal_out


def running_balance(daily):
    """Cumulative sum of daily balances (kcal)."""
    return np.cumsum(np.asarray(daily, dtype=float))


# %% [markdown]
# ## Step 5: see it
# Left: Meera's day, energy in against energy out. Right: the running total over 14 days when
# her balance is the same every day.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    e_in = energy_in(MEERA_MEALS)
    e_out = energy_out(MEERA_DAY, MEERA_KG)
    bal = daily_balance(e_in, e_out)
    print(f"Meera: in {e_in:.0f} kcal ({kcal_to_kj(e_in):.0f} kJ), out {e_out:.0f} kcal, balance {bal:.0f} kcal")
    hours = sum(h for _, h in MEERA_DAY)
    print("hours in the day:", hours)

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(["energy in", "energy out"], [e_in, e_out], color=["#2a9d8f", "#e76f51"])
    ax.set_ylabel("energy per day (kcal, approximate)")
    ax.set_title("Meera's day: in versus out")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(OUT / "day_bars.png", dpi=120)

    days = np.arange(1, 15)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for b, lab in [(bal, "Meera's balance"), (-300.0, "300 kcal short each day"), (0.0, "perfect balance")]:
        ax2.plot(days, running_balance([b] * 14), marker="o", ms=3, label=lab)
    ax2.set_xlabel("day")
    ax2.set_ylabel("running balance (kcal)")
    ax2.set_title("The account statement over 14 days")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "running_balance.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
