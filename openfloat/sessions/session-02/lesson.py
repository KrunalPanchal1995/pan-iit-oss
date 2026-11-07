"""Session 2 (Level 2): IEEE 754 double precision, rounding and cancellation.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the 64-bit format, rounding error and cancellation
# **A. Real-world problem.** A physicist computes 1 - cos(angle) for a tiny angle and gets
# exactly 0. An engineer solves a quadratic equation and one of the two roots has few correct
# digits. Nothing is broken in the computer: the formulas lose digits. We learn how the
# 64-bit format stores a number, how big the rounding error is, and which formulas to avoid.
#
# **Plan.** (1) decode the 64 bits, (2) measure machine epsilon, (3) see cancellation in the
# quadratic formula and in 1 - cos, (4) meet overflow and underflow.

# %%
import pathlib
from decimal import Decimal, getcontext

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: 1 sign bit, 11 exponent bits, 52 fraction bits
# A normal 64-bit number is stored as (-1)^s * (1 + f / 2^52) * 2^(e - 1023), where s is the
# sign bit, e the 11-bit exponent field (1 to 2046) and f the 52-bit fraction field. The leading
# 1 is not stored. We read the bits by viewing the same 8 bytes as an integer.

# %%
def decode(x):
    """Return (sign, exponent_field, fraction_field) of the 64-bit float x."""
    bits = int(np.array([x], dtype=np.float64).view(np.uint64)[0])
    return bits >> 63, (bits >> 52) & 0x7FF, bits & ((1 << 52) - 1)


def encode_value(s, e, f):
    """Value of a normal number from its three fields."""
    return (-1.0) ** s * (1.0 + f / 2.0 ** 52) * 2.0 ** (e - 1023)


def machine_epsilon():
    """Gap between 1 and the next float: 2^-52."""
    return float(np.finfo(np.float64).eps)


def rel_error(approx, exact):
    return abs(approx - exact) / abs(exact)


# %% [markdown]
# ## Step 2: rounding and cancellation
# Every operation rounds to the nearest stored number, so the result has a relative error of
# at most u = 2^-53 (about 1.1e-16), half of machine epsilon. This is tiny, but it can be
# magnified when two nearly equal numbers are subtracted: the leading digits cancel and what
# is left is mostly old rounding noise. `small_root_exact` uses 60-digit decimal arithmetic as
# a trusted reference.

# %%
getcontext().prec = 60


def small_root_exact(b, c):
    """Smaller root of x^2 - b x + c = 0 (b > 0), in 60-digit decimal arithmetic."""
    B, C = Decimal(float(b)), Decimal(float(c))
    return (B - (B * B - 4 * C).sqrt()) / 2


def roots_naive(b, c):
    """Textbook formula for x^2 - b x + c = 0 with b > 0: (b -/+ sqrt(b^2 - 4c)) / 2."""
    d = np.sqrt(b * b - 4.0 * c)
    return (b + d) / 2.0, (b - d) / 2.0          # (large root, small root)


def roots_stable(b, c):
    """Add the two like-signed terms first, then use x1 * x2 = c for the other root."""
    d = np.sqrt(b * b - 4.0 * c)
    big = (b + d) / 2.0
    return big, c / big


def one_minus_cos_naive(theta):
    return 1.0 - np.cos(theta)


def one_minus_cos_stable(theta):
    """Same quantity from the identity 1 - cos t = 2 sin^2(t / 2): no subtraction."""
    return 2.0 * np.sin(theta / 2.0) ** 2


# %% [markdown]
# ## Step 3: overflow and underflow
# The exponent field limits the range: the largest finite double is about 1.8e308 and the
# smallest positive normal one about 2.2e-308. Beyond the top you get `inf` (overflow); below
# the bottom, numbers lose digits ("subnormals") and finally become 0 (underflow).

# %%
def float_limits():
    fi = np.finfo(np.float64)
    return float(fi.max), float(fi.tiny), float(np.nextafter(0.0, 1.0))


def length_naive(x, y):
    with np.errstate(over="ignore"):
        return float(np.sqrt(x * x + y * y))


def length_safe(x, y):
    """Scale by the larger value first so that no square overflows."""
    m = max(abs(x), abs(y))
    if m == 0.0:
        return 0.0
    return float(m * np.sqrt((x / m) ** 2 + (y / m) ** 2))


# %% [markdown]
# ## Step 4: see it
# Left: relative error of the small root of x^2 - b x + 1 = 0 for the naive and stable formulas
# as b grows. Right: the error of 1 - cos for small angles.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for x in (1.0, -6.5, 0.1):
        s, e, f = decode(x)
        print(f"{x:5}: sign {s}, exponent field {e} (true exponent {e - 1023}), fraction {f:013x} hex")
    print("machine epsilon (numpy):", machine_epsilon())
    for b in (1e2, 1e4, 1e6, 1e8):
        ex = float(small_root_exact(b, 1.0))
        print(f"b={b:.0e}: naive error {rel_error(roots_naive(b, 1.0)[1], ex):.1e}, "
              f"stable error {rel_error(roots_stable(b, 1.0)[1], ex):.1e}")
    for t in (1e-2, 1e-6, 1e-8):
        print(f"theta={t:.0e}: naive 1-cos {one_minus_cos_naive(t):.4e}, stable {one_minus_cos_stable(t):.4e}")
    print("limits (max, smallest normal, smallest subnormal):", float_limits())
    print("length of (3e200, 4e200): naive", length_naive(3e200, 4e200), ", safe", length_safe(3e200, 4e200))

    bs = np.logspace(0.5, 8, 60)
    en = np.array([max(rel_error(roots_naive(b, 1.0)[1], float(small_root_exact(b, 1.0))), 1e-17) for b in bs])
    es = np.array([max(rel_error(roots_stable(b, 1.0)[1], float(small_root_exact(b, 1.0))), 1e-17) for b in bs])
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.loglog(bs, en, label="textbook formula")
    ax.loglog(bs, es, label="stable formula")
    ax.axhline(2.0 ** -53, color="gray", ls=":", label="u = 2^-53")
    ax.set_xlabel("coefficient b (no unit)")
    ax.set_ylabel("relative error of the small root (floor 1e-17)")
    ax.set_title("Small root of x^2 - b x + 1 = 0")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "quadratic_error.png", dpi=120)

    th = np.logspace(-9, -1, 60)
    ref = 2 * np.sin(th / 2) ** 2
    err = np.maximum(np.abs(one_minus_cos_naive(th) - ref) / ref, 1e-17)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.loglog(th, err, label="1 - cos(theta)")
    ax2.set_xlabel("angle theta (radians)")
    ax2.set_ylabel("relative error (floor 1e-17)")
    ax2.set_title("Subtracting nearly equal numbers destroys digits")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "one_minus_cos_error.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
