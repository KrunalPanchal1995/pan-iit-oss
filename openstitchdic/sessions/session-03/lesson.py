"""Session 3 (Level 3): a mini stereo-DIC pipeline on synthetic data, with an error budget.

Run:  python start.py 3
Your own pictures: make a folder `data` next to start.py and put view_a.png and view_b.png in it
(see the README of this session). Without them the lesson draws its own speckle pictures.
"""
# %% [markdown]
# # Session 3: align, correlate, merge, and measure the error
# **A. Real-world problem.** A flat speckled sample moves while camera A (4:3, 30 fps, almost
# head-on) and camera B (16:9, 24 fps, 28 degrees to the side) film it. We know the true motion
# because we simulate it. Can we merge both cameras into one data set and recover it? What goes
# wrong if we skip the geometry step, or the time step?
#
# **Plan.** (1) a camera model and a speckle sheet, (2) calibrate: homography from 4 corners,
# (3) warp both cameras onto one 160 x 120 grid, (4) measure displacement with subset
# correlation (ZNCC + parabola), (5) put both time series on a 120 fps timeline with Makima,
# (6) compare with the truth and break things on purpose.

# %%
import math
import pathlib
import warnings
from functools import lru_cache

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
# your own pictures go in <repo folder>/data (next to start.py); in Colab: a folder named data
DATA_DIR = (pathlib.Path(__file__).resolve().parents[2] if "__file__" in globals() else pathlib.Path(".")) / "data"

GRID_W, GRID_H = 160, 120          # the common grid: 1 pixel = 1 unit of the sheet
DURATION = 0.8                     # seconds filmed
TIMELINE_FPS = 120                 # 120 = 4 x 30 = 5 x 24
GRAD = 0.004                       # strain-like gradient of the true displacement (per unit)
OCCLUDE_SHIFT = -120.0             # slides camera B sideways so its left edge cuts off part of the sheet
CENTRES = [(x, y) for y in (30, 60, 90) for x in (40, 80, 120)]    # 9 subset centres on the grid


# %% [markdown]
# ## Step 1: geometry tools (the same ideas as Session 2, repeated so this file runs alone)

# %%
def homography_from_points(src, dst):
    """3x3 H (h33 = 1) mapping four src points to four dst points."""
    src, dst = np.asarray(src, float), np.asarray(dst, float)
    A, b = np.zeros((8, 8)), np.zeros(8)
    for i in range(4):
        (x, y), (u, v) = src[i], dst[i]
        A[2 * i] = [x, y, 1, 0, 0, 0, -x * u, -y * u]
        A[2 * i + 1] = [0, 0, 0, x, y, 1, -x * v, -y * v]
        b[2 * i], b[2 * i + 1] = u, v
    return np.append(np.linalg.solve(A, b), 1.0).reshape(3, 3)


def affine_from_points(src, dst):
    """Best 3x3 affine matrix (last row 0 0 1) for several point pairs, by least squares:
    the 'no perspective' alternative to a homography."""
    src, dst = np.asarray(src, float), np.asarray(dst, float)
    X = np.hstack([src, np.ones((len(src), 1))])
    sol, *_ = np.linalg.lstsq(X, dst, rcond=None)
    return np.vstack([sol.T, [0.0, 0.0, 1.0]])


def apply_h(H, pts):
    pts = np.atleast_2d(np.asarray(pts, float))
    q = np.hstack([pts, np.ones((len(pts), 1))]) @ np.asarray(H).T
    return q[:, :2] / q[:, 2:3]


def bilinear(img, x, y):
    """Sample at float positions (x = column, y = row); NaN outside the picture."""
    h, w = img.shape
    inside = (x >= 0) & (x <= w - 1) & (y >= 0) & (y <= h - 1)
    xs, ys = np.where(inside, x, 0.0), np.where(inside, y, 0.0)
    x0, y0 = np.clip(np.floor(xs).astype(int), 0, w - 2), np.clip(np.floor(ys).astype(int), 0, h - 2)
    fx, fy = xs - x0, ys - y0
    v = ((1 - fx) * (1 - fy) * img[y0, x0] + fx * (1 - fy) * img[y0, x0 + 1]
         + (1 - fx) * fy * img[y0 + 1, x0] + fx * fy * img[y0 + 1, x0 + 1])
    return np.where(inside, v, np.nan)


def warp_image(img, H, shape):
    """Output picture of `shape`; H maps source pixel positions to output pixel positions."""
    gy, gx = np.mgrid[0:shape[0], 0:shape[1]].astype(float)
    src = apply_h(np.linalg.inv(H), np.stack([gx.ravel(), gy.ravel()], axis=1))
    return bilinear(img, src[:, 0], src[:, 1]).reshape(shape)


def resize_matrix(src_shape, dst_shape):
    sy, sx = dst_shape[0] / src_shape[0], dst_shape[1] / src_shape[1]
    return np.array([[sx, 0, 0.5 * sx - 0.5], [0, sy, 0.5 * sy - 0.5], [0, 0, 1.0]])


# %% [markdown]
# ## Step 2: the world we simulate
# A speckled sheet (sheet units = grid pixels). Each camera is a plane-to-plane homography
# built from a focal length f (pixels), a viewing angle and a distance, which is exactly what a
# real camera does to a flat sheet. The sheet moves by s(t) pixels along x (with a small
# gradient, so the field is not a pure shift) and by 0.4 s(t) along y.

# %%
def speckle_waves(seed=11, count=44, kmin=0.35, kmax=1.2):
    rng = np.random.default_rng(seed)
    k, th = rng.uniform(kmin, kmax, count), rng.uniform(0, 2 * np.pi, count)
    return np.stack([k * np.cos(th), k * np.sin(th), rng.uniform(0, 2 * np.pi, count)], axis=1)


WAVES = speckle_waves()


def speckle_at(x, y):
    out = np.zeros(np.shape(x))
    for kx, ky, ph in WAVES:
        out += np.cos(kx * x + ky * y + ph)
    return out * np.sqrt(2.0 / len(WAVES))


CAMS = {
    "A": {"rows": 180, "cols": 240, "fps": 30, "f": 650.0, "yaw": 3.0, "pitch": 2.0, "dist": 500.0,
          "cx": 120.0, "cy": 90.0, "gain": 1.0, "offset": 0.0},
    "B": {"rows": 180, "cols": 320, "fps": 24, "f": 600.0, "yaw": 28.0, "pitch": -6.0, "dist": 500.0,
          "cx": 160.0, "cy": 90.0, "gain": 0.8, "offset": 0.15},
}


def camera_homography(cam):
    """3x3 matrix taking sheet coordinates (X, Y), 0..160 and 0..120, to camera pixels (x, y)."""
    a, b = math.radians(cam["yaw"]), math.radians(cam["pitch"])
    Ry = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(b), -math.sin(b)], [0, math.sin(b), math.cos(b)]])
    R = Ry @ Rx
    K = np.array([[cam["f"], 0, cam["cx"]], [0, cam["f"], cam["cy"]], [0, 0, 1.0]])
    M = K @ np.column_stack([R[:, 0], R[:, 1], [0, 0, cam["dist"]]])
    return M @ np.array([[1, 0, -GRID_W / 2], [0, 1, -GRID_H / 2], [0, 0, 1.0]])


def motion_smooth(t):
    t = np.asarray(t, float)
    return 2.0 * np.sin(2 * np.pi * 1.5 * t) + 0.8 * np.sin(2 * np.pi * 3.1 * t)


def motion_step(t):
    t = np.asarray(t, float)
    return 4.0 * 0.5 * (1 + np.tanh((t - 0.52) / 0.01))


PROFILES = {"smooth": motion_smooth, "step": motion_step}


def true_displacement(s, centres=CENTRES):
    """True (ux, uy) in grid pixels at each subset centre for motion amplitudes s: shape (len(s), len(centres), 2)."""
    s = np.atleast_1d(np.asarray(s, float))
    cx = np.array([c[0] for c in centres], float)
    ux = s[:, None] * (1 + GRAD * (cx[None, :] - GRID_W / 2))
    uy = 0.4 * s[:, None] * np.ones_like(cx)[None, :]
    return np.stack([ux, uy], axis=2)


def render_frame(cam, s, noise=0.02, seed=0):
    """Camera picture of the sheet after it moved by amplitude s."""
    gy, gx = np.mgrid[0:cam["rows"], 0:cam["cols"]].astype(float)
    sheet = apply_h(np.linalg.inv(camera_homography(cam)), np.stack([gx.ravel(), gy.ravel()], axis=1))
    Xc, Yc = sheet[:, 0], sheet[:, 1]
    Xr = (Xc - s + (GRID_W / 2) * s * GRAD) / (1 + s * GRAD)      # where this material point started
    Yr = Yc - 0.4 * s
    img = (speckle_at(Xr, Yr) * cam["gain"] + cam["offset"]).reshape(cam["rows"], cam["cols"])
    return img + np.random.default_rng(seed).normal(0, noise, img.shape)


# %% [markdown]
# ## Step 3: put every camera on the common grid
# We "click" the four sheet corners in each camera picture (with a small click error) and
# solve the homography from camera pixels to grid pixels. Alternatives we will compare later:
# an affine fit (no perspective) and a plain resize of the whole picture to the grid size.

# %%
@lru_cache(maxsize=None)
def camera_frames(key, profile, shift_cx=0.0):
    """(times, frames) of camera `key` filming motion `profile`. shift_cx moves the camera picture sideways."""
    cam = dict(CAMS[key])
    cam["cx"] += shift_cx
    n = int(math.floor(DURATION * cam["fps"] + 1e-9))
    t = np.arange(n) / cam["fps"]
    s = PROFILES[profile](t)
    return t, np.array([render_frame(cam, si, seed=i) for i, si in enumerate(s)])


def to_grid_matrix(key, geometry="homography", click_noise=0.3, seed=0, shift_cx=0.0):
    cam = dict(CAMS[key])
    cam["cx"] += shift_cx
    corners = np.array([[0, 0], [GRID_W - 1, 0], [GRID_W - 1, GRID_H - 1], [0, GRID_H - 1]], float)
    if geometry == "resize":
        return resize_matrix((cam["rows"], cam["cols"]), (GRID_H, GRID_W))
    pix = apply_h(camera_homography(cam), corners) + np.random.default_rng(seed).normal(0, click_noise, (4, 2))
    return homography_from_points(pix, corners) if geometry == "homography" else affine_from_points(pix, corners)


# %% [markdown]
# ## Step 4: subset correlation (ZNCC, whole pixel, then a parabola)
# Cut a (2h+1) x (2h+1) subset from the first picture. Slide it over every shift in a +-search
# window in the later picture. ZNCC (zero-normalised cross-correlation) scores each shift from
# -1 to 1 and ignores brightness and contrast changes. The best whole-pixel shift is refined
# by a parabola through the peak and its two neighbours, in x and in y.

# %%
def parabola_peak(m, z, p):
    """Sub-pixel position (-0.5..0.5) of the peak of a parabola through scores m, z, p at shifts -1, 0, +1."""
    d = m - 2 * z + p
    return 0.0 if abs(d) < 1e-12 else 0.5 * (m - p) / d


def track_subset(ref, cur, cx, cy, h=10, search=6, nan_policy="skip"):
    """Displacement (dx, dy) of the subset centred at (cx, cy) between ref and cur. NaN if undecidable."""
    r = h + search
    if cx - r < 0 or cy - r < 0 or cx + r >= cur.shape[1] or cy + r >= cur.shape[0]:
        return np.nan, np.nan                       # the search window would leave the picture
    if nan_policy == "zero":
        ref, cur = np.nan_to_num(ref), np.nan_to_num(cur)
    patch = ref[cy - h:cy + h + 1, cx - h:cx + h + 1]
    region = cur[cy - h - search:cy + h + search + 1, cx - h - search:cx + h + search + 1]
    if not (np.all(np.isfinite(patch)) and np.all(np.isfinite(region))):
        return np.nan, np.nan
    win = sliding_window_view(region, patch.shape)
    wm = win - win.mean(axis=(2, 3), keepdims=True)
    pm = patch - patch.mean()
    den = np.sqrt((wm ** 2).sum(axis=(2, 3)) * (pm ** 2).sum())
    num = (wm * pm).sum(axis=(2, 3))
    c = np.where(den > 1e-12, num / np.where(den > 1e-12, den, 1.0), 0.0)
    j, i = np.unravel_index(np.argmax(c), c.shape)
    if i in (0, c.shape[1] - 1) or j in (0, c.shape[0] - 1):
        return np.nan, np.nan                       # the peak touches the edge of the search window
    dx = i - search + parabola_peak(c[j, i - 1], c[j, i], c[j, i + 1])
    dy = j - search + parabola_peak(c[j - 1, i], c[j, i], c[j + 1, i])
    return float(dx), float(dy)


def dic_series(frames, centres=CENTRES, mode="reference", **kw):
    """Displacement of every subset in every frame: shape (frames, centres, 2).
    mode 'reference': each frame against frame 0. mode 'consecutive': frame k against k-1, then added up."""
    out = np.zeros((len(frames), len(centres), 2))
    for k in range(1, len(frames)):
        base = frames[0] if mode == "reference" else frames[k - 1]
        for n, (cx, cy) in enumerate(centres):
            d = np.array(track_subset(base, frames[k], cx, cy, **kw))
            out[k, n] = d if mode == "reference" else out[k - 1, n] + d
    return out


@lru_cache(maxsize=None)
def camera_series(key, profile, geometry="homography", dic_mode="reference", click_noise=0.3,
                  shift_cx=0.0, nan_policy="skip"):
    """(times, displacement series on the grid) of one camera, after warping to the grid."""
    t, frames = camera_frames(key, profile, shift_cx)
    H = to_grid_matrix(key, geometry, click_noise, 0, shift_cx)
    grid = [warp_image(f, H, (GRID_H, GRID_W)) for f in frames]
    return t, dic_series(grid, mode=dic_mode, nan_policy=nan_policy)


# %% [markdown]
# ## Step 5: one time base, one data set
# Each camera's displacement series is resampled to the 120 fps timeline, then the two are
# averaged where both exist. `nearest` takes the closest real sample (what you get if you
# ignore the clocks), `linear` joins the dots, `makima` is the curve from Session 2. Outside a
# camera's own time range its series is NaN (no extrapolation) and the other camera is used.

# %%
def _slopes(x, y):
    m = np.diff(y) / np.diff(x)
    n = len(x)
    e = np.empty(n + 3)
    e[2:n + 1] = m
    e[1] = 2 * m[0] - m[1]
    e[0] = 2 * e[1] - m[0]
    e[n + 1] = 2 * m[-1] - m[-2]
    e[n + 2] = 2 * e[n + 1] - m[-1]
    m2, m1, p0, p1 = e[0:n], e[1:n + 1], e[2:n + 2], e[3:n + 3]
    w1 = np.abs(p1 - p0) + 0.5 * np.abs(p1 + p0)
    w2 = np.abs(m1 - m2) + 0.5 * np.abs(m1 + m2)
    tot = w1 + w2
    return np.where(tot > 0, (w1 * m1 + w2 * p0) / np.where(tot > 0, tot, 1.0), 0.5 * (m1 + p0))


def resample(method, t, y, tq, extrapolate=False):
    """Values of the series (t, y) at tq. NaN outside [t[0], t[-1]] unless extrapolate=True."""
    t, y, tq = np.asarray(t, float), np.asarray(y, float), np.asarray(tq, float)
    if method == "nearest":
        out = y[np.argmin(np.abs(t[None, :] - tq[:, None]), axis=1)]
    else:
        i = np.clip(np.searchsorted(t, tq, side="right") - 1, 0, len(t) - 2)
        h = t[i + 1] - t[i]
        u = (tq - t[i]) / h
        if method == "linear":
            out = (1 - u) * y[i] + u * y[i + 1]
        elif method == "makima":
            d = _slopes(t, y)
            out = ((2 * u**3 - 3 * u**2 + 1) * y[i] + (u**3 - 2 * u**2 + u) * h * d[i]
                   + (-2 * u**3 + 3 * u**2) * y[i + 1] + (u**3 - u**2) * h * d[i + 1])
        else:
            raise ValueError("method must be 'nearest', 'linear' or 'makima'")
    if not extrapolate:
        out = np.where((tq < t[0] - 1e-12) | (tq > t[-1] + 1e-12), np.nan, out)
    return out


def merge_series(tA, dA, tB, dB, timeline, method):
    """Average of the two cameras on the timeline; where one camera has no data the other is used alone."""
    parts = []
    for t, d in ((tA, dA), (tB, dB)):
        r = np.full((len(timeline),) + d.shape[1:], np.nan)
        for n in range(d.shape[1]):
            for c in range(d.shape[2]):
                if np.all(np.isfinite(d[:, n, c])):
                    r[:, n, c] = resample(method, t, d[:, n, c], timeline)
        parts.append(r)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmean(np.stack(parts), axis=0)


def rms(a):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return float(np.sqrt(np.nanmean(np.square(a))))


def common_timeline(tA, tB, fps=TIMELINE_FPS):
    last = min(tA[-1], tB[-1])
    return np.arange(int(math.floor(last * fps + 1e-9)) + 1) / fps


@lru_cache(maxsize=None)
def run_pipeline(profile="smooth", geometry="homography", timing="makima", dic_mode="reference",
                 click_noise=0.3, shift_cx=0.0, nan_policy="skip"):
    """Full pipeline. Returns RMS displacement errors (grid pixels) against the known truth."""
    tA, dA = camera_series("A", profile, geometry, dic_mode, click_noise, 0.0, nan_policy)
    tB, dB = camera_series("B", profile, geometry, dic_mode, click_noise, shift_cx, nan_policy)
    tl = common_timeline(tA, tB)
    truth = true_displacement(PROFILES[profile](tl))
    merged = merge_series(tA, dA, tB, dB, tl, timing)
    tr = true_displacement(PROFILES[profile](tA))
    trb = true_displacement(PROFILES[profile](tB))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        worst = float(np.nanmax(np.abs(merged - truth)))
    return {"rms": rms(merged - truth), "max": worst, "rms_a": rms(dA - tr), "rms_b": rms(dB - trb), "timeline": tl,
            "merged": merged, "truth": truth, "valid_b": float(np.mean(np.isfinite(dB[-1, :, 0])))}


def extrapolation_error(signal, fps, frames_beyond, method="makima"):
    """Error (px) of continuing a sampled motion `frames_beyond` frame periods after its last sample."""
    t = np.arange(int(DURATION * fps)) / fps
    tq = t[-1] + frames_beyond / fps
    v = resample(method, t, signal(t), np.array([tq]), extrapolate=True)[0]
    return float(abs(v - signal(tq)))


# %% [markdown]
# ## Step 6: your own pictures, or the synthetic ones
# Put `view_a.png` (or .jpg) and `view_b.png` in the `data` folder next to start.py. Optional:
# `points.txt` with four lines `xa ya xb yb`: the same four physical points found by eye in
# picture A and picture B. With points, B is warped onto A's pixel grid with a homography; without
# them B is simply scaled and centre-cropped to the shape of A.

# %%
def to_gray(a):
    a = np.asarray(a, float)
    if a.ndim == 3:
        a = a[..., :3].mean(axis=2)
    return a / 255.0 if a.max() > 1.5 else a


def load_user_pair(folder=None):
    """(picture A, picture B, points or None) from `folder`, or None when the pictures are not there."""
    import matplotlib.image as mpimg
    folder = pathlib.Path(folder) if folder is not None else DATA_DIR
    found = []
    for stem in ("view_a", "view_b"):
        hits = [p for ext in ("png", "jpg", "jpeg") for p in folder.glob(f"{stem}.{ext}")]
        if not hits:
            return None
        found.append(to_gray(mpimg.imread(str(hits[0]))))
    pts = None
    pf = folder / "points.txt"
    if pf.exists():
        pts = np.loadtxt(pf, ndmin=2)
        if pts.shape != (4, 4):
            raise ValueError("points.txt needs 4 lines of 4 numbers: xa ya xb yb")
    return found[0], found[1], pts


def align_pair(a, b, points=None):
    """Put picture B on the pixel grid of picture A. Returns the warped B (NaN where B has no data)."""
    if points is not None:
        H = homography_from_points(points[:, 2:4], points[:, 0:2])
    else:
        s = max(a.shape[0] / b.shape[0], a.shape[1] / b.shape[1])      # fill A completely, then crop
        H = np.array([[s, 0, (a.shape[1] - 1) / 2 - s * (b.shape[1] - 1) / 2],
                      [0, s, (a.shape[0] - 1) / 2 - s * (b.shape[0] - 1) / 2], [0, 0, 1.0]])
    return warp_image(b, H, a.shape)


def get_pair(folder=None):
    """(A, B, points, where they came from): your pictures if present, else synthetic speckle pictures."""
    user = load_user_pair(folder)
    if user is not None:
        return user[0], user[1], user[2], "your pictures in the data folder"
    ta, fa = camera_frames("A", "smooth")
    tb, fb = camera_frames("B", "smooth")
    corners = np.array([[0, 0], [GRID_W - 1, 0], [GRID_W - 1, GRID_H - 1], [0, GRID_H - 1]], float)
    pa, pb = apply_h(camera_homography(CAMS["A"]), corners), apply_h(camera_homography(CAMS["B"]), corners)
    return fa[0], fb[0], np.hstack([pa, pb]), "synthetic speckle pictures made by this lesson"


def ncc(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    x, y = a[ok] - a[ok].mean(), b[ok] - b[ok].mean()
    return float(np.dot(x, y) / np.sqrt(np.dot(x, x) * np.dot(y, y)))


# %% [markdown]
# ## Mini-project: 30 fps and 24 fps, different aspect ratios, before and after
# Before: each picture only resized to the grid, frames paired by nearest time.
# After: homography to the grid and Makima in time. Same cameras, same step-like motion.

# %%
def before_after(profile="step"):
    before = run_pipeline(profile, "resize", "nearest")
    after = run_pipeline(profile, "homography", "makima")
    return before["rms"], after["rms"]


# %% [markdown]
# ## See it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    a, b, pts, source = get_pair()
    bw = align_pair(a, b, pts)
    print("pictures:", source)
    print(f"A is {a.shape[1]} x {a.shape[0]}, B is {b.shape[1]} x {b.shape[0]}; correlation of A with warped B: {ncc(a, bw):.3f}")
    fig, ax = plt.subplots(1, 3, figsize=(10, 3.2))
    for axis, im, ttl in zip(ax, (a, b, bw), ("picture A", "picture B (raw)", "B warped onto A's grid")):
        axis.imshow(im, cmap="gray")
        axis.set_title(ttl)
        axis.set_xlabel("x (pixels)")
        axis.set_ylabel("y (pixels)")
    fig.tight_layout()
    fig.savefig(OUT / "pair_on_grid.png", dpi=110)

    print("RMS displacement error (grid pixels), motion = step-like:")
    labels = []
    vals = []
    for geo in ("homography", "affine", "resize"):
        for tim in ("nearest", "makima"):
            r = run_pipeline("step", geo, tim)
            print(f"  geometry {geo:10s} timing {tim:8s}: merged {r['rms']:.3f}  (A alone {r['rms_a']:.3f}, B alone {r['rms_b']:.3f})")
            labels.append(f"{geo}\n{tim}")
            vals.append(r["rms"])
    r = run_pipeline("smooth", "homography", "makima")
    print(f"smooth motion, homography + makima: merged RMS {r['rms']:.3f} px")
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.bar(range(len(vals)), vals, color=["tab:green" if "homography\nmakima" == l else "tab:gray" for l in labels])
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_yscale("log")
    ax.set_ylabel("RMS displacement error (grid pixels)")
    ax.set_title("Skip the geometry step or the time step and the error grows")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(OUT / "error_budget.png", dpi=110)

    r = run_pipeline("step", "homography", "makima")
    rn = run_pipeline("step", "homography", "nearest")
    tA, dA = camera_series("A", "step")
    tB, dB = camera_series("B", "step")
    n = 4
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.plot(r["timeline"], r["truth"][:, n, 0], "k", lw=1.5, label="truth")
    ax.plot(r["timeline"], r["merged"][:, n, 0], color="tab:blue", label="merged, Makima")
    ax.plot(rn["timeline"], rn["merged"][:, n, 0], color="tab:red", lw=1, label="merged, nearest sample")
    ax.plot(tA, dA[:, n, 0], "o", ms=4, color="tab:green", label="camera A (30 fps)")
    ax.plot(tB, dB[:, n, 0], "s", ms=4, color="tab:orange", label="camera B (24 fps)")
    ax.set_xlim(0.35, 0.75)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("x displacement at the centre subset (px)")
    ax.set_title("Two clocks, one timeline")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "merged_timeline.png", dpi=110)

    print("consecutive-frame DIC drifts more than reference DIC (smooth motion, camera A only):")
    for mode in ("reference", "consecutive"):
        t_, d_ = camera_series("A", "smooth", "homography", mode)
        print(f"  {mode:11s}: RMS error {rms(d_ - true_displacement(motion_smooth(t_))):.3f} px")
    ob = run_pipeline("smooth", "homography", "makima", shift_cx=OCCLUDE_SHIFT)
    oz = run_pipeline("smooth", "homography", "makima", shift_cx=OCCLUDE_SHIFT, nan_policy="zero")
    print(f"occlusion: camera B sees {ob['valid_b']:.0%} of the subsets; merged RMS {ob['rms']:.3f} px (masked) versus {oz['rms']:.3f} px (NaN filled with zeros)")
    print("extrapolation error of a 24 fps series beyond its last sample (px):",
          [round(extrapolation_error(motion_smooth, 24, k), 3) for k in (1, 2, 3)])
    print("mini-project, step-like motion, error before and after: %.3f px -> %.3f px" % before_after())
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
