"""Session 3 (Level 3): synthetic kymographs, two estimators, errors, and aliasing.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulate, measure, validate
# **A. Real-world problem.** Before trusting a method on a real video you must test it where the
# answer is known. We generate kymographs with a *known* speed, measure them in two different
# ways, and find out how the error grows with noise and what happens when the object moves too
# far between frames.
#
# **Plan.** (1) generators for blobs and for a textured belt, (2) a gradient estimator, (3) a
# ridge-following estimator with a straight-line fit, (4) Monte Carlo error against noise,
# (5) a formula to check the fit scatter, (6) aliasing, (7) the conveyor mini-project.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: generators with a known answer
# `tracks` is a list of (start column, speed px/frame, amplitude). `noise` is the standard
# deviation of Gaussian noise added to every pixel (the brightest blob has height 1).

# %%
def blob_kymo(tracks, n_t=60, n_x=96, sigma=1.5, noise=0.0, seed=0):
    """Kymograph (time down, position across) with one Gaussian stripe per track."""
    rng = np.random.default_rng(seed)
    t = np.arange(n_t)[:, None]
    x = np.arange(n_x)[None, :]
    K = np.zeros((n_t, n_x))
    for x0, v, amp in tracks:
        K += amp * np.exp(-((x - (x0 + v * t)) ** 2) / (2 * sigma ** 2))
    return K + noise * rng.standard_normal(K.shape)


def texture_kymo(v, n_t=60, n_x=128, corr=2.0, noise=0.0, seed=0):
    """Kymograph of a random smooth texture sliding at v px/frame (like a belt surface)."""
    rng = np.random.default_rng(seed)
    pad = int(abs(v) * n_t) + 40
    raw = rng.standard_normal(n_x + 2 * pad + 40)
    k = np.exp(-0.5 * (np.arange(-4 * int(corr) - 1, 4 * int(corr) + 2) / corr) ** 2)
    base = np.convolve(raw, k / k.sum(), mode="same")
    base = (base - base.mean()) / base.std()
    t = np.arange(n_t)[:, None]
    x = np.arange(n_x)[None, :]
    K = np.interp(x - v * t + pad + 20, np.arange(base.size), base)
    return K + noise * rng.standard_normal(K.shape)


def wave_kymo(v, wavelength, n_t=60, n_x=128):
    """Kymograph of a travelling cosine pattern: used to show true aliasing."""
    t = np.arange(n_t)[:, None]
    x = np.arange(n_x)[None, :]
    return np.cos(2 * np.pi * (x - v * t) / wavelength)


# %% [markdown]
# ## Step 2: estimator 1, gradients (two versions)
# Along a stripe the brightness K(x, t) = f(x - v t) obeys `Kt + v * Kx = 0` at every pixel.
# Kx is the brightness change per pixel, Kt per frame.
#
# * **Least squares (LS)** treats Kx as exact: v = - sum(Kx * Kt) / sum(Kx * Kx). Noise in Kx
#   makes the denominator too big, so LS is *biased towards zero* when the image is noisy.
# * **Total least squares (TLS)** uses the structure tensor of Session 2 (the eigenvector of
#   the 2x2 matrix of sums). If the noise in Kx and Kt is equal and independent, the noise only
#   adds the same amount to both diagonal entries and leaves the eigenvector unchanged, so the
#   bias goes away. We get Kx and Kt from derivative-of-Gaussian filters, which keeps the noise
#   in the two equal.

# %%
def smooth(K, s=1.0):
    """Separable Gaussian smoothing with standard deviation s pixels (and frames)."""
    if s <= 0:
        return K
    r = int(np.ceil(3 * s))
    g = np.exp(-0.5 * (np.arange(-r, r + 1) / s) ** 2)
    g /= g.sum()
    A = np.apply_along_axis(lambda m: np.convolve(m, g, mode="same"), 1, K)
    A = np.apply_along_axis(lambda m: np.convolve(m, g, mode="same"), 0, A)
    return A[r:-r, r:-r]


def gradient_speed_ls(K, s=1.0):
    """Least-squares speed (px/frame) from smoothed central differences. nan if the image is flat."""
    S = smooth(K, s)
    Kt, Kx = np.gradient(S)
    Kx, Kt = Kx[1:-1, 1:-1], Kt[1:-1, 1:-1]
    den = np.sum(Kx * Kx)
    return float(-np.sum(Kx * Kt) / den) if den > 1e-12 else float("nan")


def derivative_images(K, s=1.0):
    """Kx and Kt from derivative-of-Gaussian filters of width s; the borders (4 s) are cropped."""
    r = int(np.ceil(4 * s))
    u = np.arange(-r, r + 1)
    g = np.exp(-0.5 * (u / s) ** 2)
    g /= g.sum()
    d = -u / s ** 2 * g

    def conv(A, k, axis):
        return np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), axis, A)

    Kx = conv(conv(K, d, 1), g, 0)
    Kt = conv(conv(K, g, 1), d, 0)
    return Kx[r:-r, r:-r], Kt[r:-r, r:-r]


def gradient_speed(K, s=1.0):
    """TLS speed (px/frame) from the structure tensor of derivative-of-Gaussian images. nan if flat."""
    Kx, Kt = derivative_images(K, s)
    J = np.array([[np.sum(Kx * Kx), np.sum(Kx * Kt)], [np.sum(Kx * Kt), np.sum(Kt * Kt)]])
    if np.trace(J) < 1e-12:
        return float("nan")
    _, V = np.linalg.eigh(J)
    nx, nt = V[:, 1]
    return float(-nt / nx) if abs(nx) > 1e-12 else float("inf")


# %% [markdown]
# ## Step 3: estimator 2, follow the ridge, fit a line
# Start at the known column of one stripe. In each row look only in a window around the last
# position and take the brightness-weighted centre (sub-pixel). Then fit x = x0 + v t by least
# squares. The fit also tells us the scatter of the points around the line.

# %%
def track_ridge(K, x_start, win=3):
    """Follow one stripe down the rows. Returns the centre column (float) of every row."""
    n_t, n_x = K.shape
    pos = np.empty(n_t)
    c = float(x_start)
    for t in range(n_t):
        lo, hi = max(0, int(round(c)) - win), min(n_x, int(round(c)) + win + 1)
        w = np.clip(K[t, lo:hi], 0.0, None)
        if w.sum() > 1e-9:
            c = float(np.sum(w * np.arange(lo, hi)) / w.sum())
        pos[t] = c
    return pos


def ridge_speed(K, x_start, win=3):
    """Return (speed px/frame, rms scatter of the points about the line in pixels)."""
    pos = track_ridge(K, x_start, win)
    t = np.arange(pos.size)
    slope, icpt = np.polyfit(t, pos, 1)
    return float(slope), float(np.sqrt(np.mean((pos - (slope * t + icpt)) ** 2)))


# %% [markdown]
# ## Step 4: error against noise (Monte Carlo)
# Repeat the experiment with new noise `trials` times. The *bias* is the average error, the
# *scatter* is the standard deviation of the results.

# %%
def monte_carlo(estimate, make, trials=60):
    """estimate(K) -> speed; make(seed) -> kymograph. Returns (mean speed, std of speed)."""
    vals = np.array([estimate(make(s)) for s in range(trials)])
    return float(vals.mean()), float(vals.std())


def slope_std_formula(sigma_pos, n):
    """Standard deviation of a least-squares slope through n equally spaced points of scatter sigma_pos."""
    return float(sigma_pos * np.sqrt(12.0 / (n * (n * n - 1.0))))


# %% [markdown]
# ## Step 5: aliasing
# If the pattern shifts by `d` pixels between frames and repeats every `wavelength` pixels,
# a camera cannot tell shift `d` from `d - wavelength`. The apparent shift is `d` folded into
# the range -wavelength/2 .. +wavelength/2. For a single blob the failure is different: once the
# shift is bigger than the blob is wide, neighbouring frames no longer overlap and the
# gradient equation Kt + v Kx = 0 is no longer true.

# %%
def apparent_shift(d, wavelength):
    """The shift a camera would report for true shift d (pixels per frame) of a pattern with the given wavelength."""
    return float((d + wavelength / 2.0) % wavelength - wavelength / 2.0)


def shift_error(v_true, make, estimate):
    """Relative error (estimate - true) / true for one kymograph."""
    return (estimate(make(v_true)) - v_true) / v_true


# %% [markdown]
# ## Step 6: the mini-project world
# A belt with a random surface moves past a camera. `conveyor_kymo` is the kymograph of one
# line along the belt. `belt_speed_mps` converts the measured slope to m/s.

# %%
def conveyor_kymo(v_mps, fps, mm_per_px, n_t=60, n_x=160, noise=0.2, seed=1):
    """Kymograph of a textured belt moving at v_mps seen with the given frame rate and pixel size."""
    v_px = v_mps / ((mm_per_px / 1000.0) * fps)
    return texture_kymo(v_px, n_t=n_t, n_x=n_x, corr=1.0, noise=noise, seed=seed)


def belt_speed_mps(K, fps, mm_per_px):
    """Speed in m/s from a conveyor kymograph, using the gradient estimator."""
    return gradient_speed(K) * (mm_per_px / 1000.0) * fps


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # accuracy against noise
    print("true v = 0.7 px/frame.   noise: LS (mean, std) | TLS (mean, std) | ridge (mean, std)")
    noises = [0.0, 0.1, 0.2, 0.4, 0.8]
    res = {"LS": [], "TLS": [], "ridge": []}
    for nz in noises:
        mk = lambda s, nz=nz: blob_kymo([(10, 0.7, 1.0)], noise=nz, seed=s)
        a = monte_carlo(gradient_speed_ls, mk)
        b = monte_carlo(gradient_speed, mk)
        c = monte_carlo(lambda K: ridge_speed(K, 10)[0], mk)
        res["LS"].append(a); res["TLS"].append(b); res["ridge"].append(c)
        print(f"  {nz:4.1f}: {a[0]:.3f} {a[1]:.3f} | {b[0]:.3f} {b[1]:.3f} | {c[0]:.3f} {c[1]:.3f}")

    # check the line-fit formula with points of known scatter
    rng = np.random.default_rng(5)
    tt = np.arange(60)
    fits = [np.polyfit(tt, 0.7 * tt + 0.26 * rng.standard_normal(60), 1)[0] for _ in range(2000)]
    print(f"line fit, 60 points, scatter 0.26 px: formula {slope_std_formula(0.26, 60):.4f}, simulated {np.std(fits):.4f}")
    print(f"ridge fit on the noisy image (noise 0.2): scatter of speed {res['ridge'][2][1]:.4f}")

    # failure: speed sweep (blob width sigma = 1.5 px)
    speeds = np.array([0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0])
    eg, er = [], []
    for v in speeds:
        make = lambda vv: blob_kymo([(5, vv, 1.0)], n_x=700)
        eg.append(shift_error(v, make, gradient_speed))
        er.append(shift_error(v, make, lambda K: ridge_speed(K, 5)[0]))
    print("blob sigma 1.5 px: shift per frame -> gradient error, ridge error")
    for v, a, b in zip(speeds, eg, er):
        print(f"  {v:4.1f}: {a:+8.1%}  {b:+8.1%}")

    # aliasing of a periodic pattern
    print("cosine wave, wavelength 8 px: true shift -> apparent shift (formula), measured by TLS")
    for d in (1.0, 3.0, 5.0, 6.0):
        print(f"  {d:.1f} -> {apparent_shift(d, 8.0):+.2f}, {gradient_speed(wave_kymo(d, 8.0), s=1.0):+.2f}")

    # conveyor
    print("conveyor 0.80 m/s, 2 mm/px, 5 seeds: fps -> shift, worst error")
    conv = []
    for fps in (100, 200, 300, 400, 600, 800):
        errs = [(belt_speed_mps(conveyor_kymo(0.8, fps, 2.0, seed=sd), fps, 2.0) - 0.8) / 0.8 for sd in range(5)]
        conv.append(max(abs(e) for e in errs))
        print(f"  {fps:4d} fps  {0.8 / (0.002 * fps):.2f} px/frame  worst error {conv[-1]:.1%}")

    # figures
    fig, axs = plt.subplots(1, 3, figsize=(9.5, 3.4))
    for ax, nz in zip(axs, (0.0, 0.4, 0.8)):
        ax.imshow(blob_kymo([(10, 0.7, 1.0), (45, 0.7, 0.7), (75, 0.7, 0.5)], noise=nz, seed=3), cmap="gray", aspect="auto")
        ax.set_title(f"noise {nz}")
        ax.set_xlabel("position x (pixels)")
        ax.set_ylabel("time t (frames)")
    fig.tight_layout()
    fig.savefig(OUT / "noisy_kymographs.png", dpi=120)

    fig2, ax2 = plt.subplots(1, 2, figsize=(9.5, 3.8))
    for name, mark in (("LS", "o"), ("TLS", "s"), ("ridge", "^")):
        m = [r[0] for r in res[name]]
        sd = [r[1] for r in res[name]]
        ax2[0].errorbar(noises, m, yerr=sd, marker=mark, capsize=3, label=name)
    ax2[0].axhline(0.7, color="k", ls="--", label="true 0.7")
    ax2[0].set_xlabel("noise standard deviation (brightness units)")
    ax2[0].set_ylabel("measured speed (px/frame)")
    ax2[0].set_title("Error against noise")
    ax2[0].legend()
    ax2[0].grid(alpha=0.3)
    ax2[1].plot(speeds, np.clip(np.abs(eg) * 100, 0, 100), "o-", label="gradient (TLS)")
    ax2[1].plot(speeds, np.clip(np.abs(er) * 100, 0, 100), "s-", label="ridge fit, window 3 px")
    ax2[1].set_xlabel("true shift per frame (pixels)")
    ax2[1].set_ylabel("absolute error (percent, capped at 100)")
    ax2[1].set_title("Failure at large shift (blob sigma 1.5 px)")
    ax2[1].legend()
    ax2[1].grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "error_study.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
