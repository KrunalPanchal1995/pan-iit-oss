"""Session 1 (Level 1): a switch is on or off, and a row of switches can count.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: switches, lamps and counting in binary
# **A. Real-world problem.** A light switch is either on or off. A computer is built from
# an enormous number of such switches, yet it can store a photo, a song or your bank balance. How can
# something that only knows "on" and "off" hold a number like 13?
#
# **Plan.** (1) give each switch a place value, (2) write a number as a pattern of on/off,
# (3) read a pattern back as a number, (4) count with lamps from 0 to 15 and see the pattern.
# This is a simplified educational model of how computers store whole numbers.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: place values
# In the decimal number 345 the digit 3 is worth 3 hundreds, 4 is worth 4 tens and 5 is worth 5 ones.
# Each place is worth 10 times the place to its right. In binary each place is worth **2** times the
# place to its right, and each digit (a *bit*) is only 0 (off) or 1 (on). With 4 switches the places
# are worth 8, 4, 2 and 1.

# %%
def place_values(width=4):
    """Place value of each switch, left (biggest) to right: width 4 gives [8, 4, 2, 1]."""
    return [2 ** k for k in range(width - 1, -1, -1)]


def to_bits(n, width=4):
    """Number n as a list of 0/1 switches, biggest place first. Raises if n does not fit."""
    if n < 0 or n >= 2 ** width:
        raise ValueError(f"{n} does not fit in {width} switches (0 to {2 ** width - 1})")
    return [(n >> k) & 1 for k in range(width - 1, -1, -1)]


def from_bits(bits):
    """Read a list of 0/1 switches (biggest place first) back as a number: add up the place values."""
    return sum(b * v for b, v in zip(bits, place_values(len(bits))))


# %% [markdown]
# ## Step 2: lamps
# A row of lamps shows the pattern: `#` is a lamp that is on, `.` is off. Count how many different
# patterns n switches can make: each switch doubles the number of possibilities.

# %%
def lamps(n, width=4):
    return "".join("#" if b else "." for b in to_bits(n, width))


def count_patterns(width):
    """How many different on/off patterns `width` switches can make."""
    return 2 ** width


def largest(width):
    """Largest whole number that fits in `width` switches (all on)."""
    return 2 ** width - 1


def lamps_on(n, width=4):
    return sum(to_bits(n, width))


def count_table(width=4):
    """Rows (number, pattern) for counting from 0 up to the largest number."""
    return [(n, lamps(n, width)) for n in range(count_patterns(width))]


def add_one(n, width=4):
    """Add one and keep only `width` switches: past the largest number the count wraps to 0."""
    return (n + 1) % count_patterns(width)


# %% [markdown]
# ## Step 3: see it
# Left: the number 13 as a row of four switches and the sum 8 + 4 + 0 + 1. Right: the counting
# table 0 to 15, one row per number, one column per switch.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    bits = to_bits(13)
    print("13 as switches:", bits, "= sum of", [b * v for b, v in zip(bits, place_values())], "=", from_bits(bits))
    fig, ax = plt.subplots(figsize=(6, 3))
    for i, (b, v) in enumerate(zip(bits, place_values())):
        ax.add_patch(plt.Rectangle((i * 1.4, 0), 1.0, 1.0, color="#e9b44c" if b else "#c9ccd1"))
        ax.text(i * 1.4 + 0.5, 0.5, "on = 1" if b else "off = 0", ha="center", va="center", fontsize=9)
        ax.text(i * 1.4 + 0.5, 1.25, f"place value {v}", ha="center", fontsize=9)
        ax.text(i * 1.4 + 0.5, -0.35, f"{b} x {v} = {b * v}", ha="center", fontsize=9)
    ax.text(2.1, -0.9, "8 + 4 + 0 + 1 = 13", ha="center", fontsize=11, weight="bold")
    ax.set_xlim(-0.3, 5.9)
    ax.set_ylim(-1.2, 1.7)
    ax.axis("off")
    ax.set_title("The number 13 as a row of four switches")
    fig.savefig(OUT / "switches_13.png", dpi=120)

    grid = np.array([to_bits(n) for n in range(16)])
    fig2, ax2 = plt.subplots(figsize=(4.4, 6))
    ax2.imshow(grid, cmap="YlOrBr", aspect="auto", vmin=0, vmax=1.4)
    ax2.set_xticks(range(4), [str(v) for v in place_values()])
    ax2.set_yticks(range(16), [str(n) for n in range(16)])
    ax2.set_xlabel("switch place value (dark = on)")
    ax2.set_ylabel("number being shown (decimal)")
    ax2.set_title("Counting 0 to 15 with four lamps")
    fig2.tight_layout()
    fig2.savefig(OUT / "counting_lamps.png", dpi=120)
    for n, pattern in count_table():
        print(f"{n:2d}  {pattern}")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
