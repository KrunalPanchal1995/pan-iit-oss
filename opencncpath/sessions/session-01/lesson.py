"""Session 1 (Level 1): a cutter follows a path to carve a shape.

Educational toolpath geometry only. Real machining needs trained operators,
machine-specific post-processing and safety checks.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a cutter follows a path to carve a shape
# **A. Real-world problem.** A CNC (computer numerical control) machine moves a spinning
# cutter along a list of coordinates. A plotter moves a pen the same way. If you want a square
# pocket, where must the *centre* of the cutter go, and how long does it take?
#
# **Plan.** (1) a path is a list of points, (2) the cutter centre stays one radius inside the
# wall, (3) one lap leaves an island in the middle, (4) time = path length / feed.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: a path is a list of points
# A plotter pen goes to (x, y), then (x, y) again, and so on. The path length is the sum of
# the straight distances between neighbouring points. All lengths here are in millimetres (mm).

# %%
def polyline_length(points):
    """Total length of the straight pieces joining the points (mm)."""
    pts = np.asarray(points, dtype=float)
    return float(np.sum(np.hypot(*np.diff(pts, axis=0).T)))


def square_outline(side):
    """The wall of a square pocket, corner (0, 0) to (side, side), as a closed list of points."""
    return np.array([[0, 0], [side, 0], [side, side], [0, side], [0, 0]], dtype=float)


# %% [markdown]
# ## Step 2: the cutter centre stays one radius inside the wall
# The cutter has a radius r (half its diameter). If its edge must touch the wall, its centre
# must be r away from the wall. So the centre path is the wall moved inwards by r: a smaller
# square of side (side - 2r).

# %%
def centre_path(side, r):
    """Closed square path of the cutter centre, or None if the cutter does not fit."""
    if 2 * r > side:
        return None
    return np.array([[r, r], [side - r, r], [side - r, side - r], [r, side - r], [r, r]], dtype=float)


# %% [markdown]
# ## Step 3: one lap leaves an island
# The cutter removes material up to r on each side of its centre path. After one lap the
# strip next to the wall is clear, but a square island of side (side - 4r) may remain.

# %%
def distance_to_path(point, path):
    """Shortest distance from a point to a polyline (mm)."""
    p = np.asarray(point, dtype=float)
    best = np.inf
    for a, b in zip(path[:-1], path[1:]):
        ab = b - a
        t = 0.0 if not ab.any() else float(np.clip(np.dot(p - a, ab) / np.dot(ab, ab), 0.0, 1.0))
        best = min(best, float(np.linalg.norm(p - (a + t * ab))))
    return best


def island_side(side, r):
    """Side of the square island left after one lap (0 if none)."""
    return max(0.0, side - 4 * r)


def is_cut(point, path, r):
    """True if the cutter, following the path, touches this point."""
    return distance_to_path(point, path) <= r + 1e-9


# %% [markdown]
# ## Step 4: how long does it take?
# Feed rate F is how fast the cutter moves along the path, in mm per minute. The time for a
# path of length L is L / F minutes.

# %%
def lap_time_s(side, r, feed):
    """Time in seconds for one lap of the centre path at the feed (mm/min)."""
    path = centre_path(side, r)
    if path is None:
        return float("nan")
    return polyline_length(path) / feed * 60.0


# %% [markdown]
# ## Step 5: see it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    side, d, feed = 20.0, 4.0, 120.0
    r = d / 2
    path = centre_path(side, r)
    print(f"pocket {side:g} mm, cutter diameter {d:g} mm, feed {feed:g} mm/min")
    print(f"centre path length = {polyline_length(path):.1f} mm, time = {lap_time_s(side, r, feed):.1f} s")
    print(f"island side after one lap = {island_side(side, r):.1f} mm")

    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    wall = square_outline(side)
    ax.plot(wall[:, 0], wall[:, 1], "k-", lw=2, label="pocket wall")
    ax.plot(path[:, 0], path[:, 1], "C0--", lw=1.5, label="cutter centre path")
    for corner in path[:4]:
        ax.add_patch(plt.Circle(corner, r, fill=False, color="C1", lw=1))
    ax.add_patch(plt.Circle(path[0], r, color="C1", alpha=0.35, label="cutter (diameter 4 mm)"))
    isl = island_side(side, r)
    c0 = (side - isl) / 2
    ax.add_patch(plt.Rectangle((c0, c0), isl, isl, color="C2", alpha=0.35, label="island left"))
    ax.set_aspect("equal")
    ax.set_xlim(-2, side + 2)
    ax.set_ylim(-2, side + 2)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title("A square pocket, the centre path and the island")
    ax.legend(loc="upper right", fontsize=7)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "pocket_lap.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ds = np.linspace(1, 9.5, 60)
    ax2.plot(ds, [polyline_length(centre_path(side, x / 2)) for x in ds], "C0")
    ax2.set_xlabel("cutter diameter (mm)")
    ax2.set_ylabel("one-lap path length (mm)")
    ax2.set_title("Bigger cutter: shorter lap (20 mm pocket)")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "lap_length_vs_diameter.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
