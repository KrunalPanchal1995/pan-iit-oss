"""Session 1 (Level 1): a number without a unit is not an answer.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a number without a unit is not an answer
# **A. Real-world problem.** A friend texts "the car did 60". Sixty what? Metres per second,
# kilometres per hour, miles per hour? Those are very different speeds. Today you build a unit
# converter, learn the SI prefixes, and see why every number must carry its unit.
#
# **Plan.** (1) tables of units with their size in SI, (2) a converter, (3) prefixes,
# (4) significant figures, (5) a picture of what one bare number can mean.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: every unit is "this many SI units"
# SI = the international system of units. Its base units for length, mass and time are the
# metre (m), kilogram (kg) and second (s). Every other unit is defined as a fixed multiple:
# 1 km = 1000 m, 1 ft = 0.3048 m (exactly), 1 mile = 1609.344 m (exactly).
# We store the multiplier and convert through the SI unit.

# %%
LENGTH = {"m": 1.0, "km": 1000.0, "cm": 0.01, "mm": 0.001, "in": 0.0254, "ft": 0.3048,
          "mi": 1609.344, "nmi": 1852.0}          # metres per unit
SPEED = {"m/s": 1.0, "km/h": 1000.0 / 3600.0, "mph": 1609.344 / 3600.0,
         "knot": 1852.0 / 3600.0, "ft/s": 0.3048}  # (metres per second) per unit


def convert(value, from_unit, to_unit, table):
    """Convert a number between two units of the same kind. Raises KeyError for unknown units."""
    return value * table[from_unit] / table[to_unit]


# %% [markdown]
# ## Step 2: prefixes are just powers of ten
# kilo = 10^3, mega = 10^6, milli = 10^-3, micro = 10^-6 ... A prefix is a shorthand
# multiplier, so 5 km = 5 * 10^3 m = 5000 m.

# %%
PREFIX = {"G": 9, "M": 6, "k": 3, "": 0, "m": -3, "u": -6, "n": -9}   # symbol -> power of ten


def with_prefix(value, symbol):
    """Value in the base unit for `value` written with a prefix (u means micro)."""
    return value * 10.0 ** PREFIX[symbol]


def best_prefix(value):
    """Choose the prefix that puts the number between 1 and 1000. Returns (number, symbol)."""
    if value == 0:
        return 0.0, ""
    power = 3 * int(np.floor(np.log10(abs(value)) / 3))
    power = max(-9, min(9, power))
    symbol = [s for s, p in PREFIX.items() if p == power][0]
    return value / 10.0 ** power, symbol


# %%
# %% [markdown]
# ## Step 3: significant figures say how much to trust a number
# A measurement of 12.3 m is good to about 0.1 m. Writing 12.3456 m would claim more than
# you know. `round_sig(x, n)` keeps n significant figures.

# %%
def round_sig(x, n):
    if x == 0:
        return 0.0
    return float(round(x, n - 1 - int(np.floor(np.log10(abs(x))))))


def label(value, unit, n=3):
    """A number is only an answer with its unit attached."""
    return f"{round_sig(value, n):g} {unit}"


# %% [markdown]
# ## Step 4: see the problem
# The same bare number 60 means five different speeds, depending on the unit.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    names = list(SPEED)
    ms = [60 * SPEED[u] for u in names]
    for u, v in zip(names, ms):
        print(f"60 {u:5s} = {v:7.3f} m/s")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(names, ms, color="#2a9d8f")
    ax.set_xlabel("unit written after the number 60")
    ax.set_ylabel("speed in SI (m/s)")
    ax.set_title("The same number 60 means five different speeds")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(OUT / "same_number.png", dpi=120)

    n = np.linspace(0, 100, 101)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for u in names:
        ax2.plot(n, n * SPEED[u], label=u)
    ax2.set_xlabel("number you read (no unit)")
    ax2.set_ylabel("speed (m/s)")
    ax2.set_title("Each unit is a straight line through the origin; its slope is the unit size")
    ax2.grid(alpha=0.3)
    ax2.legend(title="unit")
    fig2.tight_layout()
    fig2.savefig(OUT / "unit_lines.png", dpi=120)
    print("72 km/h =", label(convert(72, "km/h", "m/s", SPEED), "m/s"))
    print("60 mph  =", label(convert(60, "mph", "km/h", SPEED), "km/h"))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
