"""Session 1 (Level 1): a shape described by a function (signed distance).

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a shape is a function
# **A. Real-world problem.** CAD software has to answer one question millions of times: "is
# this point inside the part?" A mug is not stored as a picture. It can be stored as a
# *function*: give it any point in space and it returns one number, the distance from that
# point to the surface of the mug, **negative if the point is inside**. Today we do it in 2D
# with a circle and a box, and draw the numbers as pictures.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the circle and the box
# A point `p = (x, y)`. For a circle with centre `c` and radius `r`, the distance from `p` to the
# edge is `|p - c| - r`: positive outside, zero on the edge, negative inside (the most negative
# value, `-r`, is at the centre).
#
# For a box with centre `c` and half-sizes `(a, b)`, let `q = |p - c| - (a, b)` (per coordinate).
# If both parts of `q` are negative the point is inside, and the distance to the nearest side
# is `max(q)`. Otherwise it is outside, and the distance is the length of the positive parts of `q`.

# %%
def sd_circle(p, c, r):
    """Signed distance from points p (shape (..., 2)) to a circle of centre c and radius r."""
    p = np.asarray(p, dtype=float)
    return np.linalg.norm(p - np.asarray(c, dtype=float), axis=-1) - r


def sd_box(p, c, half):
    """Signed distance from points p (shape (..., 2)) to a box with centre c and half-sizes half."""
    q = np.abs(np.asarray(p, dtype=float) - np.asarray(c, dtype=float)) - np.asarray(half, dtype=float)
    outside = np.linalg.norm(np.maximum(q, 0.0), axis=-1)
    inside = np.minimum(np.max(q, axis=-1), 0.0)
    return outside + inside


def sd_round_box(p, c, half, r):
    """Signed distance to a box with rounded corners: the box distance reduced by the radius r.

    The box with half-sizes `half` is the core, so the rounded shape reaches r beyond it on every side."""
    return sd_box(p, c, half) - r


def sd_capsule(p, a, b, r):
    """Signed distance from points p (shape (..., 2)) to a capsule: segment a-b grown by radius r."""
    p = np.asarray(p, dtype=float)
    a = np.asarray(a, dtype=float)
    ba = np.asarray(b, dtype=float) - a
    pa = p - a
    # the closest point on the segment is at fraction h of the way from a to b, clamped to the ends
    h = np.clip(np.sum(pa * ba, axis=-1) / max(float(np.dot(ba, ba)), 1e-12), 0.0, 1.0)
    return np.linalg.norm(pa - np.asarray(h)[..., None] * ba, axis=-1) - r


# %% [markdown]
# ## Step 2: join two shapes, and turn numbers into a picture
# A point is in the *union* of two shapes when it is inside at least one of them, so we take the
# smaller of the two numbers: `min(d1, d2)`. To draw a shape we evaluate the function on a grid
# of points and colour each cell by its sign.

# %%
def union(d1, d2):
    return np.minimum(d1, d2)


def make_grid(xlim, ylim, n):
    """n by n cell centres over the rectangle; returns the points with shape (n, n, 2)."""
    x = xlim[0] + (np.arange(n) + 0.5) * (xlim[1] - xlim[0]) / n
    y = ylim[0] + (np.arange(n) + 0.5) * (ylim[1] - ylim[0]) / n
    X, Y = np.meshgrid(x, y)
    return np.stack([X, Y], axis=-1)


def inside_fraction(f, xlim, ylim, n):
    """Fraction of grid cells whose centre is inside the shape (f < 0)."""
    return float(np.mean(f(make_grid(xlim, ylim, n)) < 0))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    xlim, ylim = (-2.0, 3.5), (-1.5, 1.5)
    P = make_grid(xlim, ylim, 300)
    circle = sd_circle(P, (0, 0), 1.0)
    box = sd_box(P, (2.0, 0.0), (0.5, 0.5))
    both = union(circle, box)

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.4))
    for ax, d, name in zip(axes, [circle, box, both], ["circle: |p - c| - r", "box", "union = min(circle, box)"]):
        im = ax.imshow(d, extent=[*xlim, *ylim], origin="lower", cmap="RdBu", vmin=-1.5, vmax=1.5)
        ax.contour(P[..., 0], P[..., 1], d, levels=[0.0], colors="k", linewidths=2)
        ax.set_title(name)
        ax.set_xlabel("x (units)")
    axes[0].set_ylabel("y (units)")
    fig.colorbar(im, ax=axes, label="signed distance (units): blue negative = inside", shrink=0.85)
    fig.savefig(OUT / "sdf_pictures.png", dpi=110, bbox_inches="tight")

    x = np.linspace(-2.0, 3.5, 400)
    line = np.stack([x, np.full_like(x, 0.3)], axis=-1)
    fig2, ax2 = plt.subplots(figsize=(6.5, 3.8))
    ax2.plot(x, sd_circle(line, (0, 0), 1.0), label="circle")
    ax2.plot(x, sd_box(line, (2.0, 0.0), (0.5, 0.5)), label="box")
    ax2.plot(x, union(sd_circle(line, (0, 0), 1.0), sd_box(line, (2.0, 0.0), (0.5, 0.5))), "k--", label="union (min)")
    ax2.axhline(0, color="gray", lw=1)
    ax2.set_xlabel("x along the line y = 0.3 (units)")
    ax2.set_ylabel("signed distance (units)")
    ax2.set_title("Where a curve is below zero, the point is inside")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "sdf_profile.png", dpi=120)

    # the same grid and colour scale as the first figure, for the two new shapes
    fig3, axes3 = plt.subplots(1, 2, figsize=(8, 3.4))
    shapes3 = [sd_round_box(P, (2.0, 0.0), (0.5, 0.5), 0.3), sd_capsule(P, (-1.5, 0.0), (-0.5, 0.0), 0.5)]
    for ax, d, name in zip(axes3, shapes3, ["rounded box: box distance - r", "capsule: segment distance - r"]):
        im = ax.imshow(d, extent=[*xlim, *ylim], origin="lower", cmap="RdBu", vmin=-1.5, vmax=1.5)
        ax.contour(P[..., 0], P[..., 1], d, levels=[0.0], colors="k", linewidths=2)
        ax.set_title(name)
        ax.set_xlabel("x (units)")
    axes3[0].set_ylabel("y (units)")
    fig3.colorbar(im, ax=axes3, label="signed distance (units): blue negative = inside", shrink=0.85)
    fig3.savefig(OUT / "sdf_rounded_capsule.png", dpi=110, bbox_inches="tight")

    frac = inside_fraction(lambda q: sd_circle(q, (0, 0), 1.0), (-1.5, 1.5), (-1.5, 1.5), 300)
    print("circle area by counting:", round(frac * 9.0, 4), " exact pi r^2 =", round(np.pi, 4))
    p = np.array([1.2, 0.3])
    print("worked example: circle", round(float(sd_circle(p, (0, 0), 1.0)), 3),
          " box", round(float(sd_box(p, (2.0, 0.0), (0.5, 0.5))), 3),
          " union", round(float(union(sd_circle(p, (0, 0), 1.0), sd_box(p, (2.0, 0.0), (0.5, 0.5)))), 3))

# %% [markdown]
# ## Where this stops
# We only measured distances and joined two shapes. Session 2 adds cutting (subtraction), smooth
# blending and a parametric mug cross-section you can resize.
