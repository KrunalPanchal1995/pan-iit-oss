"""Session 1 (Level 1): computers store numbers with limited digits.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: numbers with gaps
# **A. Real-world problem.** Type 0.1 + 0.2 into almost any programming language and it
# does not give exactly 0.3. A spreadsheet, a calculator app and a missile computer all store
# numbers with a limited number of binary digits, so between two stored numbers there is a gap.
#
# **Plan.** (1) see what is really stored for 0.1, (2) measure the gap next to a number,
# (3) watch the gap grow with the size of the number, (4) learn the safe way to compare.

# %%
import pathlib
from decimal import Decimal

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: what is stored for 0.1?
# Computers use binary. In binary, 0.1 is a repeating pattern 0.000110011001100... that never
# ends, just as 1/3 = 0.3333... never ends in decimal. The computer keeps only the first
# 53 significant binary digits, so the stored number is very close to 0.1 but not equal.
# `Decimal(x)` prints the exact value stored in the float `x`.

# %%
def stored_value(x, digits=30):
    """Exact decimal value stored in the float x, cut to `digits` decimal places."""
    return format(Decimal(float(x)), f".{digits}f")


def sum_error_01_02():
    """(0.1 + 0.2) - 0.3 computed in floating point."""
    return (0.1 + 0.2) - 0.3


# %% [markdown]
# ## Step 2: the gap next to a number
# Stored numbers are not evenly spaced over the whole number line. `np.spacing(x)` is the gap
# between x and the next larger stored number. In a format with m fraction bits, the numbers
# between 2^k and 2^(k+1) are spaced exactly 2^(k - m) apart. So the gap doubles every time the
# number doubles. The *relative* gap, gap / x, stays between 2^-m / 2 and 2^-m.

# %%
def gap(x):
    """Gap between the positive float x and the next larger float (64-bit)."""
    return float(np.spacing(abs(float(x))))


def relative_gap(x):
    return gap(x) / abs(float(x))


def toy_gap(x, m):
    """Gap above x >= 1 in a toy format with m fraction bits: 2^(floor(log2 x) - m)."""
    return 2.0 ** (int(np.floor(np.log2(x))) - m)


def toy_numbers(m, lo=1.0, hi=16.0):
    """All numbers of the toy format with m fraction bits in [lo, hi)."""
    out = []
    k = int(np.floor(np.log2(lo)))
    while 2.0 ** k < hi:
        out.append(2.0 ** k * (1 + np.arange(2 ** m) / 2 ** m))
        k += 1
    v = np.concatenate(out)
    return v[(v >= lo) & (v < hi)]


# %% [markdown]
# ## Step 3: comparing safely
# Because of the gaps, `==` on computed floats is dangerous. Compare with a tolerance
# that is relative to the size of the numbers.

# %%
def nearly_equal(a, b, rel=1e-9, abs_tol=0.0):
    return abs(a - b) <= max(rel * max(abs(a), abs(b)), abs_tol)


# %% [markdown]
# ## Step 4: see it
# Left: the stored numbers of a tiny toy format (3 fraction bits) between 1 and 16: the ticks
# spread out as the numbers grow. Right: the real 64-bit gap against magnitude on log axes.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("0.1 is stored as", stored_value(0.1))
    print("0.1 + 0.2 =", repr(0.1 + 0.2), "; (0.1 + 0.2) - 0.3 =", sum_error_01_02())
    for x in (1.0, 1000.0, 1e8, 1e16):
        print(f"gap above {x:9.1e} is {gap(x):.3e}  (relative {relative_gap(x):.2e})")
    print("2**53 + 1 == 2**53 ?", 2.0 ** 53 + 1 == 2.0 ** 53)

    fig, ax = plt.subplots(figsize=(7, 2.6))
    v = toy_numbers(3)
    ax.vlines(v, 0, 1, color="#2a6fdb")
    for k in range(4):
        ax.axvline(2 ** k, color="#d9534f", lw=1.4, ls=":")
    ax.set_xlim(0.8, 16.2)
    ax.set_yticks([])
    ax.set_xlabel("value (units); dotted lines mark powers of two")
    ax.set_title("A toy format with 3 fraction bits: gaps double with each power of two")
    fig.tight_layout()
    fig.savefig(OUT / "toy_number_line.png", dpi=120)

    xs = np.logspace(-6, 20, 200)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.loglog(xs, [gap(x) for x in xs], label="gap above x (64-bit float)")
    ax2.loglog(xs, xs * 2.0 ** -52, ls="--", label="x * 2^-52 (upper edge)")
    ax2.set_xlabel("magnitude x (units)")
    ax2.set_ylabel("gap to next float (same units as x)")
    ax2.set_title("The gap grows in proportion to the number")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "gap_vs_magnitude.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
