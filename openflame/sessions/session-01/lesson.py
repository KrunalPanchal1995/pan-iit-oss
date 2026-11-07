"""Session 1 (Level 1): a flame video is a stack of pictures, and a threshold finds the flame.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a flame video is a stack of pictures
# **A. Real-world problem.** You film a flame with a phone. How tall is it? A ruler held up to a
# flickering flame is useless, but a video is just many still pictures, and a computer can
# measure the same flame in every one of them.
#
# **Plan.** (1) a picture is a grid of brightness numbers, (2) a *threshold* turns it into a
# flame mask of yes/no pixels, (3) count the mask rows from the burner up, (4) turn pixels into
# millimetres with a scale, (5) stack many pictures into a video and get a height for each.
#
# Real footage is not available here, so we draw a *synthetic* flame with a height we know.
# That lets us check that the measurement is right, which is the whole idea of this repo.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

ROWS, COLS = 100, 61      # picture size in pixels (rows down, columns across)
BASE_ROW = 95             # the burner top sits on this row; height is counted upward from it
AXIS_COL = 30             # the flame axis (middle column)
SOFT = 2.0                # how many pixels the flame tip fades over


# %% [markdown]
# ## Step 1: a synthetic flame picture
# Brightness runs from 0 (black) to 1 (white). Along the flame axis the brightness is 1 near
# the burner and fades to 0 over a few pixels around the tip. We *define* the true height as the
# place where the brightness is exactly half, so a good measurement should give that number back.
#
#     brightness on the axis = 1 / (1 + exp((z - h) / SOFT))      z = height above the burner (px)
#
# At z = h this is exactly 1/2. Sideways the flame is brightest in the middle and narrows upward.

# %%
def flame_frame(height_px, softness=SOFT, noise=0.0, seed=0):
    """One picture (ROWS x COLS) of a flame whose half-brightness tip is height_px above the burner."""
    z = BASE_ROW - np.arange(ROWS, dtype=float)[:, None]          # height of each row above the burner
    x = np.arange(COLS, dtype=float)[None, :] - AXIS_COL           # sideways distance from the axis
    along = 1.0 / (1.0 + np.exp((z - height_px) / softness))
    half_width = np.maximum(2.0, 9.0 * (1.0 - 0.75 * z / height_px))
    img = along * np.exp(-(x / half_width) ** 2)
    img = np.where(z < 0, 0.0, img)                                # nothing below the burner row
    if noise > 0:
        img = img + np.random.default_rng(seed).normal(0.0, noise, img.shape)
    return np.clip(img, 0.0, 1.0)


# %% [markdown]
# ## Step 2: threshold -> flame mask
# A *mask* is a picture of True/False. A pixel belongs to the flame if its brightness is at least
# the threshold. Then we walk up from the burner row and count how many rows still contain
# flame pixels. `min_row_pixels` ignores rows with only a few stray pixels (noise specks).

# %%
def flame_mask(frame, threshold):
    return frame >= threshold


def flame_height_px(mask, min_row_pixels=1):
    """Rows between the burner row and the highest row of the flame (the run must be unbroken)."""
    top = 0
    for z in range(0, BASE_ROW + 1):
        if mask[BASE_ROW - z].sum() >= min_row_pixels:
            top = z
        else:
            break
    return top


# %% [markdown]
# ## Step 3: pixels -> millimetres
# Put a ruler beside the flame. If 100 px of the picture cover 50 mm of the ruler, then
# `scale = 50 / 100 = 0.5 mm per pixel`, and a flame 60 px tall is 60 x 0.5 = 30 mm tall.

# %%
def scale_mm_per_px(ref_mm, ref_px):
    return ref_mm / ref_px


def height_mm(height_px, scale):
    return height_px * scale


def predicted_height_px(h_true, threshold, softness=SOFT):
    """Closed form for the noise-free measurement: the highest whole-pixel row with brightness >= threshold."""
    if threshold <= 0:
        return BASE_ROW
    if threshold >= 1:
        return 0
    z = h_true + softness * np.log((1.0 - threshold) / threshold)
    return int(min(BASE_ROW, max(0, np.floor(z + 1e-9))))


# %% [markdown]
# ## Step 4: a video is a stack of pictures
# A video of N frames is an array of shape (N, rows, columns). Measuring every frame gives a
# *height trace*: height against frame number. Dividing the frame number by the frame rate
# (frames per second) gives time.

# %%
def video_stack(heights_px, softness=SOFT, noise=0.0, seed=0):
    return np.stack([flame_frame(h, softness, noise, seed + k) for k, h in enumerate(heights_px)])


def height_trace(stack, threshold, min_row_pixels=1):
    return np.array([flame_height_px(flame_mask(f, threshold), min_row_pixels) for f in stack])


# %% [markdown]
# ## Step 5: see it
# Left: the picture, the mask at threshold 0.5, and the measured height. Right: how the measured
# height changes when you move the threshold (it is exact at 0.5 and drifts away from it).

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    h = 60
    img = flame_frame(h)
    m = flame_mask(img, 0.5)
    hp = flame_height_px(m)
    print(f"true height {h} px, measured {hp} px, scale 0.5 mm/px -> {height_mm(hp, 0.5):.1f} mm")

    fig, ax = plt.subplots(1, 3, figsize=(8.5, 4.2))
    ax[0].imshow(img, cmap="gray", vmin=0, vmax=1)
    ax[0].set_title("brightness picture")
    ax[1].imshow(m, cmap="gray")
    ax[1].set_title("mask (threshold 0.5)")
    noisy = flame_frame(h, noise=0.12, seed=3)
    ax[2].imshow(noisy, cmap="gray", vmin=0, vmax=1)
    ax[2].set_title("with camera noise")
    for a in ax:
        a.axhline(BASE_ROW - hp, color="tab:red", lw=1)
        a.set_xlabel("column (px)")
        a.set_ylabel("row (px, down)")
    fig.suptitle(f"red line: measured tip, {hp} px above the burner row")
    fig.tight_layout()
    fig.savefig(OUT / "frame_mask.png", dpi=110)

    thr = np.arange(0.1, 0.91, 0.05)
    meas = [predicted_height_px(h, t) for t in thr]
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(thr, meas, "o-", label="measured height")
    ax2.axhline(h, color="gray", ls=":", label="true height")
    ax2.set_xlabel("threshold (fraction of full brightness)")
    ax2.set_ylabel("measured height (px)")
    ax2.set_title("The threshold you pick moves the tip")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "threshold_vs_height.png", dpi=120)
    for t in (0.2, 0.5, 0.8):
        print(f"threshold {t:.1f} -> measured {predicted_height_px(h, t)} px")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
