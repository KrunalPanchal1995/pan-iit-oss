"""Session 3 (Level 3): the inverse Abel transform: onion peeling, smoothing, noise, and a candle mini-project.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: from the photo back to the flame
# **A. Real-world problem.** You have a photo of a flame and want the glow of its inside, not
# the sum along each line of sight. If the flame is round about its axis, one photo is enough:
# peel it like an onion. The catch is noise. Every real photo has a little noise, and the
# inversion multiplies it, most of all near the axis. You will measure that amplification,
# fight it with a smoothing method, and see the price (bias). Everything is checked against
# the exact pair Gaussian -> Gaussian from Session 2.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
R_MM = 4.0


# %% [markdown]
# ## Step 1: the forward model and the exact truth
# The matrix W (Session 2) turns ring emissions into a brightness profile. To avoid the
# "inverse crime" (testing a method on data made by the very same approximation), the test
# photos below come from a *fine* numerical integral, not from W.

# %%
def ring_matrix(N, R=R_MM):
    dr = R / N
    edges = dr * np.arange(N + 1)
    y = edges[:N]
    inner = np.sqrt(np.clip(edges[None, :-1] ** 2 - y[:, None] ** 2, 0.0, None))
    outer = np.sqrt(np.clip(edges[None, 1:] ** 2 - y[:, None] ** 2, 0.0, None))
    return 2.0 * (outer - inner)


def radii(N, R=R_MM):
    """Ring middles r_j (mm)."""
    return (R / N) * (np.arange(N) + 0.5)


def gauss_eps(r, a):
    return np.exp(-(np.asarray(r, dtype=float) / a) ** 2)


def ring_eps(r, r0, w):
    return np.exp(-((np.asarray(r, dtype=float) - r0) / w) ** 2)


def photo_profile(eps_fn, N, R=R_MM, n_fine=3000):
    """Brightness at y_i = i*dr from a fine integral (not from W): I = 2 * int eps(sqrt(y^2+u^2)) du."""
    I = np.zeros(N)
    for i, y in enumerate((R / N) * np.arange(N)):
        u = np.linspace(0.0, np.sqrt(R * R - y * y), n_fine + 1)
        f = eps_fn(np.sqrt(y * y + u * u))
        I[i] = 2.0 * np.sum(0.5 * (f[1:] + f[:-1]) * np.diff(u))
    return I


def add_noise(I, frac, rng):
    """Gaussian noise with standard deviation frac * (peak brightness)."""
    return I + frac * I.max() * rng.standard_normal(I.shape)


# %% [markdown]
# ## Step 2: onion peeling
# W is upper triangular: the outermost line of sight (i = N-1) crosses only the outermost ring.
# Solve it first, then move inwards, each time subtracting what the outer rings already explain:
#
#     eps_i = ( I_i - sum over j > i of W_ij eps_j ) / W_ii

# %%
def onion_peel(I, R=R_MM):
    I = np.asarray(I, dtype=float)
    N = len(I)
    W = ring_matrix(N, R)
    eps = np.zeros(N)
    for i in range(N - 1, -1, -1):
        eps[i] = (I[i] - W[i, i + 1:] @ eps[i + 1:]) / W[i, i]
    return eps


# %% [markdown]
# ## Step 3: noise amplification
# Inversion is linear: eps = W^-1 I. If each I_i has independent noise of size sigma, the noise
# in ring i is sigma times the length of row i of W^-1. This number is the *gain* of ring i.

# %%
def noise_gain(N, R=R_MM):
    """Standard deviation of eps_i divided by the noise sigma of the photo, for onion peeling."""
    return np.linalg.norm(np.linalg.inv(ring_matrix(N, R)), axis=1)


# %% [markdown]
# ## Step 4: smoothing (Tikhonov regularisation)
# Instead of demanding W eps = I exactly, minimise  |W eps - I|^2 + lam * s * |D eps|^2,
# where D takes second differences (it is zero for a straight-line profile and large for a
# jagged one) and s = mean(diag(W^T W)) makes `lam` a pure number. Large lam = smooth but
# biased; lam = 0 gives noisy onion peeling.

# %%
def smooth_invert(I, lam, R=R_MM):
    I = np.asarray(I, dtype=float)
    N = len(I)
    W = ring_matrix(N, R)
    D = np.diff(np.eye(N), n=2, axis=0)
    s = np.trace(W.T @ W) / N
    return np.linalg.solve(W.T @ W + lam * s * (D.T @ D), W.T @ I)


def trial(eps_fn, N, lam, frac, n_trials=100, seed=0, R=R_MM):
    """Monte Carlo: return (mean estimate, std of estimate, truth) over noisy photos."""
    rng = np.random.default_rng(seed)
    I0 = photo_profile(eps_fn, N, R)
    est = np.array([smooth_invert(add_noise(I0, frac, rng), lam, R) for _ in range(n_trials)])
    return est.mean(axis=0), est.std(axis=0), eps_fn(radii(N, R))


def bias_noise_total(eps_fn, N, lam, frac, n_trials=100, seed=0, R=R_MM):
    """RMS bias, RMS noise and RMS total error (all relative to the peak of eps)."""
    mean, std, truth = trial(eps_fn, N, lam, frac, n_trials, seed, R)
    peak = truth.max()
    bias = np.sqrt(np.mean((mean - truth) ** 2)) / peak
    noise = np.sqrt(np.mean(std ** 2)) / peak
    return float(bias), float(noise), float(np.hypot(bias, noise))


def bias_noise_exact(eps_fn, N, lam, frac, R=R_MM):
    """The same three numbers without random draws. The estimate is linear, eps_hat = G I, so
    bias = G I_true - eps_true and noise_i = sigma * (length of row i of G); sigma = frac * peak(I)."""
    W = ring_matrix(N, R)
    D = np.diff(np.eye(N), n=2, axis=0)
    s = np.trace(W.T @ W) / N
    G = np.linalg.solve(W.T @ W + lam * s * (D.T @ D), W.T)
    I0 = photo_profile(eps_fn, N, R)
    truth = eps_fn(radii(N, R))
    peak = truth.max()
    bias = np.sqrt(np.mean((G @ I0 - truth) ** 2)) / peak
    noise = frac * I0.max() * np.sqrt(np.mean(np.sum(G * G, axis=1))) / peak
    return float(bias), float(noise), float(np.hypot(bias, noise))


# %% [markdown]
# ## Step 4b: a Fourier-series alternative
# Instead of penalising roughness, *describe* the flame with a few smooth shapes. The emission
# is written as a cosine series on 0 <= r <= R,
#
#     eps(r) = a_0 + a_1 cos(pi r / R) + a_2 cos(2 pi r / R) + ... + a_(M-1) cos((M-1) pi r / R),
#
# which is smooth, symmetric about the axis (zero slope at r = 0) and needs only M numbers.
# The photo of each cosine is the matrix W times its values on the rings, so the M amplitudes
# follow from least squares on the N photo pixels. The number of terms M plays the role of
# the smoothing strength: few terms = smooth but biased, M = N = the noisy onion peeling
# (the N cosines can reproduce any N ring values, so the answer is identical to Step 2).

# %%
def fourier_matrix(N, terms, R=R_MM):
    """N x terms matrix of cos(n pi r_j / R) at the ring middles."""
    return np.cos(np.pi * np.outer(radii(N, R), np.arange(terms)) / R)


def fourier_gain(N, terms, R=R_MM):
    """Matrix G with eps_hat = G I for the Fourier-series inversion with `terms` cosines."""
    if not 1 <= terms <= N:
        raise ValueError("terms must be between 1 and the number of pixels N")
    Phi = fourier_matrix(N, terms, R)
    return Phi @ np.linalg.pinv(ring_matrix(N, R) @ Phi)


def fourier_invert(I, terms, R=R_MM):
    """Emission on the rings from the photo profile I, using a cosine series with `terms` terms."""
    I = np.asarray(I, dtype=float)
    return fourier_gain(len(I), terms, R) @ I


def bias_noise_linear(G, eps_fn, N, frac, R=R_MM):
    """RMS bias, noise and total error (relative to the peak of eps) of any linear inversion eps_hat = G I."""
    I0 = photo_profile(eps_fn, N, R)
    truth = eps_fn(radii(N, R))
    peak = truth.max()
    bias = np.sqrt(np.mean((G @ I0 - truth) ** 2)) / peak
    noise = frac * I0.max() * np.sqrt(np.mean(np.sum(G * G, axis=1))) / peak
    return float(bias), float(noise), float(np.hypot(bias, noise))


def bias_noise_fourier(eps_fn, N, terms, frac, R=R_MM):
    """The Fourier-series counterpart of `bias_noise_exact` (no random draws)."""
    return bias_noise_linear(fourier_gain(N, terms, R), eps_fn, N, frac, R)


# %% [markdown]
# ## Step 5: mini-project material, a candle-like flame
# A synthetic side-view "photo" of an axisymmetric flame, in mm: the flame is hollow near the
# base (a ring of glow around dark wax vapour), fills in higher up, and tapers to a tip.
# `candle_emission(r, z)` is the hidden truth; `candle_photo` is what the camera records
# (both sides of the axis, optional noise).

# %%
def candle_emission(r, z):
    s = 3.2 * (z / 6.0) * np.exp(1.0 - z / 6.0)          # flame radius envelope (mm)
    r0 = 0.7 * s * max(0.0, 1.0 - z / 10.0)              # radius of the glow ring (mm); 0 above z = 10 mm
    e = np.exp(-(z / 22.0) ** 2)                         # overall strength fades with height
    return e * np.exp(-((np.asarray(r, dtype=float) - r0) / (0.55 * s)) ** 2)


def candle_photo(N=40, heights=range(1, 21), frac=0.0, seed=1, R=6.0):
    """Rows = heights (mm), columns = offsets y_i (mm) on one side of the axis (flame is symmetric)."""
    rng = np.random.default_rng(seed)
    rows = [photo_profile(lambda r, z=z: candle_emission(r, z), N, R) for z in heights]
    img = np.array(rows)
    if frac > 0:
        img = img + frac * img.max() * rng.standard_normal(img.shape)
    return img


def rel_rms(est, truth):
    """RMS error divided by the peak of the truth."""
    return float(np.sqrt(np.mean((est - truth) ** 2)) / np.max(np.abs(truth)))


def invert_row(row, lam, R=6.0):
    """Radial emission from one image row: onion peeling if lam == 0, otherwise smoothed."""
    return onion_peel(row, R) if lam == 0 else smooth_invert(row, lam, R)


def worst_row_error(img, lam, heights=(4, 8, 12), R=6.0):
    """Largest relative RMS error over the chosen heights (mm); img rows start at z = 1 mm."""
    rr = radii(img.shape[1], R)
    return max(rel_rms(invert_row(img[z - 1], lam, R), candle_emission(rr, z)) for z in heights)


LAM_GRID = (0.0, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    N, a, frac = 40, 1.0, 0.01
    r = radii(N)
    gauss = lambda q: gauss_eps(q, a)
    ringf = lambda q: ring_eps(q, 1.5, 0.4)
    rng = np.random.default_rng(3)

    # exact pair: noise-free onion peeling of a Gaussian
    I0 = photo_profile(gauss, N)
    e0 = onion_peel(I0)
    print(f"noise-free onion peeling, Gaussian a=1 mm, N=40: worst error {np.max(np.abs(e0 - gauss(r))):.4f} of peak 1.0")
    gain = noise_gain(N)
    print(f"noise gain (eps noise / photo noise): axis ring {gain[0]:.1f}, middle ring {gain[N // 2]:.1f}, outer ring {gain[-1]:.2f}")

    # one noisy photo
    In = add_noise(I0, frac, rng)
    print(f"noisy photo (1% of peak): onion peeling RMS error {rel_rms(onion_peel(In), gauss(r)):.3f} of the peak, "
          f"smoothed (lam=0.1) {rel_rms(smooth_invert(In, 0.1), gauss(r)):.3f}")

    # bias-noise trade-off
    lams = np.logspace(-6, 1, 29)
    stats = np.array([bias_noise_exact(gauss, N, l, frac) for l in lams])
    best = lams[np.argmin(stats[:, 2])]
    print(f"best smoothing for the Gaussian at 1% noise: lam = {best:.2g}, total error {stats[:, 2].min():.3f} of the peak")
    statr = np.array([bias_noise_exact(ringf, N, l, frac) for l in lams])
    bestr = lams[np.argmin(statr[:, 2])]
    print(f"best smoothing for the ring flame at 1% noise: lam = {bestr:.2g}, total error {statr[:, 2].min():.3f} of the peak")

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    ax = axes[0]
    ax.semilogy(r, gain, "o-", ms=3)
    ax.set_xlabel("distance from the axis r (mm)")
    ax.set_ylabel("noise gain (eps noise / photo noise)")
    ax.set_title("Onion peeling amplifies noise near the axis")
    ax.grid(alpha=0.3, which="both")
    ax = axes[1]
    ax.plot(r, gauss(r), "k", lw=2, label="truth")
    ax.plot(r, onion_peel(In), ".-", label="onion peeling")
    ax.plot(r, smooth_invert(In, best), "-", lw=2, label=f"smoothed, lam = {best:.2g}")
    ax.set_xlabel("distance from the axis r (mm)")
    ax.set_ylabel("emission eps (a.u. per mm)")
    ax.set_title("Gaussian flame, 1% noise")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    ax = axes[2]
    ax.loglog(lams, stats[:, 0], label="bias")
    ax.loglog(lams, stats[:, 1], label="noise")
    ax.loglog(lams, stats[:, 2], "k", lw=2, label="total")
    ax.set_xlabel("smoothing strength lam (no unit)")
    ax.set_ylabel("RMS error / peak")
    ax.set_title("Smoothing trades noise for bias")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "noise_and_smoothing.png", dpi=110)

    # ring-shaped flame: too much smoothing fills the hole
    fig2, axes2 = plt.subplots(1, 2, figsize=(10, 4))
    Ir = add_noise(photo_profile(ringf, N), frac, np.random.default_rng(4))
    ax = axes2[0]
    ax.plot(r, ringf(r), "k", lw=2, label="truth")
    for lam, col in ((1e-4, "tab:red"), (bestr, "tab:green"), (30.0, "tab:purple")):
        ax.plot(r, smooth_invert(Ir, lam), color=col, label=f"lam = {lam:.2g}")
    ax.set_xlabel("distance from the axis r (mm)")
    ax.set_ylabel("emission eps (a.u. per mm)")
    ax.set_title("Ring-shaped flame, 1% noise")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    ax = axes2[1]
    ax.loglog(lams, statr[:, 0], label="bias")
    ax.loglog(lams, statr[:, 1], label="noise")
    ax.loglog(lams, statr[:, 2], "k", lw=2, label="total")
    ax.set_xlabel("smoothing strength lam (no unit)")
    ax.set_ylabel("RMS error / peak")
    ax.set_title("Ring flame needs less smoothing")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "ring_flame.png", dpi=110)

    # figure 4: Fourier series against smoothing
    termsl = np.arange(3, N + 1)
    fst = {name: np.array([bias_noise_fourier(f, N, int(T), frac) for T in termsl]) for name, f in (("Gaussian", gauss), ("ring", ringf))}
    tst = {"Gaussian": stats, "ring": statr}
    fig4, axes4 = plt.subplots(1, 3, figsize=(14, 4))
    for ax, name in zip(axes4[:2], ("Gaussian", "ring")):
        ax.loglog(tst[name][:, 1], tst[name][:, 0], "-", color="#003f7f", lw=2, label="smoothing (lam)")
        ax.loglog(fst[name][:, 1], fst[name][:, 0], "s-", color="#c86a00", ms=4, label="Fourier series (terms)")
        for st, col in ((tst[name], "#003f7f"), (fst[name], "#c86a00")):
            j = np.argmin(st[:, 2])
            ax.plot(st[j, 1], st[j, 0], "o", ms=10, mfc="none", mec=col, mew=2)
        ax.set_xlabel("noise (RMS, relative to peak)")
        ax.set_ylabel("bias (RMS, relative to peak)")
        ax.set_title(f"{name} flame, 1% noise: circles mark the lowest total error")
        ax.title.set_fontsize(9)
        ax.grid(alpha=0.3, which="both")
        ax.legend(fontsize=8)
    ax = axes4[2]
    jf = int(termsl[np.argmin(fst["ring"][:, 2])])
    ax.plot(r, ringf(r), "k", lw=2, label="truth")
    ax.plot(r, fourier_invert(Ir, jf), color="#c86a00", label=f"Fourier, {jf} terms")
    ax.plot(r, fourier_invert(Ir, 6), "--", color="#d81b60", label="Fourier, 6 terms (too few)")
    ax.plot(r, smooth_invert(Ir, bestr), color="#003f7f", label=f"smoothing, lam = {bestr:.2g}")
    ax.set_xlabel("distance from the axis r (mm)")
    ax.set_ylabel("emission eps (a.u. per mm)")
    ax.set_title("Ring flame, one noisy photo", fontsize=9)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig4.tight_layout()
    fig4.savefig(OUT / "fourier_vs_smoothing.png", dpi=110)
    for name in ("Gaussian", "ring"):
        jt, jf_ = np.argmin(tst[name][:, 2]), np.argmin(fst[name][:, 2])
        print(f"{name}: smoothing best total {tst[name][jt, 2]:.4f} (lam {lams[jt]:.2g}); Fourier best total {fst[name][jf_, 2]:.4f} ({termsl[jf_]} terms)")

    # mini-project
    img = candle_photo(N=40, frac=0.03)
    zs = [4, 8, 12]
    R6 = 6.0
    rr = radii(40, R6)
    fig3, axes3 = plt.subplots(1, 4, figsize=(15, 3.8))
    axes3[0].imshow(np.hstack([img[::-1, ::-1], img[::-1]]), extent=[-6, 6, 1, 20], origin="upper", cmap="inferno", aspect="auto")
    axes3[0].set_title("Side-view photo (3% noise)")
    axes3[0].set_xlabel("offset y (mm)")
    axes3[0].set_ylabel("height z (mm)")
    for k, z in enumerate(zs):
        ax = axes3[k + 1]
        row = z - 1
        truth = candle_emission(rr, z)
        ax.plot(rr, truth, "k", lw=2, label="truth")
        ax.plot(rr, smooth_invert(img[row], 3.0, R6), label="smoothed lam=3")
        ax.plot(rr, onion_peel(img[row], R6), ":", label="onion peeling")
        ax.set_ylim(-0.5, 1.4)
        ax.set_title(f"height z = {z} mm")
        ax.set_xlabel("radius r (mm)")
        ax.set_ylabel("emission (a.u. per mm)")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    fig3.tight_layout()
    fig3.savefig(OUT / "candle_rows.png", dpi=110)
    for lam in LAM_GRID:
        print(f"lam = {lam:5.2f}: worst-row error {worst_row_error(img, lam):.3f} of the peak")

# %% [markdown]
# ## Where this stops
# We invert one row at a time and assume a perfectly round, steady flame whose axis is known.
# A puffing, tilted or noisy flame breaks those assumptions. That is the road to the Target:
# see `promo/roadmap.md`.
