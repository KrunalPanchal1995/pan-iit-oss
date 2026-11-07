"""Session 4 (Level 3): choose the smoothing strength from the photo alone.

Educational model only. Not a measurement method for any real flame or safety decision.
Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: no peeking at the truth
# **A. Real-world problem.** In Session 3 the smoothing strength `lam` was picked by trying
# several values and keeping the one whose answer was closest to the *true* flame. With a real
# photograph nobody knows the true flame, so that recipe is impossible. We need a rule that
# looks only at the photo. Three standard rules are built here, tested against the truth they
# are not allowed to see, and compared over 20 different noise draws of the candle photo:
#
# 1. the *discrepancy principle*: smooth as much as you can while still fitting the photo to
#    within the noise (needs the noise size sigma);
# 2. *unbiased predictive risk* (UPRE): an estimate of how well the smoothed photo predicts the
#    clean photo (needs sigma);
# 3. *generalised cross-validation* (GCV): leave one pixel out and predict it (needs nothing).
#
# **Plan.** (1) the smoother and its hat matrix, (2) estimating sigma from the photo, (3) the three
# scores, (4) a check of the cross-validation formula, (5) pooling the rows of the photo,
# (6) the candle over 20 noise draws.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
R_MM = 4.0
R_CANDLE = 6.0


# %% [markdown]
# ## Step 1: the forward model and the smoother (from Session 3)
# `ring_matrix` turns ring emissions into a one-sided brightness profile; the test photos come
# from a fine integral so that the method is not graded on data made by its own approximation.
# The smoothed answer is *linear* in the photo: eps_hat = G I, with
# G = (W^T W + lam s D^T D)^-1 W^T. The smoothed photo is A I with A = W G, called the *hat
# matrix* ("it puts a hat on I"). Its trace, the number of effective parameters, is N when
# lam = 0 (the photo is copied) and falls towards 2 as lam grows (only a straight line is left).

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


_CACHE = {}


def smoother(N, lam, R=R_MM):
    """Return (G, A): eps_hat = G @ I and fitted photo = A @ I, for the second-difference penalty."""
    key = (N, float(lam), float(R))
    if key not in _CACHE:
        W = ring_matrix(N, R)
        D = np.diff(np.eye(N), n=2, axis=0)
        s = np.trace(W.T @ W) / N
        G = np.linalg.solve(W.T @ W + lam * s * (D.T @ D), W.T)
        _CACHE[key] = (G, W @ G)
    return _CACHE[key]


def effective_parameters(N, lam, R=R_MM):
    """Trace of the hat matrix: how many numbers the smoothed photo is really made of."""
    return float(np.trace(smoother(N, lam, R)[1]))


# %% [markdown]
# ## Step 2: the noise size from the photo alone
# Two of the three rules need sigma, the standard deviation of the noise. It can be read from
# the photo itself. A smooth profile has tiny second differences, d_i = I_(i+1) - 2 I_i + I_(i-1),
# so what is left in d is noise: each d has variance 6 sigma^2 when the pixels are independent.
# The *median absolute deviation* (MAD, times 1.4826 to match a Gaussian) is hardly moved by the
# few places where the flame's own curvature is large. A second route uses the outermost pixels,
# where the flame has ended and only noise remains (only valid if the picture really has an
# empty margin).

# %%
def noise_sigma(img):
    """Noise standard deviation from second differences along each profile (robust MAD)."""
    img = np.atleast_2d(np.asarray(img, dtype=float))
    if img.shape[1] < 4:
        raise ValueError("need at least 4 pixels across to estimate the noise")
    d = np.diff(img, n=2, axis=1) / np.sqrt(6.0)
    return float(1.4826 * np.median(np.abs(d - np.median(d))))


def noise_sigma_margin(img, cols=8):
    """Noise standard deviation from the outermost `cols` pixels (assumes an empty margin)."""
    img = np.atleast_2d(np.asarray(img, dtype=float))
    if not 2 <= cols < img.shape[1]:
        raise ValueError("cols must be between 2 and the number of pixels")
    return float(img[:, -cols:].std())


# %% [markdown]
# ## Step 3: three scores for one smoothing strength
# For a photo I (one row, or several rows sharing the same lam) and the hat matrix A, let
# rss(lam) = |I - A I|^2 be the squared residual (the mean over the rows) and
# df(lam) = trace(A) the effective number of parameters. Then
#
#     discrepancy:  the largest lam with rss / N <= sigma^2
#     UPRE(lam)   = rss + 2 sigma^2 df - N sigma^2                  (choose the smallest)
#     GCV(lam)    = N rss / (N - df)^2                              (choose the smallest)
#
# UPRE is an unbiased estimate of the prediction error |A I - I_clean|^2 (up to a constant);
# GCV does the same without knowing sigma, by using the leave-one-out idea of Step 4.

# %%
LAMS = np.logspace(-3, 2, 51)


def _rss_df(img, lam, R):
    img = np.atleast_2d(np.asarray(img, dtype=float))
    A = smoother(img.shape[1], lam, R)[1]
    r = img - img @ A.T
    return float(np.mean(np.sum(r * r, axis=1))), float(np.trace(A)), img.shape[1]


def gcv_score(img, lam, R=R_CANDLE):
    rss, df, N = _rss_df(img, lam, R)
    if N - df < 1e-9:      # lam = 0 copies the photo: no residual, no information, never the best choice
        return float("inf")
    return N * rss / (N - df) ** 2


def upre_score(img, lam, sigma, R=R_CANDLE):
    rss, df, N = _rss_df(img, lam, R)
    return rss + 2.0 * sigma ** 2 * df - N * sigma ** 2


def discrepancy_gap(img, lam, sigma, R=R_CANDLE):
    """rss / N - sigma^2. Negative means the fit is closer to the photo than the noise allows."""
    rss, df, N = _rss_df(img, lam, R)
    return rss / N - sigma ** 2


def choose_lam(img, method="upre", sigma=None, lams=LAMS, R=R_CANDLE):
    """Pick lam from the photo alone. `img` is one profile or several rows (rows share one lam)."""
    img = np.atleast_2d(np.asarray(img, dtype=float))
    if method not in ("gcv", "upre", "discrepancy"):
        raise ValueError("method must be 'gcv', 'upre' or 'discrepancy'")
    if method != "gcv" and sigma is None:
        sigma = noise_sigma(img)
    if method == "gcv":
        return float(lams[int(np.argmin([gcv_score(img, l, R) for l in lams]))])
    if method == "upre":
        return float(lams[int(np.argmin([upre_score(img, l, sigma, R) for l in lams]))])
    ok = [l for l in lams if discrepancy_gap(img, l, sigma, R) <= 0.0]
    return float(max(ok)) if ok else float(min(lams))


# %% [markdown]
# ## Step 4: why leave-one-out needs no refitting
# Cross-validation hides one pixel, refits, and asks how well the refit predicts the hidden
# pixel. Refitting N times sounds costly, but for a linear smoother there is a shortcut: the
# error made on pixel i when it is left out equals (I_i - (A I)_i) / (1 - A_ii). GCV replaces
# each A_ii by their average df / N. We check the shortcut against honest refitting.

# %%
def loo_shortcut(I, lam, R=R_MM):
    """Leave-one-out prediction errors from the hat matrix, with no refitting."""
    I = np.asarray(I, dtype=float)
    A = smoother(len(I), lam, R)[1]
    return (I - A @ I) / (1.0 - np.diag(A))


def loo_refit(I, lam, i, R=R_MM):
    """Leave-one-out prediction error for pixel i by actually removing it and refitting."""
    I = np.asarray(I, dtype=float)
    N = len(I)
    W = ring_matrix(N, R)
    D = np.diff(np.eye(N), n=2, axis=0)
    s = np.trace(W.T @ W) / N
    keep = np.arange(N) != i
    Wk = W[keep]
    eps = np.linalg.solve(Wk.T @ Wk + lam * s * (D.T @ D), Wk.T @ I[keep])
    return float(I[i] - W[i] @ eps)


# %% [markdown]
# ## Step 5: the candle photo, and pooling the rows
# The candle photograph of Session 3 has 20 rows (heights 1 to 20 mm). All rows come from the
# same camera, so they share one noise level, and the smoothing strength is a property of the
# flame and the camera, not of one row. Choosing one lam from all rows at once uses 20 times
# the data and is far less jumpy than choosing a lam for each row separately.

# %%
def candle_emission(r, z):
    s = 3.2 * (z / 6.0) * np.exp(1.0 - z / 6.0)          # flame radius envelope (mm)
    r0 = 0.7 * s * max(0.0, 1.0 - z / 10.0)              # radius of the glow ring (mm); 0 above z = 10 mm
    e = np.exp(-(z / 22.0) ** 2)                         # overall strength fades with height
    return e * np.exp(-((np.asarray(r, dtype=float) - r0) / (0.55 * s)) ** 2)


def clean_candle(N=40, heights=range(1, 21), R=R_CANDLE):
    """Noise-free candle photo: rows = heights (mm), columns = offsets y_i (mm)."""
    return np.array([photo_profile(lambda r, z=z: candle_emission(r, z), N, R) for z in heights])


def noisy_candle(clean, frac, rng):
    """Add Gaussian noise of size frac * (peak of the photo); returns (photo, true sigma)."""
    sigma = frac * clean.max()
    return clean + sigma * rng.standard_normal(clean.shape), sigma


def rel_rms(est, truth):
    """RMS error divided by the peak of the truth."""
    return float(np.sqrt(np.mean((est - truth) ** 2)) / np.max(np.abs(truth)))


HEIGHTS = (4, 8, 12)


def worst_row_error(img, lam, heights=HEIGHTS, R=R_CANDLE):
    """Largest relative RMS error over the chosen heights. `lam` is one number or a dict {height: lam}.
    This compares with the truth: it is how we GRADE a rule, never how a rule may choose."""
    N = img.shape[1]
    rr = radii(N, R)
    errs = []
    for z in heights:
        l = lam[z] if isinstance(lam, dict) else lam
        errs.append(rel_rms(smoother(N, l, R)[0] @ img[z - 1], candle_emission(rr, z)))
    return max(errs)


def oracle_lam(img, heights=HEIGHTS, lams=LAMS, R=R_CANDLE):
    """Best single lam in the grid, found by looking at the truth (a yardstick, not a method)."""
    errs = [worst_row_error(img, l, heights, R) for l in lams]
    j = int(np.argmin(errs))
    return float(lams[j]), float(errs[j])


METHODS = {
    "fixed lam = 3": lambda img, sig: 3.0,
    "GCV, one row each": lambda img, sig: {z: choose_lam(img[z - 1], "gcv") for z in HEIGHTS},
    "GCV, all rows": lambda img, sig: choose_lam(img, "gcv"),
    "UPRE, all rows": lambda img, sig: choose_lam(img, "upre"),
    "discrepancy, all rows": lambda img, sig: choose_lam(img, "discrepancy"),
}


def compare_methods(clean, frac=0.03, n_draws=20, seed=0):
    """Worst-row error of every rule on n_draws noise draws, plus the oracle and the sigma estimate."""
    rng = np.random.default_rng(seed)
    res = {k: [] for k in METHODS}
    res["oracle (peeks at truth)"] = []
    res["sigma estimate / true sigma"] = []
    for _ in range(n_draws):
        img, sigma = noisy_candle(clean, frac, rng)
        for name, rule in METHODS.items():
            res[name].append(worst_row_error(img, rule(img, sigma)))
        res["oracle (peeks at truth)"].append(oracle_lam(img)[1])
        res["sigma estimate / true sigma"].append(noise_sigma(img) / sigma)
    return {k: np.array(v) for k, v in res.items()}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    N, R = 40, R_CANDLE
    clean = clean_candle(N)
    rng = np.random.default_rng(11)
    img, sigma = noisy_candle(clean, 0.03, rng)
    print(f"true sigma {sigma:.4f}; estimated from curvature {noise_sigma(img):.4f}; from the margin {noise_sigma_margin(img):.4f}")
    print(f"effective parameters of the smoother: lam = 0 -> {effective_parameters(N, 0.0, R):.1f}, lam = 3 -> {effective_parameters(N, 3.0, R):.2f}, lam = 100 -> {effective_parameters(N, 100.0, R):.2f}")

    # cross-validation shortcut against honest refitting
    row = img[7]
    sc = loo_shortcut(row, 3.0, R)
    brute = np.array([loo_refit(row, 3.0, i, R) for i in range(N)])
    print(f"leave-one-out shortcut against {N} refits: largest difference {np.max(np.abs(sc - brute)):.2e}")

    # the three rules on one photo, with the truth they may not use
    for method in ("gcv", "upre", "discrepancy"):
        l = choose_lam(img, method)
        print(f"{method:11s} picks lam = {l:7.3g}: worst-row error {worst_row_error(img, l):.3f}")
    lo, eo = oracle_lam(img)
    print(f"oracle (looks at the truth) lam = {lo:.3g}: worst-row error {eo:.3f}")

    # figure 1: what each rule sees, and what it picks
    lams = LAMS
    sig_hat = noise_sigma(img)
    err = np.array([worst_row_error(img, l) for l in lams])
    picks = {m: choose_lam(img, m) for m in ("gcv", "upre", "discrepancy")}
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8))
    ax = axes[0, 0]
    ax.loglog(lams, err, "k", lw=2.5, label="true worst-row error (hidden)")
    for (m, col, ls), nm in zip((("gcv", "#003f7f", "--"), ("upre", "#c86a00", "-."), ("discrepancy", "#7b2d8e", ":")), ("GCV", "UPRE", "discrepancy")):
        ax.axvline(picks[m], color=col, ls=ls, lw=2, label=f"{nm} picks {picks[m]:.3g}")
    ax.axvline(lo, color="k", ls=":", lw=1, label=f"oracle {lo:.3g}")
    ax.set_xlabel("smoothing strength lam (no unit)")
    ax.set_ylabel("worst-row error / peak")
    ax.set_title("What each rule picks (3% noise, one photo)", fontsize=10)
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=7, loc="lower left")
    ax = axes[0, 1]
    rms = np.array([np.sqrt(_rss_df(img, l, R)[0] / N) for l in lams])
    ax.loglog(lams, rms, color="#003f7f", lw=2, label="residual RMS of the fit")
    ax.axhline(sigma, color="k", ls="--", label="true noise sigma")
    ax.axhline(sig_hat, color="#c86a00", ls=":", lw=2, label="estimated sigma")
    ax.axvline(picks["discrepancy"], color="#7b2d8e", ls=":", lw=2)
    ax.set_xlabel("smoothing strength lam (no unit)")
    ax.set_ylabel("brightness (a.u.)")
    ax.set_title("Discrepancy rule: largest lam whose residual stays at sigma", fontsize=10)
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=7)
    ax = axes[1, 0]
    clean_all = clean
    true_photo = np.array([np.sqrt(np.mean((img @ smoother(N, l, R)[1].T - clean_all) ** 2)) for l in lams])
    upre_est = np.array([np.sqrt(max(upre_score(img, l, sig_hat, R), 1e-12) / N) for l in lams])
    ax.semilogx(lams, true_photo, "k", lw=2.5, label="true error of the smoothed photo (hidden)")
    ax.semilogx(lams, upre_est, color="#c86a00", lw=2, label="UPRE estimate (from the photo)")
    ax.axvline(picks["upre"], color="#c86a00", ls="-.", lw=2)
    ax.set_xlabel("smoothing strength lam (no unit)")
    ax.set_ylabel("RMS error of smoothed photo (a.u.)")
    ax.set_title("UPRE tracks the hidden photo error", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
    ax = axes[1, 1]
    rr = radii(N, R)
    ax.plot(rr, candle_emission(rr, 8), "k", lw=2, label="truth")
    ax.plot(rr, smoother(N, 0.0, R)[0] @ img[7], ":", color="#d81b60", label="onion peeling")
    ax.plot(rr, smoother(N, picks["upre"], R)[0] @ img[7], color="#003f7f", lw=2, label=f"UPRE, lam = {picks['upre']:.3g}")
    ax.set_ylim(-0.5, 1.4)
    ax.set_xlabel("radius r (mm)")
    ax.set_ylabel("emission (a.u. per mm)")
    ax.set_title("Height 8 mm: recovered emission", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "choose_lam.png", dpi=110)

    # mini-project: 20 noise draws
    res = compare_methods(clean, 0.03, 20, seed=0)
    print("\n20 noise draws of the 3% candle photo, worst-row error / peak (heights 4, 8, 12 mm):")
    print(f"{'rule':30s} {'mean':>6s} {'median':>7s} {'max':>6s}  draws <= 0.05")
    for k, v in res.items():
        if k.startswith("sigma"):
            continue
        print(f"{k:30s} {v.mean():6.3f} {np.median(v):7.3f} {v.max():6.3f}  {int(np.sum(v <= 0.05)):2d} of 20")
    s = res["sigma estimate / true sigma"]
    print(f"noise estimate / true noise over the draws: mean {s.mean():.3f}, range {s.min():.3f} to {s.max():.3f}")

    fig2, axes2 = plt.subplots(1, 2, figsize=(11, 4.2))
    names = [k for k in res if not k.startswith("sigma")]
    ax = axes2[0]
    ax.boxplot([res[k] for k in names], showmeans=True)
    ax.set_xticks(range(1, len(names) + 1))
    ax.set_xticklabels([k.replace(", ", ",\n").replace(" (", "\n(") for k in names], fontsize=7)
    ax.axhline(0.05, color="#d81b60", ls="--")
    ax.set_ylabel("worst-row error / peak (20 draws)")
    ax.set_title("Rules that look only at the photo", fontsize=10)
    ax.grid(alpha=0.3)
    ax = axes2[1]
    ax.plot(range(1, 21), res["UPRE, all rows"], "o-", color="#003f7f", label="UPRE, all rows")
    ax.plot(range(1, 21), res["oracle (peeks at truth)"], "s-", color="k", label="oracle")
    ax.plot(range(1, 21), res["GCV, one row each"], "^-", color="#c86a00", label="GCV, one row each")
    ax.axhline(0.05, color="#d81b60", ls="--")
    ax.set_xticks(range(1, 21, 2))
    ax.set_xlabel("noise draw")
    ax.set_ylabel("worst-row error / peak")
    ax.set_title("Draw by draw: the noise sets the floor", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "twenty_draws.png", dpi=110)

# %% [markdown]
# ## Where this stops
# One lam for a row-by-row inversion of an axisymmetric, steady flame whose axis is known and
# whose noise is independent from pixel to pixel. A camera with correlated noise, a flame with
# sharp edges, or an axis that is off by a pixel (Session 5) breaks those assumptions. And no
# rule can beat the noise: a smoothing strength chosen perfectly for one photo still leaves an
# error that depends on that photo's noise draw.
