"""Session 1 (Level 1): one matrix moves a whole arm.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: one matrix moves a whole arm
# **A. Real-world problem.** A film character is thousands of points. To wave, every point
# must move, together, without the arm stretching. Animators do this with a *matrix*.
#
# **Plan.** (1) write the rotation matrix, (2) use it on a list of points, (3) check that the
# arm keeps its length, (4) plot where the hand goes as the angle changes.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the rotation matrix
# A matrix is a grid of numbers. Multiplying a matrix by a point works like this: each new
# coordinate is a row of the matrix multiplied term by term with (x, y), then added.
#
#     R = [[cos t, -sin t],      new_x = cos t * x  -  sin t * y
#          [sin t,  cos t]]      new_y = sin t * x  +  cos t * y
#
# Check by hand with t = 90 degrees (cos = 0, sin = 1) and the point (1, 0):
# new_x = 0*1 - 1*0 = 0 and new_y = 1*1 + 0*0 = 1. The point (1, 0) moves to (0, 1).

# %%
def rotation(theta):
    """2x2 matrix that turns points counter-clockwise by theta (radians)."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s],
                     [s, c]])


# %% [markdown]
# ## Step 2: the arm is a list of points
# Four corners of a thin rectangle, one point per row. To move every row at once we use
# `points @ R.T` (the transpose `.T` flips R so that rows can be multiplied).

# %%
ARM = np.array([[0.0, -0.1],
                [1.0, -0.1],
                [1.0, 0.1],
                [0.0, 0.1]])     # a 1 unit long arm, 0.2 units thick


def rotate_points(points, theta):
    return points @ rotation(theta).T


# %% [markdown]
# ## Step 3: a rotation does not stretch
# The arm length is the distance from the middle of the shoulder end to the middle of the
# hand end. For every angle it must stay 1.

# %%
def arm_length(points):
    shoulder = points[[0, 3]].mean(axis=0)
    hand = points[[1, 2]].mean(axis=0)
    return float(np.linalg.norm(hand - shoulder))


def hand_position(theta):
    """Where the middle of the hand end lands for a given angle (radians)."""
    return rotate_points(ARM, theta)[[1, 2]].mean(axis=0)


# %% [markdown]
# ## Step 4: see it
# Left: the arm in four poses. Right: the hand's x and y as the angle grows. They are the
# cosine and sine curves you know from school: the matrix is just a clean way to use them.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 5))
    for deg in (0, 30, 60, 90):
        moved = rotate_points(ARM, np.radians(deg))
        ax.fill(moved[:, 0], moved[:, 1], alpha=0.35, label=f"{deg} deg")
        print(f"angle {deg:3d} deg -> hand at {hand_position(np.radians(deg)).round(3)}, "
              f"length {arm_length(moved):.3f}")
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.legend(title="angle")
    ax.set_xlabel("x (units)")
    ax.set_ylabel("y (units)")
    ax.set_title("One matrix, four poses")
    fig.savefig(OUT / "arm_poses.png", dpi=120)

    deg = np.linspace(0, 90, 91)
    hands = np.array([hand_position(np.radians(d)) for d in deg])
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(deg, hands[:, 0], label="hand x")
    ax2.plot(deg, hands[:, 1], label="hand y")
    ax2.axvline(45, color="gray", ls=":")
    ax2.set_xlabel("arm angle (degrees)")
    ax2.set_ylabel("hand coordinate (units)")
    ax2.set_title("Hand x and y cross at 45 degrees (0.707, 0.707)")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "hand_vs_angle.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
