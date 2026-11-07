"""Session 2 (Level 2): put both cameras on one pixel grid and one time base.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: one pixel grid, one time base
# **A. Real-world problem.** Camera A is 4:3 and sees the sample head-on; camera B is 16:9, looks
# from the side, and runs at a different frame rate. Before any correlation, both must be
# turned into the same kind of data: the same pixel grid and the same clock.
#
# **Plan.** (1) solve a homography from 4 point pairs, (2) warp an image with it,
# (3) cost the aspect-ratio choices, (4) measure resampling blur, (5) build Akima and Makima
# interpolation and compare them with linear and cubic spline, (6) find a timing offset.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: a homography from four point pairs
# A homography maps a flat surface seen by one camera onto the same surface seen by another:
#
#     x' = (h11 x + h12 y + h13) / (h31 x + h32 y + 1)
#     y' = (h21 x + h22 y + h23) / (h31 x + h32 y + 1)
#
# Eight unknowns (h33 is fixed to 1). Each point pair gives two equations, so four pairs give
# an 8 x 8 linear system. Multiply out the denominator and the equations become linear in h.

# %%
def homography_from_points(src, dst):
    """3x3 matrix H (h33 = 1) that maps each src point (x, y) to its dst point (u, v)."""
    src = np.asarray(src, dtype=float)
    dst = np.asarray(dst, dtype=float)
    if src.shape != (4, 2) or dst.shape != (4, 2):
        raise ValueError("need exactly four point pairs (4 x 2 arrays)")
    A = np.zeros((8, 8))
    b = np.zeros(8)
    for i in range(4):
        x, y = src[i]
        u, v = dst[i]
        A[2 * i] = [x, y, 1, 0, 0, 0, -x * u, -y * u]
        A[2 * i + 1] = [0, 0, 0, x, y, 1, -x * v, -y * v]
        b[2 * i], b[2 * i + 1] = u, v
    try:
        if np.linalg.cond(A) > 1e12:
            raise np.linalg.LinAlgError
        h = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        raise ValueError("the four points are degenerate (three on a line?)") from None
    return np.append(h, 1.0).reshape(3, 3)


def apply_h(H, pts):
    """Apply a homography to an (N, 2) array of points."""
    pts = np.atleast_2d(np.asarray(pts, dtype=float))
    q = np.hstack([pts, np.ones((len(pts), 1))]) @ np.asarray(H).T
    return q[:, :2] / q[:, 2:3]


# %% [markdown]
# ## Step 2: warp an image by inverse mapping
# To build the output image we do NOT push source pixels forward (that leaves holes). For each
# OUTPUT pixel we ask: where in the source did you come from? That is H inverse. The source
# position is usually between pixels, so we read it with bilinear interpolation: a weighted
# average of the four neighbouring pixels. Pixel centres sit at integer coordinates (x = column,
# y = row). Output pixels that map outside the source are NaN ("no data").

# %%
def bilinear(img, x, y):
    """Sample img at float positions (x = column, y = row). NaN outside the image."""
    h, w = img.shape
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    inside = (x >= 0) & (x <= w - 1) & (y >= 0) & (y <= h - 1)
    xs = np.where(inside, x, 0.0)
    ys = np.where(inside, y, 0.0)
    x0 = np.clip(np.floor(xs).astype(int), 0, w - 2)
    y0 = np.clip(np.floor(ys).astype(int), 0, h - 2)
    fx, fy = xs - x0, ys - y0
    val = ((1 - fx) * (1 - fy) * img[y0, x0] + fx * (1 - fy) * img[y0, x0 + 1]
           + (1 - fx) * fy * img[y0 + 1, x0] + fx * fy * img[y0 + 1, x0 + 1])
    return np.where(inside, val, np.nan)


def warp_image(img, H, shape):
    """Image of shape (rows, cols) on the output grid; H maps source (x, y) to output (x, y)."""
    rows, cols = shape
    gy, gx = np.mgrid[0:rows, 0:cols].astype(float)
    pts = np.stack([gx.ravel(), gy.ravel()], axis=1)
    src = apply_h(np.linalg.inv(H), pts)
    return bilinear(img, src[:, 0], src[:, 1]).reshape(shape)


def resize_matrix(src_shape, dst_shape):
    """H that stretches the whole source image onto the whole destination image (corners to corners)."""
    sy, sx = dst_shape[0] / src_shape[0], dst_shape[1] / src_shape[1]
    return np.array([[sx, 0, 0.5 * sx - 0.5], [0, sy, 0.5 * sy - 0.5], [0, 0, 1.0]])


# %% [markdown]
# ## Step 3: a speckle pattern we can sample anywhere
# DIC needs a random dot pattern. We build one from 48 random cosine waves, so it can be
# evaluated at any point (no pixel grid needed) and has a typical dot size of a few pixels.

# %%
def speckle_waves(seed=7, count=48, kmin=0.35, kmax=1.2):
    rng = np.random.default_rng(seed)
    k = rng.uniform(kmin, kmax, count)
    th = rng.uniform(0, 2 * np.pi, count)
    return np.stack([k * np.cos(th), k * np.sin(th), rng.uniform(0, 2 * np.pi, count)], axis=1)


def speckle_at(waves, x, y):
    """Pattern value (mean 0, standard deviation about 1) at float positions."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    out = np.zeros(x.shape)
    for kx, ky, ph in waves:
        out += np.cos(kx * x + ky * y + ph)
    return out * np.sqrt(2.0 / len(waves))


def speckle_image(rows, cols, seed=7):
    gy, gx = np.mgrid[0:rows, 0:cols].astype(float)
    return speckle_at(speckle_waves(seed), gx, gy)


# %% [markdown]
# ## Step 4: the cost of fitting one aspect ratio into another
# Source w x h pixels, target grid W x H. Three ways to fit:
# letterbox (shrink until everything fits, leave empty bars), crop (shrink until the grid is
# full, throw away the overflow) and stretch (different scale in x and y).

# %%
def aspect_costs(src_w, src_h, grid_w, grid_h):
    """Cost of each fit as fractions: empty target pixels, lost source pixels, and x:y stretch ratio."""
    r_src, r_grid = src_w / src_h, grid_w / grid_h
    lo, hi = min(r_src, r_grid), max(r_src, r_grid)
    return {"letterbox_empty": 1.0 - lo / hi, "crop_lost": 1.0 - lo / hi, "stretch_ratio": hi / lo}


def resample_roundtrip_error(scale, size=160, seed=7):
    """Resize a speckle image by `scale` and back (bilinear both ways).
    Returns RMS difference divided by the pattern's standard deviation (0 = perfect)."""
    img = speckle_image(size, size, seed)
    small_shape = (int(round(size * scale)), int(round(size * scale)))
    s = small_shape[0] / size
    down = warp_image(img, resize_matrix(img.shape, small_shape), small_shape)
    back = warp_image(down, resize_matrix(small_shape, img.shape), img.shape)
    m = 8
    a, b = img[m:-m, m:-m], back[m:-m, m:-m]
    ok = np.isfinite(b)
    return float(np.sqrt(np.mean((a[ok] - b[ok]) ** 2)) / np.std(img)), s


def shift_std_ratio(frac, size=400, seed=1):
    """Shift white noise by `frac` pixel with bilinear sampling; ratio of std after/before."""
    img = np.random.default_rng(seed).normal(size=(size, size))
    shifted = warp_image(img, np.array([[1.0, 0, frac], [0, 1.0, 0], [0, 0, 1.0]]), img.shape)
    ok = np.isfinite(shifted)
    return float(np.std(shifted[ok]) / np.std(img[ok]))


# %% [markdown]
# ## Step 5: the time axis. Linear, cubic spline and Makima
# Camera A gives a displacement sample every 1/30 s, camera B every 1/24 s. Both go onto a
# common 120 fps timeline (120 = 4 x 30 = 5 x 24, so every real sample lands on a timeline tick).
# The values in between must be interpolated.
#
# **Makima** (modified Akima) builds a cubic Hermite curve: through every sample, with a slope
# d_i chosen at each sample. Let m_i be the slope of the straight segment from sample i to i+1.
# The slope at sample i is a weighted average of its two neighbouring segment slopes:
#
#     d_i = (w1 m_{i-1} + w2 m_i) / (w1 + w2)
#     w1 = |m_{i+1} - m_i| + |m_{i+1} + m_i| / 2
#     w2 = |m_{i-1} - m_{i-2}| + |m_{i-1} + m_{i-2}| / 2
#
# The side whose neighbouring slopes differ most gets the larger weight on the OTHER segment,
# so a bend on one side does not drag the slope. The extra |m + m'| / 2 term is the "modified"
# part: the original Akima weight is only |m' - m|, which is exactly 0 whenever two neighbouring
# slopes are equal, and then the formula cannot decide (0/0). Makima keeps the weights above
# zero unless the data are completely flat, and picks the smaller slope at a corner between a
# flat run and a rising run, so it does not overshoot. For equally spaced samples lying on a
# straight line all m are equal, so d_i = m: lines are reproduced exactly.

# %%
def _extend_slopes(m):
    """Segment slopes m_0..m_{n-2} extended by two ghost slopes at each end (linear extrapolation)."""
    n = len(m) + 1
    e = np.empty(n + 3)
    e[2:n + 1] = m
    e[1] = 2 * m[0] - m[1]
    e[0] = 2 * e[1] - m[0]
    e[n + 1] = 2 * m[-1] - m[-2]
    e[n + 2] = 2 * e[n + 1] - m[-1]
    return e


def akima_slopes(x, y, modified=True):
    """Slopes at every sample for Akima (modified=False) or Makima (modified=True)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    m = np.diff(y) / np.diff(x)
    if n == 2:
        return np.array([m[0], m[0]])
    e = _extend_slopes(m)
    # for sample i the four slopes m_{i-2}, m_{i-1}, m_i, m_{i+1} sit at e[i], e[i+1], e[i+2], e[i+3]
    m2, m1, p0, p1 = e[0:n], e[1:n + 1], e[2:n + 2], e[3:n + 3]
    w1 = np.abs(p1 - p0)
    w2 = np.abs(m1 - m2)
    if modified:
        w1 = w1 + 0.5 * np.abs(p1 + p0)
        w2 = w2 + 0.5 * np.abs(m1 + m2)
    tot = w1 + w2
    safe = np.where(tot > 0, tot, 1.0)
    return np.where(tot > 0, (w1 * m1 + w2 * p0) / safe, 0.5 * (m1 + p0))


def hermite_eval(x, y, d, xq, deriv=0, extrapolate=False):
    """Piecewise cubic Hermite curve through (x, y) with slopes d. deriv = 0, 1 or 2.
    Outside [x[0], x[-1]] the result is NaN unless extrapolate=True (then the end cubic continues)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    xq = np.asarray(xq, dtype=float)
    i = np.clip(np.searchsorted(x, xq, side="right") - 1, 0, len(x) - 2)
    h = x[i + 1] - x[i]
    t = (xq - x[i]) / h
    y0, y1, d0, d1 = y[i], y[i + 1], d[i], d[i + 1]
    if deriv == 0:
        out = ((2 * t**3 - 3 * t**2 + 1) * y0 + (t**3 - 2 * t**2 + t) * h * d0
               + (-2 * t**3 + 3 * t**2) * y1 + (t**3 - t**2) * h * d1)
    elif deriv == 1:
        out = ((6 * t**2 - 6 * t) * y0 / h + (3 * t**2 - 4 * t + 1) * d0
               + (-6 * t**2 + 6 * t) * y1 / h + (3 * t**2 - 2 * t) * d1)
    else:
        out = ((12 * t - 6) * y0 / h**2 + (6 * t - 4) * d0 / h
               + (-12 * t + 6) * y1 / h**2 + (6 * t - 2) * d1 / h)
    if not extrapolate:
        out = np.where((xq < x[0]) | (xq > x[-1]), np.nan, out)
    return out


def makima(x, y, xq, deriv=0, extrapolate=False):
    return hermite_eval(x, y, akima_slopes(x, y, True), xq, deriv, extrapolate)


def akima(x, y, xq, deriv=0, extrapolate=False):
    return hermite_eval(x, y, akima_slopes(x, y, False), xq, deriv, extrapolate)


def spline_second_derivs(x, y):
    """Second derivatives of the not-a-knot cubic spline (the Matlab default 'spline')."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    h = np.diff(x)
    dl = np.diff(y) / h
    A = np.zeros((n, n))
    r = np.zeros(n)
    A[0, 0:3] = [h[1], -(h[0] + h[1]), h[0]]
    A[n - 1, n - 3:n] = [h[n - 2], -(h[n - 3] + h[n - 2]), h[n - 3]]
    for i in range(1, n - 1):
        A[i, i - 1:i + 2] = [h[i - 1], 2 * (h[i - 1] + h[i]), h[i]]
        r[i] = 6 * (dl[i] - dl[i - 1])
    return np.linalg.solve(A, r)


def spline(x, y, xq, extrapolate=False):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    xq = np.asarray(xq, dtype=float)
    M = spline_second_derivs(x, y)
    i = np.clip(np.searchsorted(x, xq, side="right") - 1, 0, len(x) - 2)
    h = x[i + 1] - x[i]
    a, b = x[i + 1] - xq, xq - x[i]
    out = (M[i] * a**3 / (6 * h) + M[i + 1] * b**3 / (6 * h)
           + (y[i] / h - M[i] * h / 6) * a + (y[i + 1] / h - M[i + 1] * h / 6) * b)
    if not extrapolate:
        out = np.where((xq < x[0]) | (xq > x[-1]), np.nan, out)
    return out


def linear(x, y, xq, extrapolate=False):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    xq = np.asarray(xq, dtype=float)
    i = np.clip(np.searchsorted(x, xq, side="right") - 1, 0, len(x) - 2)
    t = (xq - x[i]) / (x[i + 1] - x[i])
    out = (1 - t) * y[i] + t * y[i + 1]
    if not extrapolate:
        out = np.where((xq < x[0]) | (xq > x[-1]), np.nan, out)
    return out


METHODS = {"linear": linear, "spline": spline, "akima": akima, "makima": makima}


def interpolate(method, t, y, tq, extrapolate=False):
    """Resample the series (t, y) at times tq with 'linear', 'spline', 'akima' or 'makima'."""
    return METHODS[method](t, y, tq, extrapolate=extrapolate)


# %% [markdown]
# ## Step 6: two motions to test with, and the error against the truth
# Smooth motion: two sine waves (pixels). Step-like motion: a 4 px jump over about 40 ms,
# the kind of thing a clamp release or a crack opening does.

# %%
def smooth_motion(t):
    t = np.asarray(t, dtype=float)
    return 2.0 * np.sin(2 * np.pi * 1.5 * t) + 0.8 * np.sin(2 * np.pi * 3.1 * t + 0.6)


def step_motion(t, t0=0.52, width=0.01, amp=4.0):
    t = np.asarray(t, dtype=float)
    return amp * 0.5 * (1 + np.tanh((t - t0) / width))


def timeline(fps=120, t_end=2.0):
    return np.arange(int(round(t_end * fps)) + 1) / fps


def camera_samples(signal, fps, t_end=2.0):
    t = np.arange(int(round(t_end * fps)) + 1) / fps
    return t, signal(t)


def rms_vs_truth(signal, method, fps, window=(0.0, 2.0), t_end=2.0, grid_fps=120):
    """RMS error (px) of a camera running at `fps`, resampled onto the common timeline,
    measured only for times inside `window` (seconds)."""
    t, y = camera_samples(signal, fps, t_end)
    tl = timeline(grid_fps, t_end)
    tl = tl[(tl >= window[0] - 1e-9) & (tl <= window[1] + 1e-9)]
    err = interpolate(method, t, y, tl) - signal(tl)
    return float(np.sqrt(np.nanmean(err**2)))


STEP_WINDOW = (0.3, 0.8)     # the part of the timeline around the jump


def max_overshoot(method, signal, fps, window=STEP_WINDOW, lo=0.0, hi=4.0, n=5001):
    """How far (px) the interpolated curve goes outside the true range [lo, hi] inside `window`."""
    t, y = camera_samples(signal, fps)
    tq = np.linspace(window[0], window[1], n)
    v = interpolate(method, t, y, tq)
    return float(max(np.nanmax(v) - hi, lo - np.nanmin(v), 0.0))


def corner_dip(method):
    """Lowest value of the curve through a flat run that turns into a ramp: y = 0 0 0 1 2 3.
    The true shape never goes below 0."""
    x = np.arange(6.0)
    y = np.array([0.0, 0.0, 0.0, 1.0, 2.0, 3.0])
    return float(np.min(interpolate(method, x, y, np.linspace(0, 5, 2001))))


# %% [markdown]
# ## Step 7: the timing offset between the cameras
# The two cameras never start on the same tick. If camera B's clock is late by tau, B's sample
# labelled t really recorded the motion at t + tau. After putting both on the 120 fps timeline
# we slide one against the other (cross-correlation) and read the lag of the best match; a
# parabola through the three points around the peak gives a fraction of a tick.

# %%
def wander_motion(t):
    t = np.asarray(t, dtype=float)
    return 3.0 * np.sin(2 * np.pi * 0.7 * t) + 2.0 * np.exp(-((t - 1.0) / 0.25) ** 2) + 1.2 * np.sin(2 * np.pi * 2.2 * t + 1.0)


def estimate_offset(tA, yA, tB, yB, method="makima", fs=120, max_lag=0.1):
    """Offset tau (s) such that B(t) = A(t + tau), from the cross-correlation of the two resampled series."""
    lo, hi = max(tA[0], tB[0]), min(tA[-1], tB[-1])
    tl = np.arange(int(np.ceil(lo * fs)), int(np.floor(hi * fs)) + 1) / fs
    a = interpolate(method, tA, yA, tl)
    b = interpolate(method, tB, yB, tl)
    K = int(round(max_lag * fs))
    N = len(tl)
    bs = b[K:N - K] - np.mean(b[K:N - K])
    c = []
    for k in range(-K, K + 1):
        as_ = a[K + k:N - K + k]
        as_ = as_ - np.mean(as_)
        c.append(float(np.dot(as_, bs) / np.sqrt(np.dot(as_, as_) * np.dot(bs, bs))))
    c = np.array(c)
    j = int(np.argmax(c))
    frac = 0.0
    if 0 < j < len(c) - 1:
        frac = 0.5 * (c[j - 1] - c[j + 1]) / (c[j - 1] - 2 * c[j] + c[j + 1])
    return (j - K + frac) / fs


def worst_gap_s(fps_a, fps_b, seconds=1.0):
    """Largest time distance from any frame of A to the nearest frame of B."""
    ta = np.arange(int(seconds * fps_a)) / fps_a
    tb = np.arange(int(seconds * fps_b) + 2) / fps_b
    return float(max(np.min(np.abs(tb - t)) for t in ta))


# %% [markdown]
# ## See it
# Four pictures: the warp, the three aspect fits, resampling blur, and the three interpolants
# on a step-like motion.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # 1. homography warp
    img = speckle_image(160, 200, seed=7)
    quad = np.array([[30, 20], [170, 35], [185, 130], [20, 140]], float)       # corners seen by camera B
    grid = np.array([[0, 0], [199, 0], [199, 159], [0, 159]], float)
    H = homography_from_points(quad, grid)
    flat = warp_image(img, H, (160, 200))
    print("homography from 4 point pairs:\n", np.round(H, 4))
    fig, ax = plt.subplots(1, 2, figsize=(8, 3.6))
    ax[0].imshow(img, cmap="gray", vmin=-3, vmax=3)
    ax[0].plot(*np.append(quad, quad[:1], axis=0).T, "r-")
    ax[0].set_title("camera view: sample is a skewed quad")
    ax[1].imshow(flat, cmap="gray", vmin=-3, vmax=3)
    ax[1].set_title("warped onto a 200 x 160 grid")
    for a in ax:
        a.set_xlabel("x (pixels)")
        a.set_ylabel("y (pixels)")
    fig.tight_layout()
    fig.savefig(OUT / "homography_warp.png", dpi=110)

    # 2. aspect fits
    costs = aspect_costs(1280, 720, 640, 480)
    print("1280 x 720 into 640 x 480:", {k: round(v, 4) for k, v in costs.items()})
    fig, ax = plt.subplots(1, 3, figsize=(9, 2.9))
    for a, name in zip(ax, ("letterbox", "crop", "stretch")):
        a.add_patch(plt.Rectangle((0, 0), 640, 480, fc="#dddddd", ec="k"))
        if name == "letterbox":
            a.add_patch(plt.Rectangle((0, 60), 640, 360, fc="#4c78a8"))
            a.set_title(f"letterbox: {costs['letterbox_empty']:.0%} of grid empty")
        elif name == "crop":
            a.add_patch(plt.Rectangle((0, 0), 640, 480, fc="#4c78a8"))
            a.set_title(f"crop: {costs['crop_lost']:.0%} of source lost")
        else:
            a.add_patch(plt.Rectangle((0, 0), 640, 480, fc="#4c78a8"))
            a.set_title(f"stretch: y scaled {costs['stretch_ratio']:.2f}x more than x")
        a.set_xlim(-20, 660)
        a.set_ylim(500, -20)
        a.set_aspect("equal")
        a.set_xlabel("grid x (pixels)")
        a.set_ylabel("grid y (pixels)")
    fig.tight_layout()
    fig.savefig(OUT / "aspect_fits.png", dpi=110)

    # 3. resampling blur
    scales = [0.5, 0.6, 0.75, 0.9, 1.0, 1.25, 1.5, 2.0]
    errs = []
    for s in scales:
        e, s_eff = resample_roundtrip_error(s)
        errs.append(e)
        print(f"scale {s:4.2f}: round-trip error {e:.3f} of the pattern std")
    for f in (0.0, 0.25, 0.5):
        print(f"shift {f:.2f} px: std ratio {shift_std_ratio(f):.4f} (theory {np.hypot(1 - f, f):.4f})")
    fig, ax = plt.subplots(figsize=(5.5, 3.6))
    ax.plot(scales, errs, "o-")
    ax.set_xlabel("scale factor (output size / input size)")
    ax.set_ylabel("round-trip RMS error / pattern std")
    ax.set_title("Bilinear resampling loses detail")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "resample_error.png", dpi=110)

    # 4. interpolants on a step-like motion
    tA, yA = camera_samples(step_motion, 24)
    tq = np.linspace(STEP_WINDOW[0], STEP_WINDOW[1], 600)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(tq, step_motion(tq), "k", lw=2, label="truth")
    for name, col in (("linear", "tab:green"), ("spline", "tab:red"), ("makima", "tab:blue")):
        ax.plot(tq, interpolate(name, tA, yA, tq), color=col, label=name)
    sel = (tA >= 0.3) & (tA <= 0.8)
    ax.plot(tA[sel], yA[sel], "ko", ms=5, label="camera B samples (24 fps)")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("displacement (px)")
    ax.set_title("Step-like motion: spline overshoots, Makima does not")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "step_interpolation.png", dpi=110)

    print("RMS error (px) on the 120 fps timeline:")
    for sig, nm, win in ((smooth_motion, "smooth", (0.0, 2.0)), (step_motion, "step-like", STEP_WINDOW)):
        for fps in (30, 24):
            row = {m: rms_vs_truth(sig, m, fps, win) for m in METHODS}
            print(f"  {nm:9s} {fps} fps:", {k: round(v, 4) for k, v in row.items()})
    for fps in (30, 24):
        print(f"  overshoot at {fps} fps (px):", {m: round(max_overshoot(m, step_motion, fps), 3) for m in METHODS})
    print("  lowest value of the corner curve:", {m: round(corner_dip(m), 4) for m in METHODS})
    tau = 0.0137
    ta, ya = camera_samples(wander_motion, 30)
    tb = np.arange(49) / 24
    yb = wander_motion(tb + tau)
    print(f"true offset {tau * 1000:.1f} ms, estimated {estimate_offset(ta, ya, tb, yb) * 1000:.2f} ms")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
