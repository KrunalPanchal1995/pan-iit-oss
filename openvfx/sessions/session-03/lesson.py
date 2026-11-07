"""Session 3 (Level 3): put skin on the bones (linear blend skinning) and measure it.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: skin that follows the bones
# **A. Real-world problem.** A skeleton has no surface. The skin is a cloud of points and each
# point must decide which bone to follow. Follow one bone and the elbow cracks open like a
# robot. Follow a weighted blend of two bones and it looks like flesh, but the elbow gets
# thinner. This is *linear blend skinning* (LBS), used in almost every game engine. Today you
# build it, measure both defects, and check the thinning against a hand calculation.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
ELBOW = np.array([1.0, 0.0])      # the joint, at the middle of a 2 unit long arm
HALF = 0.15                       # half the arm thickness


# %% [markdown]
# ## Step 1: the skin in the rest pose
# Two rows of 41 points: the top edge and the bottom edge of a straight arm.

# %%
def rest_mesh(n=41):
    x = np.linspace(0.0, 2.0, n)
    top = np.stack([x, np.full(n, HALF)], axis=1)
    bottom = np.stack([x, np.full(n, -HALF)], axis=1)
    return top, bottom


# %% [markdown]
# ## Step 2: where each bone would put a point, and the weights
# Bone 1 stays put. Bone 2 turns by `bend` about the elbow (Session 2's rotate-about-a-joint).
# A weight `w` between 0 and 1 says how much a point follows bone 2:
#
#     new point = (1 - w) * (where bone 1 puts it) + w * (where bone 2 puts it)

# %%
def bone2_position(points, bend):
    c, s = np.cos(bend), np.sin(bend)
    r = np.array([[c, -s], [s, c]])
    return (points - ELBOW) @ r.T + ELBOW


def rigid_weights(x):
    """Each point follows exactly one bone: the cracked-joint look."""
    return (x >= ELBOW[0]).astype(float)


def smooth_weights(x, zone=0.3):
    """Blend between bones over a zone of half-width `zone` around the elbow (smoothstep)."""
    t = np.clip((x - (ELBOW[0] - zone)) / (2 * zone), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def skin(points, weights, bend):
    w = weights[:, None]
    return (1 - w) * points + w * bone2_position(points, bend)


def pose(weight_fn, bend):
    """Top and bottom skin edges for a bend angle (radians). weight_fn maps x to weights."""
    top, bottom = rest_mesh()
    w = weight_fn(top[:, 0])
    return skin(top, w, bend), skin(bottom, w, bend)


def lbs_pose(bend, zone=0.3):
    """Blended skin with an adjustable blend zone (use this to try different zones)."""
    return pose(lambda x: smooth_weights(x, zone), bend)


# %% [markdown]
# ## Step 3: measure the two defects
# * **Crack** = the largest gap between neighbouring points along an edge. Rest gap is 0.05.
# * **Thinning** = the elbow width divided by the rest width (0.30). 1.0 means no thinning.
#
# Hand calculation for the blended elbow (weight 1/2) at bend `b`: the top and bottom points
# end up 0.30 * cos(b/2) apart, so **thinning ratio = cos(b/2)**. At 90 degrees that is
# cos(45 degrees) = 0.707.

# %%
def max_gap(edge):
    return float(np.linalg.norm(np.diff(edge, axis=0), axis=1).max())


def elbow_width_ratio(top, bottom):
    width = np.linalg.norm(top - bottom, axis=1)
    return float(width.min() / (2 * HALF))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    bend = np.radians(90)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.5), sharey=True)
    for ax, (name, fn) in zip(axes, [("rigid (one bone each)", rigid_weights), ("blended (LBS)", smooth_weights)]):
        top, bottom = pose(fn, bend)
        ax.fill(np.r_[top[:, 0], bottom[::-1, 0]], np.r_[top[:, 1], bottom[::-1, 1]], alpha=0.4)
        ax.plot(top[:, 0], top[:, 1], "k.", ms=3)
        ax.plot(bottom[:, 0], bottom[:, 1], "k.", ms=3)
        gap = max(max_gap(top), max_gap(bottom))
        ratio = elbow_width_ratio(top, bottom)
        ax.set_title(f"{name}\nlargest gap {gap:.3f}, elbow width {ratio:.0%} of rest")
        ax.set_aspect("equal")
        ax.grid(alpha=0.3)
        ax.set_xlabel("x (units)")
        print(f"{name:22s} largest gap {gap:.3f}   elbow width ratio {ratio:.3f}")
    axes[0].set_ylabel("y (units)")
    fig.tight_layout()
    fig.savefig(OUT / "skinning_90deg.png", dpi=120)

    bends = np.radians(np.arange(0, 151, 5))
    measured = [elbow_width_ratio(*lbs_pose(b)) for b in bends]
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(np.degrees(bends), measured, "o", ms=4, label="measured from the mesh")
    ax2.plot(np.degrees(bends), np.cos(bends / 2), "-", label="hand calculation cos(b/2)")
    ax2.axhline(1.0, color="gray", ls=":", label="rigid skin (no thinning, but cracks)")
    ax2.axhline(0.8, color="red", ls="--", label="80% limit")
    ax2.set_xlabel("elbow bend (degrees)")
    ax2.set_ylabel("elbow width / rest width")
    ax2.set_title("Blended skin thins as the elbow bends")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "width_vs_bend.png", dpi=120)
    for zone in (0.1, 0.2, 0.3, 0.4):
        top, bottom = lbs_pose(bend, zone)
        print(f"blend zone {zone}: largest gap {max(max_gap(top), max_gap(bottom)):.3f}")

# %% [markdown]
# ## Where this stops
# Thinning of 30% at 90 degrees is why real characters use extra "helper" bones and better
# blending. That is the road to the Target: see `promo/roadmap.md`.
