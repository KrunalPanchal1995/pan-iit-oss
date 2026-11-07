"""Session 1 (Level 1): stack one line of pixels from every frame and read the slanted stripe.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: one line of pixels, stacked over time
# **A. Real-world problem.** A camera films something that moves along a line: a bead in a
# tube, a drop in a gutter, a bright patch riding a flame. Watching the video tells you "it
# moves", but how fast? A *kymograph* answers with one picture.
#
# **Plan.** (1) make a tiny video with a moving blob, (2) cut out one row of pixels from every
# frame, (3) stack those rows into a new image (position across, time down), (4) read the
# speed from the slope of the stripe.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: a tiny video
# Each frame is a grid of brightness numbers, `height` rows by `width` columns. The blob is a
# soft bright spot that sits at column `x0 + v * t` in frame number `t`. So it moves `v`
# pixels in every frame (v is the speed in pixels per frame).

# %%
def blob_frames(v, x0=8.0, n_frames=40, width=64, height=15, sigma=2.0):
    """Return frames with shape (n_frames, height, width): a Gaussian blob moving right at v px/frame."""
    t = np.arange(n_frames)[:, None, None]
    y = np.arange(height)[None, :, None]
    x = np.arange(width)[None, None, :]
    cx = x0 + v * t
    cy = height // 2
    return np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * sigma ** 2))


# %% [markdown]
# ## Step 2: cut out one line, then stack
# `take_line` copies one row of pixels from one frame. `kymograph` does that for every frame
# and stacks the rows: row number = frame number (time), column number = position.

# %%
def take_line(frame, row):
    """One row of pixels from one frame."""
    return frame[row, :]


def kymograph(frames, row):
    """Stack the chosen row of every frame. Result shape (n_frames, width): time down, position across."""
    return np.stack([take_line(f, row) for f in frames])


# %% [markdown]
# ## Step 3: the stripe and its slope
# In each row of the kymograph the blob is where the brightness is largest. Listing that
# column for every row draws the stripe. Slope = how far across (pixels) per step down
# (frames) = the speed in pixels per frame.

# %%
def stripe_position(K):
    """Column of the brightest pixel in each row of the kymograph (pixels)."""
    return np.argmax(K, axis=1)


def slope_two_points(K, t1, t2):
    """Speed in pixels per frame from the stripe position at frames t1 and t2."""
    x = stripe_position(K)
    return float((x[t2] - x[t1]) / (t2 - t1))


def slope_fit(K):
    """Speed in pixels per frame from a straight line through the whole stripe."""
    t = np.arange(K.shape[0])
    return float(np.polyfit(t, stripe_position(K), 1)[0])


# %% [markdown]
# ## Step 4: see it
# Left: three frames of the video with the chosen line marked. Right: the kymograph. A faster
# blob gives a flatter, more tilted stripe (it covers more pixels per frame); a still blob gives
# a vertical stripe.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    frames = blob_frames(0.6)
    row = frames.shape[1] // 2
    K = kymograph(frames, row)
    print("kymograph shape (frames, pixels):", K.shape)
    print("slope from frames 10 and 30:", slope_two_points(K, 10, 30), "px/frame")
    print("slope from a line fit:", round(slope_fit(K), 3), "px/frame")

    fig, axs = plt.subplots(1, 3, figsize=(9, 2.6))
    for ax, t in zip(axs, (0, 20, 39)):
        ax.imshow(frames[t], cmap="gray", vmin=0, vmax=1)
        ax.axhline(row, color="tab:red", lw=1)
        ax.set_title(f"frame {t}")
        ax.set_xlabel("x (pixels)")
        ax.set_ylabel("y (pixels)")
    fig.tight_layout()
    fig.savefig(OUT / "frames_and_line.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(5, 4.2))
    ax2.imshow(K, cmap="gray", aspect="auto", origin="upper")
    t = np.arange(K.shape[0])
    ax2.plot(stripe_position(K), t, "r.", ms=3, label="brightest pixel")
    ax2.set_xlabel("position x (pixels)")
    ax2.set_ylabel("time t (frames)")
    ax2.set_title("Kymograph: slope dx/dt = 0.6 px/frame")
    ax2.legend(loc="lower left")
    fig2.tight_layout()
    fig2.savefig(OUT / "kymograph.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
