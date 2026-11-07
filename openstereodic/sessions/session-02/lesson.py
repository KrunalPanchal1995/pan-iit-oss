"""Session 2 (Level 2): stereo triangulation and sub-pixel matching.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: from matched pixels to millimetres
# **A. Real-world problem.** Session 1 said Z = f B / d. A real camera gives pixels, and the
# computer must *find* the matching spot in the second picture by comparing small patches of
# random dots (speckle). If it can only find the match to a whole pixel, a surface 0.5 m away is
# located to about 6 mm, far too coarse to see a rubber strip stretch. How well can matching be
# done, and how does a matching error turn into a depth error?
#
# **Plan.** (1) triangulate a matched pixel pair into a 3D point, (2) turn a disparity error into a
# depth error, (3) match a patch by cross-correlation, (4) refine the match to a fraction of a
# pixel and measure its bias, (5) design a baseline for a required accuracy.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

F = 1000.0               # focal length in pixels
BASE = 0.04              # baseline in metres
CX, CY = 160.0, 80.0     # principal point (image centre) of a 320 x 160 pixel image


# %% [markdown]
# ## Step 1: triangulation with a calibrated pair
# "Calibrated" means f, B and the principal point (CX, CY) are known. A matched pair (uL, vL) in the
# left image and uR in the right image (same row, because the cameras are parallel) gives
#
#     d = uL - uR      Z = f B / d      X = (uL - CX) Z / f      Y = (vL - CY) Z / f
#
# Hand check: uL = 200, vL = 100, uR = 120 gives d = 80, Z = 0.5 m, X = 40 * 0.5 / 1000 = 0.02 m,
# Y = 20 * 0.5 / 1000 = 0.01 m.

# %%
def project_pair(point, f=F, baseline=BASE):
    """Pixel coordinates (uL, vL, uR) of a 3D point (X, Y, Z) in metres seen by the left (x = 0) and right (x = B) camera."""
    X, Y, Z = point
    return f * X / Z + CX, f * Y / Z + CY, f * (X - baseline) / Z + CX


def triangulate(uL, vL, uR, f=F, baseline=BASE):
    """3D point (X, Y, Z) in metres from a matched pixel pair. Disparity <= 0 gives NaN (no valid depth)."""
    d = np.asarray(uL, float) - np.asarray(uR, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        Z = np.where(d > 0, f * baseline / d, np.nan)
    return (np.asarray(uL, float) - CX) * Z / f, (np.asarray(vL, float) - CY) * Z / f, Z


# %% [markdown]
# ## Step 2: how a disparity error becomes a depth error
# From Z = f B / d, a small error dd in the disparity gives, to first order,
#
#     dZ = (f B / d^2) dd = (Z^2 / (f B)) dd
#
# Depth error grows with the *square* of the distance and shrinks with a longer baseline.
# Example: Z = 0.5 m, f B = 40 px*m, dd = 0.05 px gives dZ = 0.25 * 0.05 / 40 = 0.000313 m.

# %%
def depth_error(Z, dd, f=F, baseline=BASE):
    """First-order depth error (m) at depth Z (m) for a disparity error dd (pixels)."""
    return Z ** 2 * dd / (f * baseline)


def baseline_for(Z, dZ_max, dd, f=F):
    """Smallest baseline (m) for which the first-order depth error at depth Z stays within dZ_max (m)."""
    return Z ** 2 * dd / (f * dZ_max)


# %% [markdown]
# ## Step 3: finding the match by cross-correlation
# A row of pixels is a sum of round Gaussian dots at random places (a 1D speckle), 20 to 240 grey
# levels. We take a *subset* (a patch of 2h+1 pixels) from the left row and slide it along the right
# row. For each slide k we compute the zero-normalised cross-correlation (ZNCC):
#
#     C(k) = sum (f - mean f)(g_k - mean g_k) / sqrt( sum (f - mean f)^2 * sum (g_k - mean g_k)^2 )
#
# C is 1 for a perfect match (also if brightness and contrast differ) and near 0 for a random one.

# %%
def make_speckle_1d(n, seed=0, dot_sigma=1.5, density=0.35, margin=15):
    """Random dot positions and strengths for a speckle that can be drawn at fractional positions."""
    rng = np.random.default_rng(seed)
    count = int(density * (n + 2 * margin) / dot_sigma)
    return rng.uniform(-margin, n + margin, count), rng.uniform(0.5, 1.0, count), dot_sigma


def draw_row(speckle, n, shift=0.0, noise=0.0, seed=1):
    """Grey levels of pixels 0..n-1 when the pattern is moved right by `shift` pixels (any real number)."""
    pos, amp, sig = speckle
    x = np.arange(n, dtype=float)[:, None] - shift
    total = (amp[None, :] * np.exp(-((x - pos[None, :]) ** 2) / (2 * sig * sig))).sum(axis=1)
    row = 20.0 + 220.0 * (1.0 - np.exp(-1.5 * total))
    if noise > 0:
        row = row + np.random.default_rng(seed).normal(0.0, noise, n)
    return row


def zncc(f, g):
    f = f - f.mean()
    g = g - g.mean()
    den = np.sqrt((f * f).sum() * (g * g).sum())
    return float((f * g).sum() / den) if den > 0 else 0.0


def correlation_curve(left, right, i0, h=10, search=8):
    """ZNCC of the left subset centred at pixel i0 against the right row shifted by k = -search..search."""
    f = left[i0 - h:i0 + h + 1]
    ks = np.arange(-search, search + 1)
    c = np.array([zncc(f, right[i0 - h + k:i0 + h + 1 + k]) for k in ks])
    return ks, c


# %% [markdown]
# ## Step 4: sub-pixel refinement and its bias
# The best whole-pixel shift k0 is where C peaks. Near its top C looks like a hill, so fit a parabola
# through the three points C(k0 - 1), C(k0), C(k0 + 1); its top is at
#
#     k0 + (C(-) - C(+)) / ( 2 (C(-) - 2 C(0) + C(+)) )
#
# This is cheap and good to a few hundredths of a pixel, but a parabola is not exactly the hill
# shape, so the answer is pulled slightly toward whole pixels ("pixel locking"). For dots of size
# sigma the hill is close to exp(-D^2 / (4 sigma^2)), which lets us predict the bias.

# %%
def match_subpixel(left, right, i0, h=10, search=8):
    """Shift (pixels, real number) of the subset at i0 between the rows, to a fraction of a pixel."""
    ks, c = correlation_curve(left, right, i0, h, search)
    j = int(np.argmax(c))
    if j == 0 or j == len(c) - 1:
        raise ValueError("best match is at the edge of the search range: widen `search`")
    cm, c0, cp = c[j - 1], c[j], c[j + 1]
    return float(ks[j] + (cm - cp) / (2.0 * (cm - 2.0 * c0 + cp)))


def parabola_estimate(true_shift, sigma):
    """Predicted result of the 3-point parabola fit when the hill is exp(-D^2 / (4 sigma^2)) (true_shift in pixels)."""
    k0 = np.round(true_shift)
    r = lambda k: np.exp(-((k - true_shift) ** 2) / (4.0 * sigma ** 2))
    cm, c0, cp = r(k0 - 1), r(k0), r(k0 + 1)
    return k0 + (cm - cp) / (2.0 * (cm - 2.0 * c0 + cp))


def parabola_bias(true_shift, sigma):
    return parabola_estimate(true_shift, sigma) - true_shift


def measured_bias(shifts, seeds=range(12), n=120, h=10, noise=0.0):
    """Mean error of match_subpixel against the exact shift, over several random patterns (m seeds)."""
    err = np.zeros(len(shifts))
    for seed in seeds:
        sp = make_speckle_1d(n, seed=seed)
        left = draw_row(sp, n, 0.0)
        for i, t in enumerate(shifts):
            right = draw_row(sp, n, t, noise=noise, seed=100 + seed)
            err[i] += match_subpixel(left, right, n // 2, h) - t
    return err / len(seeds)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    uL, vL, uR = project_pair((0.02, 0.01, 0.5))
    X, Y, Z = triangulate(uL, vL, uR)
    print(f"point -> ({uL:.1f}, {vL:.1f}) and uR = {uR:.1f};  triangulated back: X {X:.4f} Y {Y:.4f} Z {Z:.4f} m")
    print(f"depth error at Z = 0.5 m for dd = 0.05 px: {1000 * depth_error(0.5, 0.05):.3f} mm;  whole-pixel (dd = 0.5): {1000 * depth_error(0.5, 0.5):.2f} mm")
    print(f"baseline for 0.2 mm at Z = 0.5 m with dd = 0.05 px: {1000 * baseline_for(0.5, 0.0002, 0.05):.1f} mm")

    sp = make_speckle_1d(120, seed=3)
    left, right = draw_row(sp, 120, 0.0), draw_row(sp, 120, 3.3)
    ks, c = correlation_curve(left, right, 60)
    print(f"true shift 3.30 px: best whole pixel {ks[np.argmax(c)]}, sub-pixel estimate {match_subpixel(left, right, 60):.3f}")

    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    ax[0].plot(np.arange(120), left, label="left row")
    ax[0].plot(np.arange(120), right, label="right row (moved 3.3 px)")
    ax[0].axvspan(50, 70, color="gray", alpha=0.2, label="subset (21 px)")
    ax[0].set_xlabel("pixel position")
    ax[0].set_ylabel("grey level (0 to 255)")
    ax[0].set_title("A 1D speckle seen twice")
    ax[0].legend(fontsize=8)
    ax[1].plot(ks, c, "o-", label="ZNCC at whole pixels")
    ax[1].axvline(3.3, color="r", ls="--", label="true shift 3.3 px")
    ax[1].axvline(match_subpixel(left, right, 60), color="g", ls=":", label="sub-pixel estimate")
    ax[1].set_xlabel("trial shift k (pixels)")
    ax[1].set_ylabel("correlation C (no unit)")
    ax[1].set_title("Correlation peaks near the true shift")
    ax[1].legend(fontsize=8)
    for a_ in ax:
        a_.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "correlation_peak.png", dpi=110)

    shifts = np.arange(0.0, 1.01, 0.1)
    mb = measured_bias(shifts)
    model = parabola_bias(shifts, 1.5)
    print("fractional shift :", np.round(shifts, 1))
    print("measured bias    :", np.round(mb, 3))
    print("model bias (1.5) :", np.round(model, 3))
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(shifts, mb, "o", label="measured (12 random patterns)")
    ax2.plot(np.linspace(0, 1, 101), parabola_bias(np.linspace(0, 1, 101), 1.5), "-", label="model, dot size 1.5 px")
    ax2.axhline(0, color="gray", lw=0.8)
    ax2.set_xlabel("fractional part of the true shift (pixels)")
    ax2.set_ylabel("error of the estimate (pixels)")
    ax2.set_title("Parabola fit: zero at 0 and 0.5, biased in between")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "subpixel_bias.png", dpi=110)

    Zs = np.linspace(0.3, 1.5, 100)
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    for dd, b in ((0.5, 0.04), (0.05, 0.04), (0.05, 0.08)):
        ax3.plot(Zs, 1000 * depth_error(Zs, dd, baseline=b), label=f"disparity error {dd} px, baseline {1000 * b:.0f} mm")
    ax3.set_yscale("log")
    ax3.set_xlabel("depth Z (m)")
    ax3.set_ylabel("depth error (mm)")
    ax3.set_title("Sub-pixel matching and a longer baseline both cut depth error")
    ax3.grid(alpha=0.3, which="both")
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "depth_error.png", dpi=110)
