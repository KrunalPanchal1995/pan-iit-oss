"""Session 1 (Level 1): the pinhole camera and parallax, two views give depth.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: where a 3D point lands, and why two cameras give depth
# **A. Real-world problem.** Close one eye and hold a finger at arm's length, then switch eyes:
# the finger jumps sideways against the background. The jump is large for near things and small
# for far things. Engineers use the same effect, with two cameras, to measure the shape of a
# loaded rubber strip or a bridge cable without touching it.
#
# **Plan.** (1) write the pinhole camera rule, (2) put two cameras side by side, (3) find the
# sideways jump (the *disparity*), (4) turn the jump back into depth, (5) see why far things are
# hard to measure.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

F = 1000.0      # focal length measured in pixels (how far the pinhole is from the sensor, in pixel widths)
BASE = 0.04     # distance between the two cameras in metres


# %% [markdown]
# ## Step 1: the pinhole camera
# Light from a point (X, Y, Z) passes through a tiny hole and lands on a sensor a distance f
# behind it. By similar triangles, the landing place is
#
#     u = f * X / Z        v = f * Y / Z
#
# X is sideways, Y is up, Z is the distance in front of the camera, all in metres. Because f is
# counted in pixels, u and v come out in pixels measured from the middle of the image.
# Check by hand: f = 1000 px, a point at X = 0.02 m, Z = 0.5 m lands at u = 1000 * 0.02 / 0.5 = 40 px.

# %%
def project(point, f=F):
    """Pixel coordinates (u, v), measured from the image centre, of a 3D point (X, Y, Z) in metres."""
    X, Y, Z = point
    if Z <= 0:
        raise ValueError("the point must be in front of the camera (Z > 0)")
    return f * X / Z, f * Y / Z


# %% [markdown]
# ## Step 2: two cameras side by side
# Put camera 2 a distance B (the *baseline*) to the right of camera 1, both looking straight ahead.
# For camera 2 the point is B closer to the left, so its sideways distance is X - B:
#
#     u1 = f * X / Z        u2 = f * (X - B) / Z
#
# The sideways jump between the two pictures is the **disparity** d = u1 - u2 = f * B / Z.
# It does not depend on X at all: only on the depth Z. That is why two views give depth.

# %%
def stereo_project(point, f=F, baseline=BASE):
    """Return ((u1, v), (u2, v)) for camera 1 at x = 0 and camera 2 at x = baseline."""
    X, Y, Z = point
    return project((X, Y, Z), f), project((X - baseline, Y, Z), f)


def disparity(point, f=F, baseline=BASE):
    (u1, _), (u2, _) = stereo_project(point, f, baseline)
    return u1 - u2


# %% [markdown]
# ## Step 3: from disparity back to depth
# Turn d = f B / Z around: **Z = f B / d**. Measure the jump in pixels, and the depth follows.
# Example: f = 1000 px, B = 0.04 m, d = 80 px gives Z = 1000 * 0.04 / 80 = 0.5 m.

# %%
def depth_from_disparity(d, f=F, baseline=BASE):
    """Depth in metres from a disparity in pixels. A disparity of zero or less means 'infinitely far' (returns inf)."""
    d = np.asarray(d, dtype=float)
    with np.errstate(divide="ignore"):
        z = np.where(d > 0, f * baseline / np.where(d > 0, d, 1.0), np.inf)
    return float(z) if z.ndim == 0 else z


# %% [markdown]
# ## Step 4: why far things are hard
# Disparity is measured in whole pixels at best (Session 2 does better). Neighbouring disparities
# d and d + 1 pixel correspond to depths f B / d and f B / (d + 1). The gap between them is the
# depth step the cameras cannot resolve. It grows rapidly with distance.

# %%
def depth_step(Z, f=F, baseline=BASE):
    """Depth change in metres caused by a 1 pixel change of disparity, for a point at depth Z."""
    d = f * baseline / Z
    return f * baseline / d - f * baseline / (d + 1.0)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    p = (0.02, 0.01, 0.5)
    (u1, v1), (u2, v2) = stereo_project(p)
    print(f"point {p}: camera 1 sees ({u1:.1f}, {v1:.1f}) px, camera 2 sees ({u2:.1f}, {v2:.1f}) px")
    print(f"disparity {disparity(p):.1f} px  ->  depth {depth_from_disparity(disparity(p)):.3f} m")
    for Z in (0.3, 0.5, 1.0, 2.0, 5.0):
        print(f"Z = {Z:4.1f} m: disparity {F * BASE / Z:6.1f} px, one pixel of disparity = {1000 * depth_step(Z):8.2f} mm of depth")

    # top view: two cameras, three points at different depths
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    for x, name in ((0.0, "camera 1"), (BASE, "camera 2")):
        ax.plot([x], [0], "ks", ms=8)
        ax.annotate(name, (x, 0), textcoords="offset points", xytext=(-6 if x == 0 else 6, -16), ha="right" if x == 0 else "left", fontsize=8)
    for Z, col in ((0.3, "tab:red"), (0.6, "tab:orange"), (1.2, "tab:green")):
        X = 0.02
        ax.plot([X], [Z], "o", color=col)
        ax.plot([0, X], [0, Z], "-", color=col, lw=0.8)
        ax.plot([BASE, X], [0, Z], "--", color=col, lw=0.8)
        ax.annotate(f"Z = {Z} m, disparity {F * BASE / Z:.0f} px", (X, Z), textcoords="offset points", xytext=(8, 0), fontsize=8)
    ax.set_xlabel("sideways position X (m)")
    ax.set_ylabel("depth Z (m)")
    ax.set_title("Top view: nearer points are seen at more different angles")
    ax.set_xlim(-0.04, 0.16)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "top_view.png", dpi=120)

    Z = np.linspace(0.25, 3.0, 200)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(Z, F * BASE / Z, label="d = f B / Z  (f = 1000 px, B = 0.04 m)")
    ax2.plot([0.5, 1.0, 2.0], [F * BASE / z for z in (0.5, 1.0, 2.0)], "ro")
    ax2.set_xlabel("depth Z (m)")
    ax2.set_ylabel("disparity d (pixels)")
    ax2.set_title("Disparity falls as 1/Z: depth is easier to measure up close")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "disparity_vs_depth.png", dpi=120)

# %% [markdown]
# ## Where this stops
# We assumed two identical cameras, perfectly parallel, with known f and B. Session 2 handles
# real pixels, sub-pixel matching and the accuracy of the result.
