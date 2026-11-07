"""Session 3 (Level 3): digital image correlation on synthetic speckle images, validated.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: measuring displacement and strain from speckle images
# **A. Real-world problem.** A rubber strip is painted with random dots and pulled. Two
# photographs, before and after, are all we have. Where did each patch of dots move, and how much
# was the rubber stretched? *Digital image correlation* (DIC) answers both by matching small
# square patches ("subsets") between the images, to a fraction of a pixel.
#
# Because we make the images ourselves, we know the exact answer and can grade the method.
# Plan: (1) draw a speckle image of a known deformation, (2) match subsets, (3) turn
# displacements into strain, (4) compare with the exact values, (5) vary noise and subset size,
# (6) finish with a stereo pair of a stretched strip (the mini-project).

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: a speckle pattern that can be drawn at any position
# The pattern is a sum of round Gaussian dots at random places. Because it is a formula, we can
# evaluate it at *any* (s, t), including fractions of a pixel, so the "true" deformed image has no
# interpolation error in it. Grey level = 20 + 220 * (1 - exp(-1.5 * sum of dots)), so 20 to 240.

# %%
def make_dots(width, height, dot_sigma=1.5, density=0.11, margin=12, seed=1):
    """Random dots covering [0, width] x [0, height] plus a margin. Returns (array of s, t, strength; dot size)."""
    rng = np.random.default_rng(seed)
    n = int(density * (width + 2 * margin) * (height + 2 * margin) / (dot_sigma ** 2 * 2.0))
    s = rng.uniform(-margin, width + margin, n)
    t = rng.uniform(-margin, height + margin, n)
    a = rng.uniform(0.5, 1.0, n)
    return np.stack([s, t, a], axis=1), dot_sigma


def texture(dots, s, t):
    """Grey level of the pattern at material coordinates (s, t) (arrays of the same shape)."""
    pts, sig = dots
    s = np.asarray(s, float)
    t = np.asarray(t, float)
    total = np.zeros(s.shape)
    flat_s, flat_t, out = s.ravel(), t.ravel(), total.reshape(-1)
    for k in range(0, len(flat_s), 4000):
        ds = flat_s[k:k + 4000, None] - pts[None, :, 0]
        dt = flat_t[k:k + 4000, None] - pts[None, :, 1]
        out[k:k + 4000] = (pts[None, :, 2] * np.exp(-(ds * ds + dt * dt) / (2 * sig * sig))).sum(axis=1)
    return 20.0 + 220.0 * (1.0 - np.exp(-1.5 * total))


# %% [markdown]
# ## Step 2: a deformation with a known strain
# Material point X = (x, y) moves to x + u(X). We choose a stretch in x with a small curvature
# (so strain is not exactly uniform) and a sideways contraction like rubber (Poisson ratio 0.45):
#
#     u = a (x - xc) + b (x - xc)^2        v = -nu a (y - yc)
#
# Exact strain: e_xx = a + 2 b (x - xc),  e_yy = -nu a.
# To draw the deformed image we need, for each deformed pixel, the material point that landed
# there: we solve x_def = X + u(X) for X by repeating X <- x_def - u(X).

# %%
A_STRAIN, B_CURVE, NU = 0.02, 1.0e-4, 0.45
SIZE = 160                       # image is SIZE x SIZE pixels; centre (80, 80)
CENTRE = SIZE / 2.0


def displacement(x, y, a=A_STRAIN, b=B_CURVE, nu=NU):
    return a * (x - CENTRE) + b * (x - CENTRE) ** 2, -nu * a * (y - CENTRE)


def exact_strain(x, y, a=A_STRAIN, b=B_CURVE, nu=NU):
    """Exact (e_xx, e_yy) of the displacement field above (small strain, dimensionless)."""
    return a + 2 * b * (x - CENTRE) + 0 * y, -nu * a + 0 * x


def render(dots, size=SIZE, deformed=True, a=A_STRAIN, b=B_CURVE, noise=0.0, seed=0):
    """Grey image of the specimen, undeformed or deformed, with optional camera noise (grey levels)."""
    yy, xx = np.mgrid[0:size, 0:size].astype(float)
    if deformed:
        X, Y = xx.copy(), yy.copy()
        for _ in range(30):
            u, v = displacement(X, Y, a, b)
            X, Y = xx - u, yy - v
    else:
        X, Y = xx, yy
    img = texture(dots, X, Y)
    if noise > 0:
        img = img + np.random.default_rng(seed).normal(0.0, noise, img.shape)
    return img


# %% [markdown]
# ## Step 3: sub-pixel sampling and subset matching
# To compare at fractions of a pixel we need grey levels *between* pixels: cubic convolution
# interpolation (a 4 x 4 neighbourhood). Then, for a subset of (2h+1)^2 pixels centred on (x0, y0):
# (a) brute-force search over whole-pixel shifts for the best zero-normalised cross-correlation
# (ZNCC), (b) refine to a fraction of a pixel by Gauss-Newton steps on the zero-normalised
# sum of squared differences, which only needs the gradient of the reference subset.

# %%
def _keys(t):
    a = -0.5
    t = np.abs(t)
    return np.where(t <= 1, (a + 2) * t ** 3 - (a + 3) * t ** 2 + 1,
                    np.where(t < 2, a * t ** 3 - 5 * a * t ** 2 + 8 * a * t - 4 * a, 0.0))


def sample(img, x, y):
    """Grey level of `img` at fractional pixel positions (x = column, y = row), cubic convolution."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    x0 = np.floor(x).astype(int)
    y0 = np.floor(y).astype(int)
    out = np.zeros(x.shape)
    for j in range(-1, 3):
        wy = _keys(y - (y0 + j))
        yi = np.clip(y0 + j, 0, img.shape[0] - 1)
        for i in range(-1, 3):
            wx = _keys(x - (x0 + i))
            xi = np.clip(x0 + i, 0, img.shape[1] - 1)
            out += wx * wy * img[yi, xi]
    return out


def zncc(f, g):
    """Zero-normalised cross-correlation of two equal-shape patches: 1 = identical up to brightness and contrast."""
    f = f - f.mean()
    g = g - g.mean()
    den = np.sqrt((f * f).sum() * (g * g).sum())
    return float((f * g).sum() / den) if den > 0 else 0.0


def track_subset(ref, cur, x0, y0, h=10, search=6, iters=25, guess=(0, 0)):
    """Displacement (u, v) in pixels of the subset centred at integer pixel (x0, y0). Returns (u, v, best whole-pixel zncc).

    The shape function is affine: a point at offset (dx, dy) from the centre moves to
    (dx, dy) + (u, v) + (ux dx + uy dy, vx dx + vy dy), so a stretched subset is matched fairly.
    `guess` = (gu, gv) whole pixels: centre of the search window, for large known shifts (stereo disparity).
    """
    dy, dx = np.mgrid[-h:h + 1, -h:h + 1]
    f = ref[y0 - h:y0 + h + 1, x0 - h:x0 + h + 1]
    best, bu, bv = -2.0, 0, 0
    for sv in range(-search, search + 1):
        for su in range(-search, search + 1):
            ys, xs = y0 - h + sv + guess[1], x0 - h + su + guess[0]
            if ys < 0 or xs < 0 or ys + 2 * h + 1 > cur.shape[0] or xs + 2 * h + 1 > cur.shape[1]:
                continue
            c = zncc(f, cur[ys:ys + 2 * h + 1, xs:xs + 2 * h + 1])
            if c > best:
                best, bu, bv = c, su + guess[0], sv + guess[1]
    gy, gx = np.gradient(ref.astype(float))
    fx = gx[y0 - h:y0 + h + 1, x0 - h:x0 + h + 1].ravel()
    fy = gy[y0 - h:y0 + h + 1, x0 - h:x0 + h + 1].ravel()
    ddx, ddy = dx.ravel().astype(float), dy.ravel().astype(float)
    fs = np.sqrt(((f - f.mean()) ** 2).sum())
    if fs < 1e-9:                                            # blank patch: nothing to follow
        return float("nan"), float("nan"), 0.0
    fn = ((f - f.mean()) / fs).ravel()
    J = np.stack([fx, fy, fx * ddx, fx * ddy, fy * ddx, fy * ddy], axis=1) / fs
    H = J.T @ J
    M = np.array([[1.0, 0.0, bu], [0.0, 1.0, bv], [0.0, 0.0, 1.0]])   # warp matrix, translation start
    for _ in range(iters):
        wx = M[0, 0] * ddx + M[0, 1] * ddy + M[0, 2]
        wy = M[1, 0] * ddx + M[1, 1] * ddy + M[1, 2]
        g = sample(cur, x0 + wx, y0 + wy)
        gn = (g - g.mean()) / np.sqrt(((g - g.mean()) ** 2).sum())
        d = np.linalg.solve(H, J.T @ (gn - fn))
        D = np.array([[1.0 + d[2], d[3], d[0]], [d[4], 1.0 + d[5], d[1]], [0.0, 0.0, 1.0]])
        M = M @ np.linalg.inv(D)
        if abs(M[0, 2] - bu) > 2 or abs(M[1, 2] - bv) > 2:      # diverged (subset too small or too flat)
            return float(bu), float(bv), best
        if np.abs(d[:2]).max() < 1e-4 and np.abs(d[2:]).max() < 1e-5:
            break
    return float(M[0, 2]), float(M[1, 2]), best


# %% [markdown]
# ## Step 4: displacement field on a grid, then strain
# Strain is the *slope* of displacement. Differencing two noisy neighbours amplifies noise, so we
# fit a plane to the displacements in a small window of grid points (least squares) and take its
# slope: e_xx = du/dx, e_yy = dv/dy.

# %%
def displacement_grid(ref, cur, h=10, step=8, margin=22, search=6):
    """Track subsets on a regular grid. Returns xs, ys (pixel centres) and U, V arrays (pixels)."""
    xs = np.arange(margin, ref.shape[1] - margin + 1, step)
    ys = np.arange(margin, ref.shape[0] - margin + 1, step)
    U = np.zeros((len(ys), len(xs)))
    V = np.zeros_like(U)
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            U[j, i], V[j, i], _ = track_subset(ref, cur, int(x), int(y), h, search)
    return xs, ys, U, V


def strain_from_grid(xs, ys, U, V, window=2):
    """Least-squares plane fit in a (2*window+1)^2 block of grid points. Returns (e_xx, e_yy) on interior points."""
    k = np.arange(-window, window + 1)
    kx, ky = np.meshgrid(k, k)
    A = np.stack([np.ones(kx.size), kx.ravel(), ky.ravel()], axis=1)
    pinv = np.linalg.pinv(A)
    dxp, dyp = float(xs[1] - xs[0]), float(ys[1] - ys[0])
    ny, nx = U.shape
    exx = np.full((ny - 2 * window, nx - 2 * window), np.nan)
    eyy = np.full_like(exx, np.nan)
    for j in range(window, ny - window):
        for i in range(window, nx - window):
            pu = pinv @ U[j - window:j + window + 1, i - window:i + window + 1].ravel()
            pv = pinv @ V[j - window:j + window + 1, i - window:i + window + 1].ravel()
            exx[j - window, i - window] = pu[1] / dxp
            eyy[j - window, i - window] = pv[2] / dyp
    return exx, eyy


def rms(a):
    a = np.asarray(a)
    return float(np.sqrt(np.mean(a * a)))


def run_dic(noise=0.0, h=10, step=8, window=2, seed=3):
    """Whole pipeline on the standard test: returns a dict with the grid, measured and exact fields."""
    dots = make_dots(SIZE, SIZE, seed=1)
    ref = render(dots, deformed=False, noise=noise, seed=seed)
    cur = render(dots, deformed=True, noise=noise, seed=seed + 1)
    xs, ys, U, V = displacement_grid(ref, cur, h=h, step=step)
    Xg, Yg = np.meshgrid(xs.astype(float), ys.astype(float))
    ue, ve = displacement(Xg, Yg)           # a subset starts at a reference point, so the exact value is taken there
    exx, eyy = strain_from_grid(xs, ys, U, V, window)
    sl = slice(window, -window)
    ex_e, ey_e = exact_strain(Xg[sl, sl], Yg[sl, sl])
    return dict(xs=xs, ys=ys, U=U, V=V, ue=ue, ve=ve, exx=exx, eyy=eyy, exx_exact=ex_e, eyy_exact=ey_e, ref=ref, cur=cur)


# %% [markdown]
# ## Step 5: noise and subset size
# Prediction for the random part of the displacement error of one subset (noise sigma_n grey
# levels in each of the two images, N = (2h+1)^2 pixels, mean squared image gradient G2 in
# (grey/pixel)^2):
#
#     sigma_u = sqrt(2) * sigma_n / sqrt(N * G2)
#
# A bigger subset averages more pixels, so noise falls. But our subset model is a pure shift, and
# the displacement here curves, which adds a bias of about b * h (h + 1) / 3 pixels. So there is
# an optimum subset size: too small is noisy, too large is biased.

# %%
def predicted_noise_error(sigma_n, h, G2):
    return np.sqrt(2.0) * sigma_n / np.sqrt((2 * h + 1) ** 2 * G2)


def predicted_bias(h, b=B_CURVE):
    return b * h * (h + 1) / 3.0


def predicted_strain_noise(sigma_u, step, window):
    """Strain error from noise alone when the plane fit uses (2w+1)^2 grid points spaced `step` pixels apart
    and the point errors are independent: sigma_u / (step * (2w+1) * sqrt(w (w+1) / 3))."""
    return sigma_u / (step * (2 * window + 1) * np.sqrt(window * (window + 1) / 3.0))


def mean_gradient_sq(img):
    gy, gx = np.gradient(img.astype(float))
    return float(np.mean(gx * gx))


def error_vs_subset(noise, hs, a=A_STRAIN, b=B_CURVE, step=20, seed=5):
    """RMS error of u over a grid of subsets for each half-size in hs (the measured counterpart of the prediction)."""
    dots = make_dots(SIZE, SIZE, seed=1)
    ref = render(dots, deformed=False, noise=noise, seed=seed)
    cur = render(dots, deformed=True, a=a, b=b, noise=noise, seed=seed + 1)
    out = []
    for h in hs:
        xs, ys, U, V = displacement_grid(ref, cur, h=h, step=step, margin=34)
        Xg, Yg = np.meshgrid(xs.astype(float), ys.astype(float))
        ue, _ = displacement(Xg, Yg, a, b)
        out.append(rms(U - ue))
    return np.array(out)


# %% [markdown]
# ## Step 6: a stereo pair of a stretched strip (used by the mini-project)
# A flat strip 60 mm x 40 mm sits Z0 = 0.5 m from two parallel cameras (f = 1000 px, baseline
# B = 0.04 m). One pixel on the strip is Z0 / f = 0.5 mm. The pattern is drawn in millimetres on
# the strip. In the loaded state the strip is stretched by `exx` in x, contracts by nu * exx in y,
# and is pulled toward the cameras by `dz` metres. A material point (s, t) in mm sits at
# X = s (1 + exx), Y = t (1 - nu exx), Z = Z0 - dz; camera 1 (at x = 0) sees u = f X / Z + cx
# and camera 2 (at x = B) sees u = f (X - B) / Z + cx.

# %%
F_PX, BASE, Z0 = 1000.0, 0.04, 0.5
IMG_W, IMG_H = 320, 160
STRIP = (60.0, 40.0)             # width, height in mm


def strip_dots(seed=2):
    d, sig = make_dots(STRIP[0], STRIP[1], dot_sigma=1.5, density=0.11, margin=6, seed=seed)
    d[:, 0] -= STRIP[0] / 2
    d[:, 1] -= STRIP[1] / 2
    return d, sig


def stereo_pair(dots, exx=0.0, dz=0.0, nu=NU, noise=0.0, seed=0):
    """Left and right grey images (IMG_H x IMG_W) of the strip in the state (exx, dz)."""
    vv, uu = np.mgrid[0:IMG_H, 0:IMG_W].astype(float)
    Z = Z0 - dz
    images = []
    for cam, off in enumerate((0.0, BASE)):
        X = (uu - IMG_W / 2) * Z / F_PX + off        # metres on the strip plane
        Y = (vv - IMG_H / 2) * Z / F_PX
        s = X * 1000.0 / (1 + exx)                   # material coordinates in mm
        t = Y * 1000.0 / (1 - nu * exx)
        inside = (np.abs(s) < STRIP[0] / 2 + 3) & (np.abs(t) < STRIP[1] / 2 + 3)
        img = np.full(uu.shape, 20.0)
        img[inside] = texture(dots, s[inside], t[inside])
        if noise > 0:
            img = img + np.random.default_rng(seed + cam).normal(0.0, noise, img.shape)
        images.append(img)
    return images[0], images[1]


# %%
if __name__ == "__main__":
    import time

    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t0 = time.time()
    r = run_dic(noise=0.0)
    print(f"noise-free: RMS displacement error u {rms(r['U'] - r['ue']):.4f} px, v {rms(r['V'] - r['ve']):.4f} px")
    print(f"strain e_xx: RMS error {rms(r['exx'] - r['exx_exact']):.5f}  (exact mean {np.mean(r['exx_exact']):.5f}, measured mean {np.nanmean(r['exx']):.5f})")
    print(f"strain e_yy: RMS error {rms(r['eyy'] - r['eyy_exact']):.5f}  (exact {-NU * A_STRAIN:.5f}, measured mean {np.nanmean(r['eyy']):.5f})")
    rn = run_dic(noise=4.0)
    print(f"noise 4 grey levels: RMS u error {rms(rn['U'] - rn['ue']):.4f} px, strain e_xx error {rms(rn['exx'] - rn['exx_exact']):.5f}")

    fig, ax = plt.subplots(1, 3, figsize=(11, 3.6))
    ax[0].imshow(r["ref"], cmap="gray", vmin=0, vmax=255)
    ax[0].set_title("reference image")
    ax[1].imshow(r["cur"], cmap="gray", vmin=0, vmax=255)
    ax[1].set_title("deformed image (2 percent stretch)")
    for a_ in ax[:2]:
        a_.set_xlabel("x (pixels)")
        a_.set_ylabel("y (pixels)")
    ax[2].plot(r["xs"], r["U"][len(r["ys"]) // 2], "o", label="measured u")
    ax[2].plot(r["xs"], r["ue"][len(r["ys"]) // 2], "-", label="exact u")
    ax[2].set_xlabel("x (pixels)")
    ax[2].set_ylabel("displacement u (pixels)")
    ax[2].set_title("displacement along the middle row")
    ax[2].legend(fontsize=8)
    ax[2].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "dic_images.png", dpi=110)

    hs = [5, 7, 10, 14, 19, 25]
    G2 = mean_gradient_sq(r["ref"])
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for sn, col in ((2.0, "tab:blue"), (6.0, "tab:red")):
        meas = error_vs_subset(sn, hs)
        pred = np.sqrt(predicted_noise_error(sn, np.array(hs), G2) ** 2 + predicted_bias(np.array(hs)) ** 2)
        ax2.plot(hs, meas, "o", color=col, label=f"measured, noise {sn:g} grey")
        ax2.plot(hs, pred, "-", color=col, label=f"prediction, noise {sn:g} grey")
        print(f"noise {sn:g}: measured", np.round(meas, 4), "predicted", np.round(pred, 4))
    ax2.set_xlabel("subset half-size h (pixels); subset is 2h+1 wide")
    ax2.set_ylabel("RMS displacement error (pixels)")
    ax2.set_title("Noise falls with subset size, bias grows")
    ax2.set_yscale("log")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "error_vs_subset.png", dpi=110)
    clean, noisy = r, rn
    G2c = mean_gradient_sq(clean["ref"])
    du = rms(noisy["U"] - clean["U"])
    print(f"noise only (4 grey levels, h = 10): u error {du:.4f} px, predicted {predicted_noise_error(4.0, 10, G2c):.4f} px")
    for w in (1, 2, 3):
        ea = strain_from_grid(noisy["xs"], noisy["ys"], noisy["U"], noisy["V"], w)[0]
        eb = strain_from_grid(clean["xs"], clean["ys"], clean["U"], clean["V"], w)[0]
        print(f"strain window {w}: noise-induced strain error {rms(ea - eb):.5f}, independent-noise formula {predicted_strain_noise(0.0124, 8, w):.5f}")
    print("mean squared gradient G2 =", round(G2, 1), "(grey/px)^2;  seconds:", round(time.time() - t0, 1))
