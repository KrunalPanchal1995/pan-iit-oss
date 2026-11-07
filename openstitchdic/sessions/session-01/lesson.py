"""Session 1 (Level 1): why two cameras disagree.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: why two cameras disagree
# **A. Real-world problem.** You film a speckled rubber sheet with two cameras. Camera A looks
# straight at it. Camera B stands to one side. B has a wider picture and runs at 24 pictures a
# second while A runs at 30. When you put the two videos side by side, nothing lines up.
#
# **Plan.** (1) draw a grid on a sheet and see it from two angles, (2) compare picture sizes
# and shapes, (3) compare the two clocks, (4) match points by eye and find the stretch needed
# to bring one picture onto the other.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# Camera A: looks straight at the sheet. Camera B: stands 40 degrees to the side.
CAM_A = {"name": "A", "width": 640, "height": 480, "fps": 30, "yaw": 0.0, "px_per_unit": 40.0}
CAM_B = {"name": "B", "width": 1280, "height": 720, "fps": 24, "yaw": 40.0, "px_per_unit": 60.0}


# %% [markdown]
# ## Step 1: one sheet, two views
# The sheet is 10 units wide and 6 units tall, with a grid line every unit. A camera turned
# `yaw` degrees to the side sees every sideways distance squeezed by cos(yaw); up-and-down
# distances are not squeezed. (This is the simplest model: a far-away camera. Session 2 handles
# the full perspective.) The picture also has a size: `px_per_unit` pixels for every unit.

# %%
def grid_points(nx=11, ny=7):
    """Grid crossings on the sheet, in sheet units: (x, y) with x from 0 to 10 and y from 0 to 6."""
    gx, gy = np.meshgrid(np.arange(nx, dtype=float), np.arange(ny, dtype=float))
    return np.stack([gx.ravel(), gy.ravel()], axis=1)


def width_ratio(yaw_deg):
    """How much a sideways distance is squeezed when the camera is turned yaw_deg to the side."""
    return math.cos(math.radians(yaw_deg))


def view_of_sheet(points, cam):
    """Pixel positions (x right, y down) of sheet points, with the sheet centre in the picture centre."""
    pts = np.asarray(points, dtype=float) - np.array([5.0, 3.0])
    k = cam["px_per_unit"]
    x = cam["width"] / 2 + k * width_ratio(cam["yaw"]) * pts[:, 0]
    y = cam["height"] / 2 + k * pts[:, 1]
    return np.stack([x, y], axis=1)


def aspect_ratio(cam):
    return cam["width"] / cam["height"]


# %% [markdown]
# ## Step 2: match points by eye, then find the stretch
# Pick landmarks that you can recognise in both pictures (corners of the sheet). The sideways
# stretch that brings picture B onto picture A is (distance between two landmarks in A) divided
# by (the same distance in B). The up-and-down stretch is found the same way. If the two stretches
# differ, a single "resize" cannot fix it.

# %%
LANDMARKS = np.array([[0.0, 0.0], [10.0, 0.0], [10.0, 6.0], [0.0, 6.0]])      # the four sheet corners


def stretch_between(pa, pb):
    """(sideways, up-down) stretch that turns landmark spacing in picture B into spacing in picture A.
    pa and pb are arrays of the same landmarks; uses the first two for x and the first and last for y."""
    sx = (pa[1, 0] - pa[0, 0]) / (pb[1, 0] - pb[0, 0])
    sy = (pa[3, 1] - pa[0, 1]) / (pb[3, 1] - pb[0, 1])
    return float(sx), float(sy)


# %% [markdown]
# ## Step 3: two clocks
# Camera A takes a picture at 0, 1/30, 2/30 ... seconds; camera B at 0, 1/24, 2/24 ... seconds.
# They only agree when k/30 = m/24, which happens every 1/6 s (6 is the largest number that
# divides both 30 and 24). In between, the nearest B picture is up to some milliseconds away,
# and a moving sample travels in that time.

# %%
def frame_times(fps, seconds):
    return np.arange(int(math.floor(seconds * fps + 1e-9)) + 1) / fps


def coincide_period(fps_a, fps_b):
    """Seconds between moments when both cameras take a picture together (both rates whole numbers)."""
    return 1.0 / math.gcd(int(fps_a), int(fps_b))


def worst_gap(fps_a, fps_b, seconds=1.0):
    """Largest time distance (s) from any A picture to the nearest B picture."""
    ta = np.arange(int(seconds * fps_a)) / fps_a
    tb = np.arange(int(seconds * fps_b) + 2) / fps_b
    return float(max(np.min(np.abs(tb - t)) for t in ta))


def gap_to_b(t, fps_b):
    """Time distance (s) from instant t to the nearest camera B picture."""
    m = int(round(t * fps_b))
    return min(abs(t - c / fps_b) for c in range(max(0, m - 1), m + 2))


def position_error(speed, gap):
    """Distance (pixels) a sample moves during a timing gap, if you pretend the pictures are simultaneous."""
    return speed * gap


# %% [markdown]
# ## See it
# Left: the sheet in the two pictures (drawn to the same pixel scale, so you see which camera
# has the bigger frame). Right: the picture times of both cameras on one time axis.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    pts = grid_points()
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    for a, cam in zip(ax, (CAM_A, CAM_B)):
        p = view_of_sheet(pts, cam)
        a.add_patch(plt.Rectangle((0, 0), cam["width"], cam["height"], fc="none", ec="k"))
        a.plot(p[:, 0], p[:, 1], "b.", ms=4)
        lm = view_of_sheet(LANDMARKS, cam)
        for i, (x, y) in enumerate(lm, 1):
            a.plot(x, y, "ro")
            a.annotate(str(i), (x, y), textcoords="offset points", xytext=(5, 5), color="r")
        a.set_xlim(-20, 1300)
        a.set_ylim(740, -20)
        a.set_aspect("equal")
        a.set_title(f"camera {cam['name']}: {cam['width']} x {cam['height']} px, {aspect_ratio(cam):.2f}:1")
        a.set_xlabel("x (pixels)")
        a.set_ylabel("y (pixels)")
    fig.tight_layout()
    fig.savefig(OUT / "two_views.png", dpi=110)
    pa, pb = view_of_sheet(LANDMARKS, CAM_A), view_of_sheet(LANDMARKS, CAM_B)
    sx, sy = stretch_between(pa, pb)
    print(f"width ratio at yaw 40 degrees: {width_ratio(40):.3f}")
    print(f"stretch needed to bring B onto A: sideways {sx:.3f}, up-down {sy:.3f}")

    fig, ax = plt.subplots(figsize=(9, 2.8))
    ta, tb = frame_times(30, 0.2), frame_times(24, 0.2)
    ax.vlines(ta, 0.5, 1.0, color="tab:blue", label="camera A (30 fps)")
    ax.vlines(tb, 0.0, 0.5, color="tab:orange", label="camera B (24 fps)")
    ax.set_yticks([])
    ax.set_xlabel("time (s)")
    ax.set_title("Picture times: the cameras agree only at 0, 1/6 s ...")
    ax.legend(loc="upper right", ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "two_clocks.png", dpi=110)
    print(f"cameras take a picture together every {coincide_period(30, 24):.4f} s")
    gap = worst_gap(30, 24)
    print(f"worst gap between an A picture and the nearest B picture: {gap * 1000:.2f} ms")
    print(f"a sample moving at 120 px/s travels {position_error(120, gap):.1f} px in that time")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
