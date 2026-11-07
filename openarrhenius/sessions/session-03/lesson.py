"""Session 3 (Level 3): uncertainty of an Arrhenius fit, prediction outside the data, validation, failure cases.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: how sure are we about k at a temperature we did not measure?
# **A. Real-world problem.** A lab measures k between 600 and 1000 K, but the engine model needs
# k at 2000 K. A single fitted line gives a number; a useful answer gives the number *and* a
# range that the truth falls inside about 95 times out of 100.
#
# **Plan.** (1) covariance of the fit, (2) the confidence band, (3) Monte Carlo prediction,
# (4) validate with synthetic data of known truth, (5) weights, (6) two ways the method fails.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R_GAS = 8.314462618          # J/(mol K)
A_TRUE = 1.0e13              # 1/s
EA_TRUE = 150.0              # kJ/mol
T_DATA = np.array([600.0, 650.0, 700.0, 750.0, 800.0, 850.0, 900.0, 950.0, 1000.0])   # K

# two-sided 95 percent Student t factors by degrees of freedom
_T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262,
        10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086, 30: 2.042}


def t95(df):
    """Student t factor for a 95 percent two-sided interval (table; next lower tabulated df, so slightly wide)."""
    if df >= 30:
        return 2.042 if df < 120 else 1.98
    return _T95[max(d for d in _T95 if d <= df)]


# %% [markdown]
# ## Step 1: model, data, and the covariance of the fit
# With x = 1000/T and y = ln k the model is y = b0 + b1 x, b0 = ln A, b1 = -Ea/(1000 R).
# Least squares gives the covariance of (b0, b1) as s^2 (X^T X)^-1 where X has a column of ones
# and a column of x, and s^2 = RSS/(n-2) estimates the error variance of ln k.
# Ea = -R b1 (kJ/mol), so the covariance of (ln A, Ea) follows by a sign flip and a scale.

# %%
def arrhenius_k(T, A=A_TRUE, Ea_kJ=EA_TRUE):
    return A * np.exp(-Ea_kJ * 1000.0 / (R_GAS * np.asarray(T, dtype=float)))


def synthetic(T, rel_noise=0.05, seed=0, A=A_TRUE, Ea_kJ=EA_TRUE):
    rng = np.random.default_rng(seed)
    T = np.asarray(T, dtype=float)
    return arrhenius_k(T, A, Ea_kJ) * np.exp(rel_noise * rng.standard_normal(T.size))


def fit_with_cov(T, k, sigma_ln=None):
    """Fit ln k = b0 + b1 * 1000/T. sigma_ln: known error of ln k per point (weighted fit) or None (estimated).
    Returns dict: b (b0, b1), cov (2x2 of b), df, s (error of ln k used)."""
    T, k = np.asarray(T, dtype=float), np.asarray(k, dtype=float)
    if T.size < 3:
        raise ValueError("need at least 3 points to estimate the error of a straight-line fit")
    x, y = 1000.0 / T, np.log(k)
    X = np.column_stack([np.ones(x.size), x])
    if sigma_ln is None:
        b = np.linalg.solve(X.T @ X, X.T @ y)
        df = x.size - 2
        s = float(np.sqrt(np.sum((y - X @ b) ** 2) / df))
        cov = s ** 2 * np.linalg.inv(X.T @ X)
    else:
        w = 1.0 / np.asarray(sigma_ln, dtype=float) ** 2
        XtW = X.T * w
        b = np.linalg.solve(XtW @ X, XtW @ y)
        df = None
        s = 1.0
        cov = np.linalg.inv(XtW @ X)
    return {"b": b, "cov": cov, "df": df, "s": s}


def lnA_Ea(fit):
    """Parameters (ln A, Ea in kJ/mol), their standard errors and their correlation."""
    M = np.diag([1.0, -R_GAS])
    cov = M @ fit["cov"] @ M.T
    se = np.sqrt(np.diag(cov))
    return {"lnA": float(fit["b"][0]), "Ea": float(-R_GAS * fit["b"][1]), "se_lnA": float(se[0]),
            "se_Ea": float(se[1]), "corr": float(cov[0, 1] / (se[0] * se[1])), "cov": cov}


# %% [markdown]
# ## Step 2: the confidence band for ln k(T)
# At temperature T the fitted ln k is g^T b with g = (1, 1000/T). Its variance is g^T cov g,
# which equals s^2 [1/n + (x - xbar)^2 / Sxx]. It is smallest at the mean x and grows with
# distance from it: the band flares outside the data. A 95 percent interval is
# ln k +- t * se; on the k axis the band is a *factor* exp(+-t se).

# %%
def se_ln_k(fit, T):
    g = np.column_stack([np.ones(np.size(T)), 1000.0 / np.asarray(T, dtype=float)])
    return np.sqrt(np.einsum("ij,jk,ik->i", g, fit["cov"], g))


def band(fit, T):
    """(central k, lower k, upper k) with a 95 percent interval for the mean ln k."""
    T = np.atleast_1d(np.asarray(T, dtype=float))
    mid = fit["b"][0] + fit["b"][1] * 1000.0 / T
    t = 1.96 if fit["df"] is None else t95(fit["df"])
    h = t * se_ln_k(fit, T)
    return np.exp(mid), np.exp(mid - h), np.exp(mid + h)


def expected_factor(sigma_ln, n, T_low, T_high=1000.0, T_target=2000.0):
    """Design tool: half-width factor exp(t * se) of the 95 percent interval at T_target for n points
    evenly spaced in 1000/T between T_low and T_high, if the error of ln k is sigma_ln (no data needed)."""
    x = np.linspace(1000.0 / T_high, 1000.0 / T_low, n)
    sxx = float(np.sum((x - x.mean()) ** 2))
    se = sigma_ln * np.sqrt(1.0 / n + (1000.0 / T_target - x.mean()) ** 2 / sxx)
    return float(np.exp(t95(n - 2) * se))


# %% [markdown]
# ## Step 3: Monte Carlo propagation
# Draw many parameter pairs from a normal distribution with the fitted covariance, compute k at
# the target temperature for each, and take the 2.5 and 97.5 percentiles. It agrees with the
# formula above and keeps working for functions of the parameters that have no simple formula.

# %%
def mc_predict(fit, T_target, draws=40000, seed=7):
    """Returns (median k, 2.5 percent, 97.5 percent) at T_target from parameter draws."""
    rng = np.random.default_rng(seed)
    b = rng.multivariate_normal(fit["b"], fit["cov"], size=draws)
    k = np.exp(b[:, 0] + b[:, 1] * 1000.0 / T_target)
    lo, med, hi = np.percentile(k, [2.5, 50, 97.5])
    return float(med), float(lo), float(hi)


# %% [markdown]
# ## Step 3b: the bootstrap, an interval without a formula
# Monte Carlo above still assumes the fitted parameters are normal. The *bootstrap* assumes
# nothing about the shape: it re-runs the experiment on the computer by reusing the data we
# have, refits every time, and reads the percentiles of the prediction.
# * **residual bootstrap**: keep the fitted line, take the n residuals (corrected for leverage,
#   because a least-squares line hugs its own points), draw n of them with replacement, add
#   them to the line, refit.
# * **pairs bootstrap**: draw n of the (T, k) points with replacement and refit (a draw with
#   all the same temperature cannot give a slope and is dropped).
#
# Both are pure numpy and vectorised: thousands of refits take a few milliseconds. The catch,
# which Step 4 will show, is that with only 7 to 9 points the percentile bootstrap is too
# narrow: the data's own scatter is a noisy estimate of the true scatter and the t factor is
# what pays for that.

# %%
def bootstrap_predict(T, k, T_target, draws=4000, seed=3, method="residual"):
    """(median k, 2.5 percent, 97.5 percent) at T_target by bootstrap. method = "residual" or "pairs"."""
    rng = np.random.default_rng(seed)
    T = np.asarray(T, dtype=float)
    x, y = 1000.0 / T, np.log(np.asarray(k, dtype=float))
    n = x.size
    if n < 3:
        raise ValueError("need at least 3 points")
    xt = 1000.0 / T_target
    if method == "residual":
        X = np.column_stack([np.ones(n), x])
        XtXiXt = np.linalg.solve(X.T @ X, X.T)                 # (2, n): maps y to (b0, b1)
        b = XtXiXt @ y
        res = y - X @ b
        lev = np.einsum("ij,ji->i", X, XtXiXt)                  # leverage of each point
        e = res / np.sqrt(1.0 - lev)
        e -= e.mean()
        ys = X @ b + e[rng.integers(0, n, (draws, n))]
        bs = ys @ XtXiXt.T
        pred = bs[:, 0] + bs[:, 1] * xt
    elif method == "pairs":
        idx = rng.integers(0, n, (draws, n))
        xs, yb = x[idx], y[idx]
        xm, ym = xs.mean(axis=1, keepdims=True), yb.mean(axis=1, keepdims=True)
        sxx = ((xs - xm) ** 2).sum(axis=1)
        ok = sxx > 1e-12
        b1 = ((xs - xm) * (yb - ym)).sum(axis=1)[ok] / sxx[ok]
        b0 = ym[ok, 0] - b1 * xm[ok, 0]
        pred = b0 + b1 * xt
    else:
        raise ValueError("method must be 'residual' or 'pairs'")
    lo, med, hi = np.percentile(np.exp(pred), [2.5, 50, 97.5])
    return float(med), float(lo), float(hi)


# %% [markdown]
# ## Step 4: validate against known truth
# Because we made the data from known A and Ea, we can repeat the whole experiment many times and
# count how often the 95 percent interval at the target temperature contains the true k.
# A correct method gives a coverage close to 0.95.

# %%
def coverage(T, T_target, rel_noise=0.05, repeats=2000, seed=11, A=A_TRUE, Ea_kJ=EA_TRUE):
    """Fraction of repeats whose 95 percent interval at T_target contains the true k, and the mean fitted Ea."""
    rng = np.random.default_rng(seed)
    T = np.asarray(T, dtype=float)
    true = float(arrhenius_k(T_target, A, Ea_kJ))
    hit, eas = 0, []
    for _ in range(repeats):
        k = arrhenius_k(T, A, Ea_kJ) * np.exp(rel_noise * rng.standard_normal(T.size))
        f = fit_with_cov(T, k)
        _, lo, hi = band(f, T_target)
        hit += int(lo[0] <= true <= hi[0])
        eas.append(lnA_Ea(f)["Ea"])
    return hit / repeats, float(np.mean(eas))


def interval_coverage(T, T_target, method, rel_noise=0.05, repeats=1000, seed=11, A=A_TRUE, Ea_kJ=EA_TRUE):
    """Like `coverage`, but for any interval method: "band" (t formula), "mc" or "bootstrap-residual"/"bootstrap-pairs".
    Returns (fraction of repeats whose interval holds the true k, mean upper/lower factor)."""
    rng = np.random.default_rng(seed)
    T = np.asarray(T, dtype=float)
    true = float(arrhenius_k(T_target, A, Ea_kJ))
    hit, fac = 0, []
    for r in range(repeats):
        k = arrhenius_k(T, A, Ea_kJ) * np.exp(rel_noise * rng.standard_normal(T.size))
        if method == "band":
            _, lo, hi = (v[0] for v in band(fit_with_cov(T, k), T_target))
        elif method == "mc":
            _, lo, hi = mc_predict(fit_with_cov(T, k), T_target, draws=4000, seed=r)
        else:
            _, lo, hi = bootstrap_predict(T, k, T_target, draws=2000, seed=r, method=method.split("-")[1])
        hit += int(lo <= true <= hi)
        fac.append(hi / lo)
    return hit / repeats, float(np.mean(fac))


# %% [markdown]
# ## Step 5: weights
# If every point has the same relative error, ln k has the same error everywhere and plain
# least squares is already right. If the lab is much less sure about some points (say 30 percent at
# the lowest temperatures, 3 percent at the highest), weight each point by 1/sigma^2.

# %%
def uneven_experiment(T, sig_lo=0.30, sig_hi=0.03, seed=0):
    """Relative error falls linearly with T from sig_lo (lowest T) to sig_hi (highest T)."""
    T = np.asarray(T, dtype=float)
    sig = sig_lo + (sig_hi - sig_lo) * (T - T.min()) / (T.max() - T.min())
    rng = np.random.default_rng(seed)
    return arrhenius_k(T) * np.exp(sig * rng.standard_normal(T.size)), sig


def ea_scatter_weighted_vs_plain(T, repeats=1500, seed=5):
    """Standard deviation of fitted Ea, plain versus weighted, over repeated uneven experiments."""
    plain, weighted = [], []
    for i in range(repeats):
        k, sig = uneven_experiment(T, seed=seed + i)
        plain.append(lnA_Ea(fit_with_cov(T, k))["Ea"])
        weighted.append(lnA_Ea(fit_with_cov(T, k, sigma_ln=sig))["Ea"])
    return float(np.std(plain, ddof=1)), float(np.std(weighted, ddof=1))


# %% [markdown]
# ## Step 6: two failures
# (a) A narrow 1000/T range makes Ea (and the extrapolation) very uncertain.
# (b) The straight line assumes ONE Arrhenius process. Two parallel channels with different
# Ea give a curved plot; the line is then wrong and the band, which only counts noise, does
# not know it.

# %%
def two_channel_k(T, A1=1.0e7, E1=50.0, A2=1.0e14, E2=200.0):
    """Sum of two Arrhenius channels (1/s); the high-Ea channel takes over at high T."""
    return arrhenius_k(T, A1, E1) + arrhenius_k(T, A2, E2)


def straight_line_on_curved(T, rel_noise=0.03, seed=2):
    k = two_channel_k(T) * np.exp(rel_noise * np.random.default_rng(seed).standard_normal(np.size(T)))
    return fit_with_cov(T, k)


# %% [markdown]
# ## Step 7: see it
# Left: the data, the fitted line, the 95 percent band out to 2000 K and the true law.
# Middle: the one-sigma ellipse of (ln A, Ea), long and thin because the two are correlated.
# Right: the straight-line fit on a two-channel reaction misses the truth at 2000 K.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    T = T_DATA
    k = synthetic(T, 0.05, seed=4)
    f = fit_with_cov(T, k)
    q = lnA_Ea(f)
    print("Ea", round(q["Ea"], 2), "+-", round(q["se_Ea"], 2), "lnA", round(q["lnA"], 3), "+-", round(q["se_lnA"], 3),
          "corr", round(q["corr"], 4))
    mid, lo, hi = band(f, 2000.0)
    print("k(2000 K)", mid[0], lo[0], hi[0], "true", float(arrhenius_k(2000.0)))
    print("MC", mc_predict(f, 2000.0))

    fig, ax = plt.subplots(1, 3, figsize=(13, 3.9))
    Tg = 1000.0 / np.linspace(0.45, 1.8, 120)
    m, l, h = band(f, Tg)
    ax[0].fill_between(1000 / Tg, np.log(l), np.log(h), alpha=0.3, label="95 percent band")
    ax[0].plot(1000 / Tg, np.log(m), label="fit")
    ax[0].plot(1000 / Tg, np.log(arrhenius_k(Tg)), "k:", label="true law")
    ax[0].plot(1000 / T, np.log(k), "o", color="tab:red", label="data")
    ax[0].set_xlabel("1000 / T (1/K x 1000)")
    ax[0].set_ylabel("ln k (k in 1/s)")
    ax[0].set_title("The band flares outside the data")
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=0.3)

    th = np.linspace(0, 2 * np.pi, 100)
    w, V = np.linalg.eigh(q["cov"])
    ell = V @ (np.sqrt(w)[:, None] * np.array([np.cos(th), np.sin(th)]))
    ax[1].plot(q["Ea"] + ell[1], q["lnA"] + ell[0])
    ax[1].plot(q["Ea"], q["lnA"], "o")
    ax[1].plot(EA_TRUE, np.log(A_TRUE), "k*", ms=10, label="truth")
    ax[1].set_xlabel("Ea (kJ/mol)")
    ax[1].set_ylabel("ln A (A in 1/s)")
    ax[1].set_title(f"One-sigma ellipse, correlation {q['corr']:.3f}")
    ax[1].legend(fontsize=8)
    ax[1].grid(alpha=0.3)

    Tc = np.linspace(800, 1600, 9)
    fc = straight_line_on_curved(Tc)
    Tg2 = 1000.0 / np.linspace(0.45, 1.3, 80)
    mc, lc, hc = band(fc, Tg2)
    ax[2].plot(1000 / Tg2, np.log(two_channel_k(Tg2)), "k:", label="true (two channels)")
    ax[2].fill_between(1000 / Tg2, np.log(lc), np.log(hc), alpha=0.3, label="95 percent band")
    ax[2].plot(1000 / Tg2, np.log(mc), label="straight-line fit")
    ax[2].plot(1000 / Tc, np.log(two_channel_k(Tc)), "o", color="tab:red", label="data")
    ax[2].set_xlabel("1000 / T (1/K x 1000)")
    ax[2].set_ylabel("ln k (k in 1/s)")
    ax[2].set_title("Failure: a curved Arrhenius plot")
    ax[2].legend(fontsize=8)
    ax[2].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "band_ellipse_failure.png", dpi=120)
    print("coverage at 2000 K:", coverage(T, 2000.0, repeats=600))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
