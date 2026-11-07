"""Session 2 (Level 2): find the match. Image correlation, sub-pixel peaks and their statistics.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: find the same spot in two photos
# **A. Real-world problem.** Session 1 turned a disparity into a depth, but somebody had to
# tell us which pixel in the right photo shows the same bit of flame as a pixel in the left
# photo. A computer must find that match by itself, thousands of times per photo, and to a
# fraction of a pixel, because a 0.5 px mistake was already worth 2.5 cm of depth. How does it
# compare two small patches of image, and how good is the answer, on average and in spread?
#
# **Plan.** (1) the zero-mean normalised cross-correlation (ZNCC) score, (2) search along the
# row for the best integer shift, (3) a parabola through the top three scores for the
# sub-pixel shift, (4) a Monte Carlo study of the bias and the spread of the result.
#
# **Model.** Synthetic "speckle" images (random bright dots, like the soot and wrinkle texture
# of a flame or the paint speckles of digital image correlation, DIC) whose true shift we
# know exactly. A simplified teaching model, not a measurement tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: a test image whose answer we know
# We scatter Gaussian dots of radius about 2 px at random places. Because each dot is a
# formula, we can draw the same pattern moved by any amount, for example 0.3 px, exactly.

# %%
def speckle_image(shape=(64, 96), n_dots=260, radius=2.0, shift=0.0, seed=0):
    """Image (rows, cols) of random Gaussian dots, values about 0..1, moved right by `shift` px."""
    rng = np.random.default_rng(seed)
    rows, cols = shape
    cy = rng.uniform(-5, rows + 5, n_dots)
    cx = rng.uniform(-5, cols + 5, n_dots)
    amp = rng.uniform(0.5, 1.0, n_dots)
    yy, xx = np.mgrid[0:rows, 0:cols].astype(float)
    img = np.zeros(shape)
    for y0, x0, a in zip(cy, cx, amp):
        img += a * np.exp(-((xx - x0 - shift) ** 2 + (yy - y0) ** 2) / (2 * radius ** 2))
    return img / max(img.max(), 1e-12)


# %% [markdown]
# ## Step 2: the ZNCC score
# Take a window f from the left image and a window g of the same size from the right image.
# Subtract each window's mean, then
#
#     ZNCC = sum (f - mean f)(g - mean g) / sqrt( sum (f - mean f)^2 * sum (g - mean g)^2 )
#
# It is the correlation coefficient r of statistics, computed over the pixels. It is +1 for
# a perfect match, about 0 for unrelated patches and -1 for a negative image. Because the
# means are removed and the result is divided by the spreads, a brighter or higher-contrast
# copy of the same patch (g = a f + b, a > 0) still scores exactly 1. That matters: the two
# cameras never have exactly the same gain.

# %%
def zncc(f, g):
    """Zero-mean normalised cross-correlation of two equal-size arrays (no unit, -1..1)."""
    f = np.asarray(f, float).ravel()
    g = np.asarray(g, float).ravel()
    if f.shape != g.shape:
        raise ValueError("windows must have the same size")
    f = f - f.mean()
    g = g - g.mean()
    den = np.sqrt(np.sum(f * f) * np.sum(g * g))
    if den == 0:
        raise ValueError("a window has no texture (zero variance); ZNCC is undefined")
    return float(np.sum(f * g) / den)


# %% [markdown]
# ## Step 3: search, then refine with a parabola
# For a window centred at column x in the left image we try every whole shift s in a search
# range: the window at x - s in the right image. The best whole shift has the largest score.
# The true shift is usually between two whole pixels. Fit a parabola through the scores at
# s - 1, s and s + 1 (c_minus, c_0, c_plus); its top is at
#
#     delta = (c_minus - c_plus) / (2 (c_minus - 2 c_0 + c_plus))
#
# which lies between -0.5 and +0.5 when c_0 is the largest. The answer is s + delta.

# %%
def subpixel_peak(c_minus, c0, c_plus):
    """Offset (px) of the top of the parabola through three equally spaced scores."""
    den = c_minus - 2.0 * c0 + c_plus
    if den >= 0:
        raise ValueError("the middle score must be a strict peak")
    return (c_minus - c_plus) / (2.0 * den)


def match(left, right, row, col, half, search):
    """Find the shift of the left window (centre row, col; size 2*half+1) in the right image.

    Tries whole shifts in `search` (iterable of ints, right window centre = col - s).
    Returns (sub-pixel shift, scores array)."""
    search = np.asarray(list(search), int)
    win = left[row - half:row + half + 1, col - half:col + half + 1]
    scores = np.array([zncc(win, right[row - half:row + half + 1, col - s - half:col - s + half + 1])
                       for s in search])
    k = int(np.argmax(scores))
    if k == 0 or k == len(scores) - 1:
        return float(search[k]), scores       # peak on the edge of the range: no refinement
    return float(search[k] + subpixel_peak(scores[k - 1], scores[k], scores[k + 1])), scores


# %% [markdown]
# ## Step 4: how good is the match? Bias and spread
# A measurement has two kinds of error. The **bias** is the average error over many repeats;
# the **spread** (standard deviation) is how much repeats scatter. We make many test pairs
# with a known shift, add random camera noise, measure the shift each time, and compute both.
# The parabola is not the true shape of the score curve, so it pulls answers toward whole
# pixels ("peak locking"): a bias that depends on the sub-pixel part of the shift. Noise adds
# spread, and a larger window averages the noise down.

# %%
def shift_statistics(true_shift, noise, half=7, trials=40, seed=0):
    """Measure a known shift `trials` times with Gaussian noise (std `noise`, image units).

    Returns (bias, standard deviation) of the measured minus true shift, in px."""
    rng = np.random.default_rng(seed)
    errs = []
    for t in range(trials):
        left = speckle_image((2 * half + 9, 2 * half + 30), n_dots=int(0.03 * (2 * half + 9) * (2 * half + 30)) + 5,
                             seed=1000 + t)
        right = speckle_image(left.shape, n_dots=int(0.03 * (2 * half + 9) * (2 * half + 30)) + 5,
                              shift=-true_shift, seed=1000 + t)
        left = left + rng.normal(0, noise, left.shape)
        right = right + rng.normal(0, noise, right.shape)
        r0, c0 = left.shape[0] // 2, left.shape[1] // 2
        d, _ = match(left, right, r0, c0, half, range(-3, 4))
        errs.append(d - true_shift)
    errs = np.array(errs)
    return float(errs.mean()), float(errs.std(ddof=1))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # worked example numbers
    print("ZNCC([2, 4, 6], [11, 12, 13]) =", round(zncc([2, 4, 6], [11, 12, 13]), 6))
    delta = subpixel_peak(0.80, 0.95, 0.90)
    print(f"Parabola through 0.80, 0.95, 0.90 at d = 39, 40, 41: d = {40 + delta:.2f} px, "
          f"Z = 800 x 0.10 / {40 + delta:.2f} = {80 / (40 + delta):.4f} m")

    # Figure 1: two speckle images, the score curve and the parabola
    true = 5.3
    left = speckle_image((48, 96), seed=3)
    right = speckle_image((48, 96), shift=-true, seed=3)      # same pattern, 5.3 px to the left
    rng = np.random.default_rng(4)
    left_n, right_n = left + rng.normal(0, 0.03, left.shape), right + rng.normal(0, 0.03, right.shape)
    d, scores = match(left_n, right_n, 24, 50, 8, range(0, 11))
    print(f"Speckle test: true shift {true} px, measured {d:.3f} px")
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.6), gridspec_kw={"width_ratios": [1, 1, 1.2]})
    for ax, im, name, cx in [(axes[0], left_n, "left image", 50), (axes[1], right_n, "right image", 50 - true)]:
        ax.imshow(im, cmap="inferno", origin="upper")
        ax.add_patch(plt.Rectangle((cx - 8.5, 24 - 8.5), 17, 17, fill=False, ec="#4fc3f7", lw=2))
        ax.set_title(f"{name} (17 x 17 px window)")
        ax.set_xlabel("column x (px)")
        ax.set_ylabel("row (px)")
    ax = axes[2]
    s = np.arange(0, 11)
    ax.plot(s, scores, "o-", color="#1f6feb", label="ZNCC at whole shifts")
    k = int(np.argmax(scores))
    ss = np.linspace(s[k] - 1.3, s[k] + 1.3, 100)
    a = 0.5 * (scores[k - 1] - 2 * scores[k] + scores[k + 1])
    b = 0.5 * (scores[k + 1] - scores[k - 1])
    ax.plot(ss, a * (ss - s[k]) ** 2 + b * (ss - s[k]) + scores[k], color="#d9534f", label="parabola through top 3")
    ax.axvline(true, color="k", ls="--", lw=1, label=f"true shift {true} px")
    ax.axvline(d, color="#d9534f", ls=":", lw=1.5, label=f"measured {d:.2f} px")
    ax.set_xlabel("trial shift s (px)")
    ax.set_ylabel("ZNCC score (no unit)")
    ax.set_title("Search, then refine the peak")
    ax.set_ylim(-0.6, 1.1)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, loc="lower center")
    fig.tight_layout()
    fig.savefig(OUT / "zncc_match.png", dpi=120)

    # Figure 2: statistics of the error (bias against sub-pixel shift, spread against window size)
    fig2, axes = plt.subplots(1, 2, figsize=(10, 4))
    fr = np.linspace(0.0, 1.0, 11)
    bias = [shift_statistics(x, 0.0, half=7, trials=12)[0] for x in fr]
    axes[0].plot(fr, bias, "o-", color="#d9534f")
    axes[0].axhline(0, color="k", lw=1)
    axes[0].set_xlabel("true sub-pixel shift (px)")
    axes[0].set_ylabel("bias = mean error (px)")
    axes[0].set_title("Peak locking: no noise, 15 x 15 window")
    axes[0].grid(alpha=0.3)
    halves = [3, 5, 7, 10]
    for noise, col in [(0.02, "#2a9d8f"), (0.06, "#1f6feb")]:
        sd = [shift_statistics(0.3, noise, half=h, trials=40)[1] for h in halves]
        axes[1].plot([2 * h + 1 for h in halves], sd, "o-", color=col, label=f"noise {noise:.2f}")
        print(f"noise {noise}: spread for windows {[2 * h + 1 for h in halves]} px = {np.round(sd, 4)} px")
    axes[1].set_xlabel("window size (px)")
    axes[1].set_ylabel("spread = std of error (px)")
    axes[1].set_title("More noise, more spread; bigger window, less")
    axes[1].grid(alpha=0.3)
    axes[1].legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "match_statistics.png", dpi=120)
    print("max |bias| with no noise:", round(max(abs(b) for b in bias), 4), "px")

# %% [markdown]
# ## Where this stops
# We matched one window between two flat test images. A flame is curved and seen from many
# sides. Session 3 renders a textured flame from several stereo pairs, matches thousands of
# windows, triangulates them into 3D points and rebuilds the flame's shape and volume.
