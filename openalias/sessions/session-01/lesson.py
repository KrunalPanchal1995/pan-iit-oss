"""Session 1 (Level 1): a wheel filmed at a fixed frame rate can look slow, frozen or backwards.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a wheel on camera
# **A. Real-world problem.** In films, car wheels and helicopter blades sometimes seem to turn
# slowly, stop, or spin the wrong way. The wheel is fine; the camera only looks at it
# 24 or 30 times a second and our brain joins the dots in the easiest way.
#
# **Plan.** (1) where is the marker in each frame, (2) how far does it seem to move between
# frames, (3) turn that into an apparent speed, (4) plot apparent speed against true speed.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: how far does the marker really turn between two frames?
# A wheel with one painted marker turns f revolutions every second. The camera takes fs frames
# every second, so the time between frames is 1/fs seconds. In that time the marker turns
#
#     step = 360 * f / fs   degrees
#
# Example: f = 28 rev/s and fs = 30 frames/s gives 360 * 28 / 30 = 336 degrees per frame.

# %%
def step_angle_deg(f, fs):
    """True turn of the marker between two frames, in degrees (may exceed 360)."""
    return 360.0 * f / fs


# %% [markdown]
# ## Step 2: what the eye sees
# Your eye cannot know how many full turns happened between frames. It only sees where the
# marker is now, and picks the shortest way from the old place to the new one. A turn of 336
# degrees looks like a turn of 336 - 360 = -24 degrees (24 degrees *backwards*). So we fold the
# step into the range -180 to +180 degrees.

# %%
def fold_deg(angle):
    """Fold any angle (degrees) into [-180, 180): the shortest signed turn."""
    return (angle + 180.0) % 360.0 - 180.0


def apparent_frequency(f, fs):
    """Apparent turns per second (signed): negative means the wheel seems to go backwards."""
    return fold_deg(step_angle_deg(f, fs)) / 360.0 * fs


def direction(f, fs, tol=1e-9):
    a = apparent_frequency(f, fs)
    if abs(abs(a) - fs / 2.0) < tol:
        return "flicker"        # exactly half a turn per frame: no way to say which way
    if abs(a) < tol:
        return "frozen"
    return "forward" if a > 0 else "backwards"


# %% [markdown]
# ## Step 3: the marker in every frame
# `marker_angles` lists where the marker is (degrees, counter-clockwise from the right) in
# frames 0, 1, 2, ... The picture the eye builds is the folded version of the same list.

# %%
def marker_angles(f, fs, n_frames):
    k = np.arange(n_frames)
    return np.mod(step_angle_deg(f, fs) * k, 360.0)


# %% [markdown]
# ## Step 4: see it
# Left: the marker positions in the first frames for four wheel speeds filmed at 30 frames per
# second. Right: apparent speed against true speed. The sawtooth is the whole story of this
# repo: every 30 rev/s the picture starts again.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    fs = 30.0
    cases = [3.0, 25.0, 29.0, 30.0]
    fig, axs = plt.subplots(1, 4, figsize=(10, 2.8))
    for ax, f in zip(axs, cases):
        ax.add_patch(plt.Circle((0, 0), 1.0, fill=False, color="gray"))
        ang = np.radians(marker_angles(f, fs, 6))
        for k, a in enumerate(ang):
            ax.plot(np.cos(a), np.sin(a), "o", color=plt.cm.viridis(k / 6), ms=9)
            ax.text(1.25 * np.cos(a), 1.25 * np.sin(a), str(k), ha="center", va="center", fontsize=8)
        ax.set_xlim(-1.6, 1.6)
        ax.set_ylim(-1.6, 1.6)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"true {f:.0f} rev/s\nseen {apparent_frequency(f, fs):+.0f} rev/s ({direction(f, fs)})", fontsize=9)
        print(f"true {f:4.1f} rev/s at {fs:.0f} fps -> step {step_angle_deg(f, fs):6.1f} deg, "
              f"seen {apparent_frequency(f, fs):+.2f} rev/s ({direction(f, fs)})")
    fig.suptitle("Frames 0 to 5 of a one-marker wheel filmed at 30 frames per second", fontsize=10)
    fig.savefig(OUT / "marker_frames.png", dpi=110, bbox_inches="tight")

    f_axis = np.linspace(0, 90, 901)
    seen = np.array([apparent_frequency(x, fs) for x in f_axis])
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(f_axis, f_axis, ":", color="gray", label="true speed")
    ax2.plot(f_axis, seen, ".", ms=2, color="tab:blue", label="apparent speed")
    ax2.axhline(0, color="k", lw=0.6)
    ax2.set_xlabel("true wheel speed f (rev/s)")
    ax2.set_ylabel("apparent speed (rev/s)")
    ax2.set_title("Apparent speed at 30 frames per second")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "apparent_vs_true.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
