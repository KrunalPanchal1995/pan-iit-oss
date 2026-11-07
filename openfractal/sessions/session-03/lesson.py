"""Session 3 (Level 3): a vectorised renderer with smooth colouring, area by Monte Carlo, limits.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: render it, measure it, find where it breaks
# **A. Real-world problem.** A zoom video needs hundreds of frames; a Python loop over pixels is
# far too slow. We use numpy to iterate all pixels at once, colour them without ugly bands, measure
# the area of the Mandelbrot set by random sampling (a way to check a renderer against a known
# number), and find out where double-precision numbers stop being good enough.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
SEAHORSE = complex(-0.743643887037151, 0.131825904205330)
KNOWN_AREA = 1.5066          # approximate literature value of the area of the Mandelbrot set


# %% [markdown]
# ## Step 1: iterate every pixel at once
# `C` is an array of complex numbers, one per pixel. Each pass does z = z*z + c for every pixel
# that has not escaped yet, and we shrink the list of "active" pixels as they escape. We stop at a
# large bailout radius (256) rather than 2, because the smooth colour below needs z after it is
# well past the escape line; the classification inside/outside is the same.

# %%
def pixel_grid(centre, width, nx, ny):
    """Complex number of every pixel of an nx-by-ny image, `width` wide, row 0 at the top."""
    height = width * ny / nx
    xs = centre.real + (np.arange(nx) + 0.5 - nx / 2) * width / nx
    ys = centre.imag + (ny / 2 - 0.5 - np.arange(ny)) * height / ny
    return xs[None, :] + 1j * ys[:, None]


def escape_counts(C, max_iter, bailout=256.0):
    """Return (n, zesc, work): n = first step with |z| > bailout (-1 if never), zesc = z at that step,
    work = total number of z-updates performed (the cost)."""
    C = np.asarray(C, dtype=complex)
    n = np.full(C.shape, -1, dtype=int)
    zesc = np.zeros(C.shape, dtype=complex)
    nf, ef, cf = n.ravel(), zesc.ravel(), C.ravel()
    idx = np.arange(cf.size)
    za, ca = np.zeros(cf.size, dtype=complex), cf.copy()
    work = 0
    for k in range(1, max_iter + 1):
        if idx.size == 0:
            break
        za = za * za + ca
        work += idx.size
        out = np.abs(za) > bailout
        if out.any():
            nf[idx[out]] = k
            ef[idx[out]] = za[out]
            keep = ~out
            idx, za, ca = idx[keep], za[keep], ca[keep]
    return n, zesc, int(work)


# %% [markdown]
# ## Step 2: smooth colouring
# The integer count n makes visible bands. Near the escape, |z| roughly squares each step, so
# log|z| doubles: log2(log|z|) tells how far *into* the last step we were. The continuous count
#
#     nu = n + 1 - log2( ln|z_n| )
#
# varies smoothly from pixel to pixel and hardly depends on the bailout radius.

# %%
def smooth_value(n, zesc):
    """Continuous escape count nu (NaN for pixels that never escaped)."""
    nu = np.full(n.shape, np.nan)
    m = n > 0
    nu[m] = n[m] + 1 - np.log2(np.log(np.abs(zesc[m])))
    return nu


def render(centre, width, nx, ny, max_iter, bailout=256.0):
    """Return (nu, work) for a window. nu is NaN inside the set."""
    n, zesc, work = escape_counts(pixel_grid(centre, width, nx, ny), max_iter, bailout)
    return smooth_value(n, zesc), work


def inside_fraction(centre, width, nx, ny, max_iter):
    nu, _ = render(centre, width, nx, ny, max_iter)
    return float(np.isnan(nu).mean())


# %% [markdown]
# ## Step 3: area of the Mandelbrot set by random sampling (Monte Carlo)
# Throw N random points into a box that contains M. The fraction p that land inside times the
# box area estimates the area of M. The set is symmetric about the real axis, so we use only
# the upper half-box [-2, 0.5] x [0, 1.15] (area 2.875) and double the answer. The statistical
# error bar is  2 * 2.875 * sqrt(p (1 - p) / N),  shrinking like 1 / sqrt(N). Using a finite
# max_iter counts slow escapers as inside, so the estimate is a little too large.

# %%
HALF_BOX = (-2.0, 0.5, 0.0, 1.15)


def sample_inside(n_samples, max_iter, seed):
    """Boolean array: which random points of the upper half-box look inside M."""
    rng = np.random.default_rng(seed)
    x0, x1, y0, y1 = HALF_BOX
    C = rng.uniform(x0, x1, n_samples) + 1j * rng.uniform(y0, y1, n_samples)
    n, _, _ = escape_counts(C, max_iter)
    return n < 0


def area_estimate(inside):
    """(area, error bar) from a boolean sample array."""
    x0, x1, y0, y1 = HALF_BOX
    box = (x1 - x0) * (y1 - y0)
    p = inside.mean()
    return 2 * box * p, 2 * box * float(np.sqrt(p * (1 - p) / inside.size))


# %% [markdown]
# ## Step 4: cost, and the limit of double precision
# * **Cost.** `work` counts z-updates. Pixels inside the set always use all `max_iter` steps, so cost
#   grows roughly linearly with `max_iter` wherever many pixels are inside.
# * **Failure.** A float64 number has about 16 significant digits. Near x = -0.74 two
#   neighbouring floats are about 1.1e-16 apart. When the pixel spacing width/nx drops to that size,
#   neighbouring pixels get the *same* coordinate and the picture turns into blocks.

# %%
def distinct_columns(centre, width, nx):
    """How many different x-coordinates the nx columns of a window actually have."""
    return int(np.unique(pixel_grid(centre, width, nx, 1).real).size)


def deepest_width(centre, nx=200, widths=None):
    """Smallest width in the list for which all nx columns still have different coordinates."""
    widths = [10.0 ** -k for k in range(1, 17)] if widths is None else widths
    ok = [w for w in widths if distinct_columns(centre, w, nx) == nx]
    return min(ok) if ok else None


# %% [markdown]
# ## Step 5: a mini-Mandelbrot copy
# Along the negative real axis there is a small copy of the whole set. Its centre is a c for which
# the orbit of 0 returns to 0 after exactly 3 steps: z3 = (c^2 + c)^2 + c = 0, i.e. c^3 + 2c^2 + c + 1 = 0.

# %%
def period3_centre():
    """The real root of c^3 + 2c^2 + c + 1 = 0 (centre of the period-3 copy on the real axis)."""
    r = np.roots([1, 2, 1, 1])
    return float(r[np.abs(r.imag) < 1e-9].real[0])


def mislabelled(centre, width, max_iter, ref_iter=2000, nx=60, ny=40):
    """Fraction of pixels painted inside at max_iter that escape within ref_iter steps."""
    low = np.isnan(render(centre, width, nx, ny, max_iter)[0])
    ref = np.isnan(render(centre, width, nx, ny, ref_iter)[0])
    return float(np.mean(low & ~ref))


# %%
if __name__ == "__main__":
    import time

    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t0 = time.time()
    nu, work = render(complex(-0.5, 0), 3.4, 480, 320, 300)
    print(f"full set 480x320, 300 iterations: work {work} z-updates, {time.time() - t0:.2f} s, inside {np.isnan(nu).mean():.3f}")
    n_int, zz, _ = escape_counts(pixel_grid(complex(-0.5, 0), 3.4, 480, 320), 300)
    bands = np.where(n_int > 0, n_int, np.nan)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    ext = (-2.2, 1.2, -1.133, 1.133)
    axes[0].imshow(bands, extent=ext, cmap="twilight_shifted")
    axes[0].set_title("integer count n: visible bands")
    axes[1].imshow(np.log(nu + 1), extent=ext, cmap="twilight_shifted")
    axes[1].set_title("smooth count nu = n + 1 - log2(ln|z|)")
    for ax in axes:
        ax.set_xlabel("Re c")
        ax.set_ylabel("Im c")
    fig.tight_layout()
    fig.savefig(OUT / "smooth_vs_bands.png", dpi=110)

    nmax = 400000
    inside = sample_inside(nmax, 2000, seed=7)
    Ns = np.unique(np.logspace(2, np.log10(nmax), 30).astype(int))
    est = np.array([area_estimate(inside[:k]) for k in Ns])
    a_full, e_full = area_estimate(inside)
    print(f"Monte Carlo area, N = {nmax}, max_iter 2000: {a_full:.4f} +/- {e_full:.4f}  (literature about {KNOWN_AREA})")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.errorbar(Ns, est[:, 0], yerr=est[:, 1], fmt="o-", ms=3, capsize=2, label="estimate +/- 1 standard error")
    ax2.axhline(KNOWN_AREA, color="red", ls="--", label="literature value about 1.5066")
    ax2.set_xscale("log")
    ax2.set_ylim(1.2, 1.8)
    ax2.set_xlabel("number of random points N")
    ax2.set_ylabel("area of the Mandelbrot set (square units)")
    ax2.set_title("Monte Carlo area converges like 1/sqrt(N)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "area_convergence.png", dpi=120)

    for m in (50, 100, 200, 400, 800):
        print(f"max_iter {m:4d}: work (full set) {render(complex(-0.5, 0), 3.4, 160, 100, m)[1]:9d}   work (seahorse, width 0.01) {render(SEAHORSE, 0.01, 160, 100, m)[1]:9d}")
    for k in (6, 10, 13, 14, 15, 16):
        w = 10.0 ** -k
        print(f"width 1e-{k}: {distinct_columns(SEAHORSE, w, 200)} distinct x-coordinates for 200 columns")
    print("deepest usable width:", deepest_width(SEAHORSE))
    c3 = period3_centre()
    z = 0j
    for _ in range(3):
        z = z * z + c3
    print(f"period-3 centre c3 = {c3:.10f}, z3 = {abs(z):.2e}")
    for m in (50, 100, 200, 400, 800):
        print(f"mini copy, width 0.05, max_iter {m}: mislabelled {mislabelled(c3, 0.05, m):.4f}")

    fig3, ax3 = plt.subplots(1, 2, figsize=(9, 3.6))
    for ax, wd, title in ((ax3[0], 0.5, "width 0.5"), (ax3[1], 0.05, "width 0.05")):
        v, _ = render(complex(c3, 0), wd, 240, 160, 400)
        ax.imshow(np.log(v + 1), extent=(c3 - wd / 2, c3 + wd / 2, -wd / 3, wd / 3), cmap="twilight_shifted")
        ax.set_title(f"mini copy near c = {c3:.4f}, {title}")
        ax.set_xlabel("Re c")
        ax.set_ylabel("Im c")
    fig3.tight_layout()
    fig3.savefig(OUT / "mini_mandelbrot.png", dpi=110)
    print("saved figures in", OUT)

# %% [markdown]
# ## Where this stops
# Float64 limits the zoom to a width near 1e-15. Deeper zooms (the long videos you may have seen)
# use perturbation theory and arbitrary precision numbers - the road to the Target.
