"""Session 3 (Level 3): accumulated rounding error, Patriot and Ariane 5.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: when small errors add up, and when a number does not fit
# **A. Real-world problem.** Two famous failures involved no exotic mathematics. In 1991 a
# Patriot battery's clock was counted in tenths of a second, and 0.1 cannot be stored exactly in
# binary, so a tiny error was added every tick for days. In 1996 the first Ariane 5 flight was
# lost after a software exception when a 64-bit floating point value was converted to a 16-bit
# signed integer that was too small to hold it. We reproduce both mechanisms as calculations,
# and measure how summation errors grow and how to shrink them.
#
# **Plan.** (1) sum 0.1 ten million times three ways, (2) compare with the error bound,
# (3) reproduce the Patriot clock drift, (4) show integer wrap-around and range checks.
# This is a simplified educational model of the mechanisms, not an account of either system.

# %%
import math
import pathlib
from fractions import Fraction

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

U = 2.0 ** -53          # unit round-off of a 64-bit float


# %% [markdown]
# ## Step 1: three ways to add the same numbers
# Naive summation adds one number at a time; each addition rounds. Kahan (compensated)
# summation keeps a second number `c` holding what was lost in the last addition and feeds it
# back in. `math.fsum` tracks the exact partial sums and rounds only once at the end.
# The exact reference for n copies of the stored double 0.1 is n times its exact value.

# %%
def exact_repeat_sum(x, n):
    """Correctly rounded value of x added n times (exact rational arithmetic)."""
    return float(n * Fraction(x))


def naive_running(x, n):
    """Running naive sums of n copies of x (sequential, left to right)."""
    return np.cumsum(np.full(n, x))


def kahan_sum(values):
    """Kahan compensated sum of an iterable of floats."""
    s = 0.0
    c = 0.0
    for v in values:
        y = v - c
        t = s + y
        c = (t - s) - y
        s = t
    return s


def kahan_error_trace(x, n, checkpoints):
    """Error of the Kahan running sum of n copies of x, recorded at the given counts."""
    marks = set(int(k) for k in checkpoints)
    s = 0.0
    c = 0.0
    out = {}
    for i in range(1, n + 1):
        y = x - c
        t = s + y
        c = (t - s) - y
        s = t
        if i in marks:
            out[i] = abs(s - exact_repeat_sum(x, i))
    return out


def naive_bound(n, total_abs):
    """Standard worst-case bound for recursive summation: (n - 1) * u * sum |x_i|."""
    return (n - 1) * U * total_abs


# %% [markdown]
# ## Step 2: the Patriot clock as a calculation
# The clock counted ticks of 0.1 s. In binary 0.1 = 0.0001100110011... forever. A fixed-point
# register that keeps `nbits` places after the binary point chops the rest off. The commonly
# cited layout is a 24-bit register holding 23 places after the point. The chopped value is a
# little smaller than 0.1, so every tick adds a little too little time.

# %%
SCUD_SPEED = 1676.0       # m/s, a commonly cited Scud speed (about Mach 5)


def chop(x, nbits):
    """Chop the positive number x to nbits binary places after the point."""
    fx = Fraction(x)
    return Fraction(math.floor(fx * 2 ** nbits), 2 ** nbits)


def tick_error(nbits=23):
    """Error per 0.1 s tick (seconds) when 0.1 is chopped to nbits binary places."""
    return float(Fraction(1, 10) - chop(Fraction(1, 10), nbits))


def clock_drift(hours, nbits=23):
    """Accumulated clock error in seconds after `hours` hours of ticks."""
    return hours * 36000 * tick_error(nbits)


def scud_shift(drift_s, speed=SCUD_SPEED):
    """Distance (m) a target moving at `speed` covers during `drift_s` seconds."""
    return drift_s * speed


# %% [markdown]
# ## Step 3: a number that does not fit
# A 16-bit signed integer holds -32768 to 32767. Converting a larger value can wrap around
# silently (two's complement) or, in some languages, raise an exception. The safe design is
# to check the range and decide what to do (saturate, raise, flag) before converting.

# %%
INT16_MIN, INT16_MAX = -32768, 32767


def wrap_int16(x):
    """What an unchecked conversion keeps: the value modulo 65536 mapped to -32768..32767."""
    return ((int(x) + 32768) % 65536) - 32768


def checked_int16(x):
    """Convert to int16 only if it fits; otherwise raise OverflowError."""
    if not (INT16_MIN <= x <= INT16_MAX):
        raise OverflowError(f"{x} does not fit in a signed 16-bit integer")
    return int(x)


def saturate_int16(x):
    """Clamp into the 16-bit range (one common safe choice)."""
    return int(min(max(x, INT16_MIN), INT16_MAX))


# %% [markdown]
# ## Step 4: the mini-project tools
# Two calculations to audit: the variance of data with a big offset, and a vector length.

# %%
def variance_naive(x):
    """Textbook shortcut mean(x^2) - mean(x)^2 : suffers cancellation."""
    x = np.asarray(x, dtype=float)
    return float(np.mean(x * x) - np.mean(x) ** 2)


def variance_two_pass(x):
    """Subtract the mean first, then average the squares: no cancellation."""
    x = np.asarray(x, dtype=float)
    d = x - np.mean(x)
    return float(np.mean(d * d))


def norm_naive(x):
    with np.errstate(over="ignore"):
        x = np.asarray(x, dtype=float)
        return float(np.sqrt(np.sum(x * x)))


def norm_scaled(x):
    x = np.asarray(x, dtype=float)
    m = float(np.max(np.abs(x)))
    if m == 0.0:
        return 0.0
    return m * float(np.sqrt(np.sum((x / m) ** 2)))


# %% [markdown]
# ## Step 5: see it
# Left: error of the running sum of 0.1 against the number of terms, with the worst-case
# bound. Right: the Patriot clock error against hours of operation.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    n = 10_000_000
    marks = np.unique(np.logspace(1, 7, 25).astype(int))
    run = naive_running(0.1, n)
    naive_err = np.array([abs(run[k - 1] - exact_repeat_sum(0.1, int(k))) for k in marks])
    kt = kahan_error_trace(0.1, n, marks)
    kahan_err = np.array([kt[int(k)] for k in marks])
    bound = np.array([naive_bound(int(k), 0.1 * int(k)) for k in marks])
    ref = exact_repeat_sum(0.1, n)
    print(f"n = {n}: exact reference {ref!r}")
    print(f"  naive loop sum error : {abs(run[-1] - ref):.3e}")
    print(f"  Kahan sum error      : {kahan_err[-1]:.3e}")
    print(f"  math.fsum error      : {abs(math.fsum(np.full(n, 0.1)) - ref):.3e}")
    print(f"  worst-case bound     : {bound[-1]:.3e}")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.loglog(marks, np.maximum(naive_err, 1e-17), label="naive")
    ax.loglog(marks, np.maximum(kahan_err, 1e-17), label="Kahan")
    ax.loglog(marks, bound, ls="--", color="gray", label="worst-case bound (n-1) u sum|x|")
    ax.set_xlabel("number of terms n")
    ax.set_ylabel("absolute error of the sum (floor 1e-17)")
    ax.set_title("Summing 0.1 n times")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "sum_error.png", dpi=120)

    e = tick_error(23)
    print(f"Patriot: error per tick {e:.3e} s; after 100 h {clock_drift(100):.3f} s; "
          f"Scud moves {scud_shift(clock_drift(100)):.0f} m in that time")
    h = np.linspace(0, 100, 101)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(h, [clock_drift(x) for x in h])
    ax2.set_xlabel("hours since power-up (h)")
    ax2.set_ylabel("clock error (s)")
    ax2.set_title("Chopped 0.1 tick: clock error grows linearly")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "patriot_drift.png", dpi=120)

    for v in (1000.0, 32767.0, 32768.0, 40000.0):
        print(f"{v:8.0f}: wraps to {wrap_int16(v):6d}, saturates to {saturate_int16(v)}")
    a = np.array([32767], dtype=np.int16)
    with np.errstate(over="ignore"):
        print("numpy int16 32767 + 1 =", (a + np.int16(1))[0])
    data = 1e9 + np.array([4.0, 7.0, 13.0, 16.0])
    print("variance of 1e9 + [4,7,13,16]: naive", variance_naive(data), ", two-pass", variance_two_pass(data))
    print("norm of [3e200, 4e200]: naive", norm_naive([3e200, 4e200]), ", scaled", norm_scaled([3e200, 4e200]))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), run the checkpoint,
# then start the mini-project.
