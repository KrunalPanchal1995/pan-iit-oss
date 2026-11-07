"""Session 5 (Level 3): find the flame axis in the photo.

Educational model only. Not a measurement method for any real flame or safety decision.
Run:  python start.py 5
"""
# %% [markdown]
# # Session 5: where is the axis?
# **A. Real-world problem.** Every inversion so far assumed that the symmetry axis of the flame
# runs exactly through the middle of one pixel column. A real camera is never aligned that
# well: the flame sits a fraction of a pixel off. A one-pixel (0.15 mm) mistake already makes the
# recovered flame wrong by about as much as 3 percent noise does. The photo itself shows where the
# axis is, because a round flame looks the same on the left and on the right of its axis. We build
# two axis finders, test them on a candle photo whose axis we moved on purpose (so the truth is
# known), and then invert with the axis we found, using *both* halves of the photo.
#
# **Plan.** (1) a photo with the axis anywhere, and the inversion for any pixel positions,
# (2) what a wrong axis costs, (3) finder 1: the centroid, (4) finder 2: match the photo with its
# mirror image, (5) invert with the found axis, (6) 20 noise draws against the alternatives.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
R_CANDLE = 6.0
N_RINGS = 40


# %% [markdown]
# ## Step 1: a full photo with the axis anywhere
# A full photo has `2N - 1 = 79` pixel columns, `N = 40` on each side of the middle column. We
# measure positions in *pixels from the middle of the picture* (right is positive); one pixel is
# `dr = R / N = 0.15 mm`. If the axis is at `shift` pixels, the column at position x sees the line
# of sight at offset |x - shift| * dr from the axis. The brightness there is a line integral
# (Session 1), computed with a fine integral, not with the matrix we invert with (no inverse crime).
#
# For the inversion the offsets are no longer the neat numbers 0, dr, 2 dr, ...: each pixel has
# its own offset y, and its row of the ring matrix is the chord length of each ring at that y,
# 2 [ sqrt(r_(j+1)^2 - y^2) - sqrt(r_j^2 - y^2) ] (taking 0 for a negative square root). Writing the
# matrix for the actual pixel offsets means the photo is never resampled, so no noise is blurred.

# %%
def radii(N=N_RINGS, R=R_CANDLE):
    """Ring middles r_j (mm)."""
    return (R / N) * (np.arange(N) + 0.5)


def candle_emission(r, z):
    s = 3.2 * (z / 6.0) * np.exp(1.0 - z / 6.0)          # flame radius envelope (mm)
    r0 = 0.7 * s * max(0.0, 1.0 - z / 10.0)              # radius of the glow ring (mm); 0 above z = 10 mm
    e = np.exp(-(z / 22.0) ** 2)                         # overall strength fades with height
    return e * np.exp(-((np.asarray(r, dtype=float) - r0) / (0.55 * s)) ** 2)


def photo_at(eps_fn, offsets, R=R_CANDLE, n_fine=1200):
    """Brightness at transverse offsets y (mm, any real numbers): I(y) = 2 * int eps(sqrt(y^2+u^2)) du.
    The flame is taken to end at the radius R, so lines of sight with |y| >= R see nothing."""
    out = np.zeros(len(offsets))
    for i, y in enumerate(np.abs(np.asarray(offsets, dtype=float))):
        if y >= R:
            continue
        u = np.linspace(0.0, np.sqrt(R * R - y * y), n_fine + 1)
        f = eps_fn(np.sqrt(y * y + u * u))
        out[i] = 2.0 * np.sum(0.5 * (f[1:] + f[:-1]) * np.diff(u))
    return out


def pixel_positions(N=N_RINGS):
    """Pixel columns of a full photo, in pixels from the middle one: -(N-1), ..., 0, ..., N-1."""
    return np.arange(2 * N - 1) - (N - 1.0)


def clean_candle_full(shift=0.0, N=N_RINGS, heights=range(1, 21), R=R_CANDLE):
    """Noise-free full candle photo (rows = heights in mm) whose axis is `shift` pixels right of the middle."""
    dr = R / N
    offs = (pixel_positions(N) - shift) * dr
    return np.array([photo_at(lambda r, z=z: candle_emission(r, z), offs, R) for z in heights])


def noisy(clean, frac, rng):
    """Gaussian noise of size frac * (peak of the photo)."""
    return clean + frac * clean.max() * rng.standard_normal(clean.shape)


def ring_matrix_at(offsets, N=N_RINGS, R=R_CANDLE):
    """Rows = pixels at the given offsets y (mm); columns = the N rings. Entry = chord length of the ring."""
    y = np.abs(np.asarray(offsets, dtype=float))[:, None]
    edges = (R / N) * np.arange(N + 1)
    inner = np.sqrt(np.clip(edges[None, :-1] ** 2 - y ** 2, 0.0, None))
    outer = np.sqrt(np.clip(edges[None, 1:] ** 2 - y ** 2, 0.0, None))
    return 2.0 * (outer - inner)


def smooth_invert_at(I, offsets, lam, N=N_RINGS, R=R_CANDLE):
    """Smoothed (Tikhonov) inversion of a photo whose pixels sit at arbitrary offsets y (mm)."""
    W = ring_matrix_at(offsets, N, R)
    D = np.diff(np.eye(N), n=2, axis=0)
    s = np.trace(W.T @ W) / N
    return np.linalg.solve(W.T @ W + lam * s * (D.T @ D), W.T @ np.asarray(I, dtype=float))


def rel_rms(est, truth):
    """RMS error divided by the peak of the truth."""
    return float(np.sqrt(np.mean((est - truth) ** 2)) / np.max(np.abs(truth)))


HEIGHTS = (4, 8, 12)
LAM = 3.0


def invert_full_row(row, axis, lam=LAM, both=True, N=N_RINGS, R=R_CANDLE):
    """Emission on the rings from one row of a full photo, taking the axis to be at `axis` pixels.
    both=True uses every pixel (both sides of the axis); both=False only the pixels right of the axis."""
    row = np.asarray(row, dtype=float)
    x = pixel_positions(N) if len(row) == 2 * N - 1 else np.arange(len(row)) - (len(row) - 1) / 2.0
    offs = (x - axis) * (R / N)
    keep = np.ones(len(row), dtype=bool) if both else offs >= 0.0
    return smooth_invert_at(row[keep], offs[keep], lam, N, R)


def worst_row_error(img, axis, lam=LAM, both=True, heights=HEIGHTS, N=N_RINGS, R=R_CANDLE):
    """Largest relative RMS error over the chosen heights (mm). This compares with the truth:
    it is how we GRADE an axis, never how a finder may choose it."""
    rr = radii(N, R)
    return max(rel_rms(invert_full_row(img[z - 1], axis, lam, both, N, R), candle_emission(rr, z)) for z in heights)


# %% [markdown]
# ## Step 2: what a wrong axis costs
# Invert the noise-free photo, assuming the axis is in the middle (axis = 0) while it is really
# `shift` pixels away. Even without any noise the error grows quickly with the mistake.

# %%
def axis_damage(shifts=(0.0, 0.25, 0.5, 1.0, 2.0), lam=LAM, N=N_RINGS, R=R_CANDLE):
    """Worst-row error of the noise-free inversion that wrongly assumes the axis is in the middle."""
    return {s: worst_row_error(clean_candle_full(s, N, R=R), 0.0, lam, both=False, N=N, R=R) for s in shifts}


# %% [markdown]
# ## Step 3: finder 1, the centroid
# The centre of mass of a symmetric glow lies on its axis: axis = sum(x I) / sum(I). To keep the
# far pixels, which carry only noise, from pulling on the sum, only the columns where the (smoothed,
# row-averaged) photo is above 10 percent of its peak are used. Simple, but the choice of columns
# itself moves with the noise.

# %%
def axis_centroid(img, window=0.1):
    """Axis position (pixels from the middle of the picture) as the centroid of the photo."""
    img = np.atleast_2d(np.asarray(img, dtype=float))
    n = img.shape[1]
    x = np.arange(n) - (n - 1) / 2.0
    m = np.convolve(img.mean(axis=0), np.ones(5) / 5.0, mode="same")
    keep = m > window * m.max()
    w = img[:, keep].sum(axis=0)
    total = w.sum()
    if not np.isfinite(total) or total <= 0.0:
        raise ValueError("the photo has no light to take a centroid of")
    return float(np.sum(w * x[keep]) / total)


# %% [markdown]
# ## Step 4: finder 2, match the photo with its mirror image
# If the axis is at c, the picture reflected about c must look like the picture itself:
# I(2c - x) = I(x). Slide c and measure the mismatch,
#
#     cost(c) = mean over x of [ I(x) - I(2c - x) ]^2,
#
# and take the c where it is smallest; refine it with a parabola through the lowest points.
# There is a trap: I(2c - x) falls between pixels and must be interpolated, and interpolation
# averages two noisy pixels, which lowers the noise *more at some c than at others*. The cost then
# prefers those c (a "pixel locking" artefact, about 0.2 pixel of scatter here). Smoothing the photo
# first with a Gaussian of a few pixels makes neighbouring pixels alike, so the interpolation no
# longer changes the noise much, while the axis position of a smooth glow is not changed.

# %%
def mirror_cost(img, c, blur=2.0):
    """Mean squared mismatch between the (smoothed) photo and its mirror image about c (pixels)."""
    img = np.atleast_2d(np.asarray(img, dtype=float))
    n = img.shape[1]
    x = np.arange(n) - (n - 1) / 2.0
    pad = int(np.ceil(3 * blur))
    k = np.arange(-pad, pad + 1)
    g = np.exp(-0.5 * (k / blur) ** 2)
    g /= g.sum()
    sm = np.array([np.convolve(r, g, mode="same") for r in img])
    half = (n - 1) / 2.0 - pad                      # columns nearer the edge are spoiled by the blur
    use = np.abs(x) <= half
    mirrored = 2.0 * c - x[use]
    ok = np.abs(mirrored) <= half
    if ok.sum() < 8:
        raise ValueError("axis position too far from the middle of the picture")
    refl = np.array([np.interp(mirrored[ok], x, r) for r in sm])
    return float(np.mean((sm[:, use][:, ok] - refl) ** 2))


def axis_mirror(img, blur=2.0, search=3.0, steps=121):
    """Axis position (pixels from the middle of the picture) by mirror matching, all rows together."""
    grid = np.linspace(-search, search, steps)
    cost = np.array([mirror_cost(img, c, blur) for c in grid])
    j = int(np.argmin(cost))
    if j < 3 or j > steps - 4:
        raise ValueError("no axis found inside the search range; widen `search`")
    sl = slice(max(0, j - 6), min(steps, j + 7))
    a, b, _ = np.polyfit(grid[sl], cost[sl], 2)
    return float(-b / (2.0 * a)) if a > 0 else float(grid[j])


# %% [markdown]
# ## Step 5: invert with the axis found, using both halves
# Once the axis is known to a small fraction of a pixel, every pixel of the photo, on both
# sides, has a known offset from it, and `smooth_invert_at` uses all of them at once. Each half
# carries its own independent noise, so using both lowers the noise of the answer by about
# a factor sqrt(2) compared with one half.

# %%
METHODS = {
    "assume the axis is in the middle (one half)": lambda img, s: worst_row_error(img, 0.0, both=False),
    "centroid axis, both halves": lambda img, s: worst_row_error(img, axis_centroid(img), both=True),
    "mirror axis, one half": lambda img, s: worst_row_error(img, axis_mirror(img), both=False),
    "mirror axis, both halves": lambda img, s: worst_row_error(img, axis_mirror(img), both=True),
    "true axis, both halves (not known in practice)": lambda img, s: worst_row_error(img, s, both=True),
}


def compare_axis_methods(shift=1.0, frac=0.03, n_draws=20, seed=0):
    """Worst-row error of each way of treating the axis on n_draws noise draws of a candle photo whose
    true axis is `shift` pixels off centre, plus the axis error of both finders."""
    clean = clean_candle_full(shift)
    rng = np.random.default_rng(seed)
    res = {k: [] for k in METHODS}
    res["centroid axis error (pixels)"] = []
    res["mirror axis error (pixels)"] = []
    for _ in range(n_draws):
        img = noisy(clean, frac, rng)
        for name, rule in METHODS.items():
            res[name].append(rule(img, shift))
        res["centroid axis error (pixels)"].append(axis_centroid(img) - shift)
        res["mirror axis error (pixels)"].append(axis_mirror(img) - shift)
    return {k: np.array(v) for k, v in res.items()}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    N, dr = N_RINGS, R_CANDLE / N_RINGS
    rng = np.random.default_rng(5)
    shift = 1.0
    clean = clean_candle_full(shift)
    img = noisy(clean, 0.03, rng)

    print("noise-free damage of assuming the axis is in the middle (worst-row error, lam = 3):")
    dmg = axis_damage()
    for s, e in dmg.items():
        print(f"  axis {s:4.2f} pixel off ({s * dr:.3f} mm): {e:.3f}")
    print(f"one noisy photo (3%), axis really {shift} pixel off: centroid says {axis_centroid(img):+.3f}, mirror matching says {axis_mirror(img):+.3f}")

    # figure 1: photo, cost curve, finders over 20 draws, damage
    grid = np.linspace(-3, 3, 121)
    cost = np.array([mirror_cost(img, c) for c in grid])
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8))
    ax = axes[0, 0]
    xp = pixel_positions(N)
    ax.imshow(img[::-1], extent=[xp[0] - 0.5, xp[-1] + 0.5, 1, 20], origin="upper", cmap="inferno", aspect="auto")
    ax.axvline(0, color="w", ls=":", lw=1.5, label="middle of the picture")
    ax.axvline(shift, color="#7fd6ff", lw=2, label="true axis")
    ax.axvline(axis_mirror(img), color="#ffd24a", ls="--", lw=2, label="mirror estimate")
    ax.set_xlabel("pixel column (from the middle)")
    ax.set_ylabel("height z (mm)")
    ax.set_title("Full photo, 3% noise, axis 1 pixel right of the middle", fontsize=10)
    ax.legend(fontsize=7, loc="upper right")
    ax = axes[0, 1]
    ax.plot(grid, cost, color="#003f7f", lw=2)
    ax.axvline(shift, color="k", ls=":", label="true axis")
    ax.axvline(axis_mirror(img), color="#c86a00", ls="--", lw=2, label="minimum of the cost")
    ax.set_xlabel("trial axis position c (pixels)")
    ax.set_ylabel("mismatch with the mirror image (a.u.^2)")
    ax.set_title("Mirror matching: cost against c", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    ax = axes[1, 0]
    shifts = (-2.0, -1.0, 0.0, 0.5, 1.0, 2.0)
    ec, em = [], []
    for s in shifts:
        cl = clean_candle_full(s)
        r2 = np.random.default_rng(20 + int(10 * s))
        pairs = [(axis_centroid(im_) - s, axis_mirror(im_) - s) for im_ in (noisy(cl, 0.03, r2) for _ in range(20))]
        ec.append([p[0] for p in pairs])
        em.append([p[1] for p in pairs])
    pos = np.arange(len(shifts))
    ax.boxplot(ec, positions=pos - 0.18, widths=0.3, patch_artist=True, boxprops=dict(facecolor="#f4c58a"), medianprops=dict(color="k"))
    ax.boxplot(em, positions=pos + 0.18, widths=0.3, patch_artist=True, boxprops=dict(facecolor="#8fb7e6"), medianprops=dict(color="k"))
    ax.axhline(0, color="k", lw=0.8)
    ax.axhspan(-0.3, 0.3, color="g", alpha=0.08)
    ax.set_xticks(pos)
    ax.set_xticklabels([f"{s:+.1f}" for s in shifts])
    ax.set_xlabel("true axis position (pixels from the middle)")
    ax.set_ylabel("axis error (pixels)")
    ax.set_title("20 noise draws each: centroid (orange) and mirror (blue); green band: 0.3 pixel", fontsize=9)
    ax.grid(alpha=0.3)
    ax = axes[1, 1]
    sl = list(dmg)
    ax.plot([s * dr for s in sl], [dmg[s] for s in sl], "o-", color="#d81b60", lw=2, label="assumed middle, noise-free")
    ax.axhline(0.05, color="k", ls="--", lw=1)
    ax.set_xlabel("how far the real axis is from the middle (mm)")
    ax.set_ylabel("worst-row error / peak")
    ax.set_title("A wrong axis costs about as much as 3% noise at 1 pixel", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "find_axis.png", dpi=110)

    # mini-project: shift of 1 pixel, 20 draws
    res = compare_axis_methods(1.0, 0.03, 20, seed=0)
    print("\n20 noise draws, 3% noise, axis 1 pixel (0.15 mm) off centre, lam = 3, heights 4, 8, 12 mm:")
    print(f"{'treatment of the axis':50s} {'mean':>6s} {'median':>7s} {'max':>6s}  draws <= 0.045")
    names = [k for k in res if "axis error" not in k]
    for k in names:
        v = res[k]
        print(f"{k:50s} {v.mean():6.3f} {np.median(v):7.3f} {v.max():6.3f}  {int(np.sum(v <= 0.045)):2d} of 20")
    for k in ("centroid axis error (pixels)", "mirror axis error (pixels)"):
        v = res[k]
        print(f"{k}: mean {v.mean():+.3f}, sd {v.std():.3f}, largest {np.abs(v).max():.3f}")

    fig2, axes2 = plt.subplots(1, 2, figsize=(11.5, 4.4))
    ax = axes2[0]
    rr = radii(N)
    z = 8
    ax.plot(rr, candle_emission(rr, z), "k", lw=2, label="truth")
    ax.plot(rr, invert_full_row(img[z - 1], 0.0, both=False), color="#d81b60", label="middle assumed, one half")
    ax.plot(rr, invert_full_row(img[z - 1], axis_mirror(img), both=True), color="#003f7f", lw=2, label="mirror axis, both halves")
    ax.set_ylim(-0.5, 1.4)
    ax.set_xlabel("radius r (mm)")
    ax.set_ylabel("emission (a.u. per mm)")
    ax.set_title("Height 8 mm, axis 1 pixel off, 3% noise", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    ax = axes2[1]
    ax.boxplot([res[k] for k in names], showmeans=True)
    ax.set_xticks(range(1, len(names) + 1))
    ax.set_xticklabels(["middle\nassumed,\none half", "centroid,\nboth halves", "mirror,\none half", "mirror,\nboth halves", "true axis,\nboth halves"], fontsize=7)
    ax.axhline(0.045, color="#d81b60", ls="--")
    ax.set_ylabel("worst-row error / peak (20 draws)")
    ax.set_title("Treating the axis: error over 20 noise draws", fontsize=10)
    ax.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "invert_with_axis.png", dpi=110)

# %% [markdown]
# ## Where this stops
# One steady, upright flame with a single straight axis for all heights, a camera that looks
# exactly sideways, and noise that is independent from pixel to pixel. A flame that leans or flickers has
# an axis that changes with height and time, a lens adds its own distortion, and the same photo can
# hide a true shift of the flame from an optical misalignment. Smoothing the rows along the height is
# a different improvement; that is the next milestone in `promo/roadmap.md`.
