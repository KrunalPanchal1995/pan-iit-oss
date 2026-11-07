"""Session 1 (Level 1): no part is made exactly, so we give it limits.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: no part is made exactly
# **A. Real-world problem.** A shaft that is a little too big will not go into a hole that is
# a little too small. No machine makes a part exactly 10.000 mm; every part is a bit bigger or
# smaller. *Tolerance* is the wiggle we agree to allow. Today you write a part's limits, find
# its tolerance, and decide whether a pin and a hole will assemble.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: limits and tolerance
# A drawing gives a part two **limits**: the largest allowed size (upper limit) and the smallest
# allowed size (lower limit). The **tolerance** is the difference:
#
#     tolerance = upper limit - lower limit
#
# A part is *in tolerance* if its measured size is between the two limits (inclusive).

# %%
def tolerance(lower, upper):
    """Tolerance = upper limit - lower limit (same unit as the inputs)."""
    if upper < lower:
        raise ValueError("upper limit must not be below the lower limit")
    return round(upper - lower, 9)


def in_limits(size, lower, upper):
    """True if a measured size is inside the limits (the limits themselves are allowed)."""
    return lower - 1e-9 <= size <= upper + 1e-9


# %% [markdown]
# ## Step 2: a pin and a hole (all sizes in mm)
# Our pin is *nominal* 10 mm but is specified as at most 9.98 mm and at least `9.98 - tol`.
# The hole is at least 10.00 mm and at most `10.00 + tol`. The gap between hole and pin is the
# **clearance** = hole size - pin size. Negative clearance means the pin is bigger than the
# hole: that is called **interference**.

# %%
PIN_UPPER = 9.98
HOLE_LOWER = 10.00


def pin_limits(tol):
    return round(PIN_UPPER - tol, 9), PIN_UPPER


def hole_limits(tol):
    return HOLE_LOWER, round(HOLE_LOWER + tol, 9)


def clearance(hole_size, pin_size):
    return round(hole_size - pin_size, 9)


def kind_of_fit(c):
    if c > 1e-9:
        return "clearance"
    if c < -1e-9:
        return "interference"
    return "line to line"


# %% [markdown]
# ## Step 3: the worst cases
# The *smallest* possible clearance happens with the biggest pin in the smallest hole; the
# *largest* with the smallest pin in the biggest hole:
#
#     min clearance = hole lower limit - pin upper limit
#     max clearance = hole upper limit - pin lower limit

# %%
def clearance_range(tol):
    h_lo, h_hi = hole_limits(tol)
    p_lo, p_hi = pin_limits(tol)
    return clearance(h_lo, p_hi), clearance(h_hi, p_lo)


def always_assembles(tol):
    """True if every pin and hole inside their limits will go together."""
    return clearance_range(tol)[0] >= 0


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    tol = 0.05
    h_lo, h_hi = hole_limits(tol)
    p_lo, p_hi = pin_limits(tol)
    cmin, cmax = clearance_range(tol)
    print(f"hole {h_lo:.2f} to {h_hi:.2f} mm, pin {p_lo:.2f} to {p_hi:.2f} mm")
    print(f"tolerance {tolerance(p_lo, p_hi):.2f} mm; clearance {cmin:.2f} to {cmax:.2f} mm")

    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.barh(1, h_hi - h_lo, left=h_lo, height=0.5, color="tab:blue", alpha=0.6, label="hole: allowed sizes")
    ax.barh(0, p_hi - p_lo, left=p_lo, height=0.5, color="tab:orange", alpha=0.7, label="pin: allowed sizes")
    ax.axvline(10.0, color="k", ls=":", lw=1)
    ax.annotate("", xy=(h_lo, 0.5), xytext=(p_hi, 0.5), arrowprops=dict(arrowstyle="<->", color="green"))
    ax.text((h_lo + p_hi) / 2, 0.58, f"min clearance {cmin:.2f}", ha="center", fontsize=8, color="green")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["pin", "hole"])
    ax.set_xlabel("diameter (mm)")
    ax.set_title("Limits of a pin and a hole (tolerance 0.05 mm each)")
    ax.legend(fontsize=8, loc="upper center")
    ax.grid(alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(OUT / "limits_picture.png", dpi=120)

    tols = np.linspace(0.0, 0.2, 41)
    ranges = np.array([clearance_range(t) for t in tols])
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.fill_between(tols, ranges[:, 0], ranges[:, 1], alpha=0.3, label="possible clearances")
    ax2.plot(tols, ranges[:, 0], label="minimum clearance")
    ax2.plot(tols, ranges[:, 1], label="maximum clearance")
    ax2.set_xlabel("tolerance of each part (mm)")
    ax2.set_ylabel("clearance (mm)")
    ax2.set_title("Looser tolerance, wider spread of clearance")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "clearance_vs_tol.png", dpi=120)
    for t in (0.02, 0.05, 0.10):
        print(f"tol {t:.2f}: clearance {clearance_range(t)[0]:.2f} to {clearance_range(t)[1]:.2f} mm")

# %% [markdown]
# ## Where this stops
# Here the pin and hole limits were chosen by hand. Session 2 uses the standard ISO fit system
# (such as 25 H7/g6) so that engineers everywhere choose the limits in the same way.
