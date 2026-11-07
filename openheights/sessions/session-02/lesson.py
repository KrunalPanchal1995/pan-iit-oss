"""Session 2 (Level 2): two angles when the base is out of reach, and how errors spread.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: two readings, and how wrong can the height be?
# **A. Real-world problem.** A moat, a fence or a river stops you reaching the base of the tower,
# so you do not know the distance `d`. And your phone clinometer is only good to about half a
# degree. Where should you stand so that a 30 m tower is measured to within 0.5 m?
#
# **Plan.** (1) height from two angles at two spots, (2) propagate the angle error into a height
# error, (3) turn the error formula into a design rule.

# %%
import pathlib
import math

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
EYE = 1.6


def cot(deg):
    return 1.0 / math.tan(math.radians(deg))


# %% [markdown]
# ## Step 1: two angles, one baseline
# Read angle `a1` at a far spot, walk `b` metres straight towards the tower, read `a2`. With
# `x` the unknown horizontal distance from the near spot to the base, and H the height above eye:
#
#     x = H cot(a2)   and   x + b = H cot(a1)   so   H = b / (cot(a1) - cot(a2))

# %%
def height_two_angles(b, a1_deg, a2_deg, eye=EYE):
    """Total height (m). a1 is the FAR reading (smaller), a2 the NEAR reading (larger), b the walk (m)."""
    if not 0 < a1_deg < a2_deg < 90:
        raise ValueError("need 0 < a1 < a2 < 90 degrees (far reading smaller than near reading)")
    return b / (cot(a1_deg) - cot(a2_deg)) + eye


def distance_to_base(b, a1_deg, a2_deg):
    """Horizontal distance (m) from the near spot to the base, found as a by-product."""
    return b * cot(a2_deg) / (cot(a1_deg) - cot(a2_deg))


# %% [markdown]
# ## Step 2: error propagation
# If the true height above the eye is H = d tan(theta), a reading error `dtheta` (in radians)
# changes it by about  dH = d sec^2(theta) dtheta,  and since d = H / tan(theta):
#
#     dH = 2 H dtheta / sin(2 theta)
#
# This is smallest at theta = 45 degrees (sin 2theta = 1) and grows fast at small and large angles.

# %%
def height_error(d, angle_deg, sigma_deg):
    """First-order height error (m): d * sec^2(theta) * sigma, with sigma converted to radians."""
    return d / math.cos(math.radians(angle_deg)) ** 2 * math.radians(sigma_deg)


def best_window(h_above_eye, sigma_deg, tol):
    """Distances (m) between which the first-order error stays within tol, or None if never.

    From 2 H sigma / sin(2 theta) <= tol:  sin(2 theta) >= 2 H sigma / tol.
    """
    s = 2 * h_above_eye * math.radians(sigma_deg) / tol
    if s > 1 + 1e-12:
        return None
    s = min(s, 1.0)
    th_lo = 0.5 * math.asin(s)
    th_hi = math.pi / 2 - th_lo
    return h_above_eye / math.tan(th_hi), h_above_eye / math.tan(th_lo)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    H = 28.4          # 30 m tower, eye at 1.6 m
    sig = 0.5         # degrees
    print("window for 0.5 m:", best_window(H, sig, 0.5))
    for d in (10, 20, 28.4, 40, 60, 100):
        th = math.degrees(math.atan(H / d))
        print(f"d = {d:5.1f} m  angle {th:5.1f} deg  error {height_error(d, th, sig):.3f} m")

    d = np.linspace(5, 100, 300)
    th = np.degrees(np.arctan(H / d))
    err = d / np.cos(np.radians(th)) ** 2 * math.radians(sig)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(d, err, label="height error d sec^2(theta) sigma")
    ax.axhline(0.5, color="red", ls="--", label="0.5 m target")
    lo, hi = best_window(H, sig, 0.5)
    ax.axvspan(lo, hi, color="green", alpha=0.2, label=f"stand {lo:.1f} to {hi:.1f} m away")
    ax.set_ylim(0, 3)
    ax.set_xlabel("distance from the base (m)")
    ax.set_ylabel("height error (m)")
    ax.set_title("Where to stand: 30 m tower, reading good to 0.5 degrees")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "error_vs_distance.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    ax2.plot([0, 40], [0, 0], "k-")
    ax2.plot([0, 0], [0, 30], lw=4, color="tab:blue", label="tower 30 m")
    for x, name in ((40, "far spot, a1"), (30, "near spot, a2")):
        ax2.plot([x, 0], [1.6, 30], "--", color="orange")
        ax2.plot([x], [1.6], "ro")
        ax2.annotate(name, (x, 4), ha="center", fontsize=8)
    ax2.set_xlabel("distance from the tower base (m)")
    ax2.set_ylabel("height (m)")
    ax2.set_title("Two readings, walk b = 10 m towards the tower")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "two_angle_geometry.png", dpi=120)

# %% [markdown]
# ## Where this stops
# These error formulas assume a small, random reading error and a level surface. Session 3 tests
# them with a simulation, adds a hill, and shows what happens near 90 degrees.
