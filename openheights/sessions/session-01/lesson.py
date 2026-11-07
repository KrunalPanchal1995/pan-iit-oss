"""Session 1 (Level 1): similar triangles, the shadow method and the angle of elevation.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: height from a shadow and from one angle
# **A. Real-world problem.** You cannot climb a tower or a tree with a tape measure. But you can
# stand on the ground, look up at the top, and read the angle on a phone. Two ideas turn that
# angle (or a shadow) into a height: *similar triangles* and the *tangent*.
#
# **Plan.** (1) shadow method, (2) tangent method, (3) add your eye height, (4) plot height
# against angle.

# %%
import pathlib
import math

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
EYE = 1.6   # metres: a typical eye height above the ground (an assumption you can change)


# %% [markdown]
# ## Step 1: the shadow method (similar triangles)
# At the same moment the sun makes the same angle with the ground for everything. A stick and a
# tower then form two triangles with the same shape, so their height-to-shadow ratios match:
#
#     tower_height / tower_shadow = stick_height / stick_shadow

# %%
def shadow_height(stick_height, stick_shadow, tower_shadow):
    """Height (m) of a tower from the shadow of a reference stick measured at the same moment."""
    if stick_shadow <= 0:
        raise ValueError("the stick shadow must be positive")
    return stick_height * tower_shadow / stick_shadow


# %% [markdown]
# ## Step 2: the angle of elevation
# Stand a distance `d` from the base. The angle `a` is measured from the horizontal up to the top.
# In the right triangle, tan(a) = (height above your eye) / d, so
#
#     height above eye = d * tan(a)        total height = d * tan(a) + eye height

# %%
def height_from_angle(d, angle_deg, eye=EYE):
    """Total height (m) from distance d (m, horizontal, to the base) and angle of elevation (degrees)."""
    if not 0 < angle_deg < 90:
        raise ValueError("angle of elevation must be between 0 and 90 degrees")
    return d * math.tan(math.radians(angle_deg)) + eye


def angle_for_height(d, height, eye=EYE):
    """The angle (degrees) you should read if the tower has this total height."""
    return math.degrees(math.atan2(height - eye, d))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("shadow method: stick 1.5 m, shadow 1.0 m; tower shadow 18 m ->", shadow_height(1.5, 1.0, 18.0), "m")
    print("angle method: d = 40 m, a = 35 degrees ->", round(height_from_angle(40, 35), 2), "m")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot([0, 18], [0, 0], "k-")
    ax.plot([18, 18], [0, 27], color="tab:blue", lw=4, label="tower: 27 m, shadow 18 m")
    ax.plot([18, 0], [27, 0], "--", color="orange")
    ax.plot([0, 0], [0, 1.5], color="tab:red", lw=4, label="stick: 1.5 m, shadow 1.0 m")
    ax.plot([0, 1.0], [1.5, 0], "--", color="orange")
    ax.set_aspect("equal")
    ax.set_xlabel("distance along the ground (m)")
    ax.set_ylabel("height (m)")
    ax.set_title("Similar triangles: same sun angle, same ratio")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "shadow_triangles.png", dpi=120)

    a = np.linspace(1, 80, 200)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for d in (20, 40, 60):
        ax2.plot(a, d * np.tan(np.radians(a)) + EYE, label=f"d = {d} m")
    ax2.axhline(30, color="gray", ls=":")
    ax2.set_ylim(0, 100)
    ax2.set_xlabel("angle of elevation (degrees)")
    ax2.set_ylabel("total height (m)")
    ax2.set_title("Height = d tan(angle) + 1.6 m")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "height_vs_angle.png", dpi=120)

# %% [markdown]
# ## Where this stops
# One angle needs the distance `d` to the base. If a fence or a river stops you reaching the
# base, Session 2 uses two angles instead.
