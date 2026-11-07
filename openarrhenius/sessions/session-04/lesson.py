"""Session 4 (Level 3): fit a curved Arrhenius plot, k = k1(T) + k2(T), with an uncertainty band.

Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: fit a curved Arrhenius plot
# **A. Real-world problem.** Session 3 ended with a warning: when two reactions run in parallel,
# the plot of ln k against 1000/T bends, and a straight line predicts k at 2000 K about nine to
# fifty times too low (it depends how cold the data start) while its own band says it is
# sure. A combustion or pyrolysis model needs the right number, so we fit **two channels**
# and report how sure we are.
#
# **Plan.** (1) the two-channel model, (2) fit it by nonlinear least squares (Levenberg-Marquardt,
# written out in numpy), (3) the covariance and why the parameters are hard to pin down while the
# prediction is not, (4) the band at 2000 K, (5) is the extra channel justified? (6) validate
# against known truth, (7) three ways it fails: data that stop too cool, bad start values,
# too few points.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R_GAS = 8.314462618          # J/(mol K)
# the same two-channel truth as Session 3: lnA1, E1 (kJ/mol), lnA2, E2 (kJ/mol)
A1, E1 = 1.0e7, 50.0         # low-Ea channel, wins when it is cool
A2, E2 = 1.0e14, 200.0       # high-Ea channel, wins when it is hot
P_TRUE = np.array([np.log(A1), E1, np.log(A2), E2])
T_DATA = np.linspace(500.0, 1600.0, 12)     # K, the roadmap data window
T_TARGET = 2000.0                            # K, where the engine model needs k

# two-sided 95 percent Student t factors by degrees of freedom
_T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262,
        10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086, 30: 2.042}


def t95(df):
    """Student t factor for a 95 percent two-sided interval (table; next lower tabulated df, so slightly wide)."""
    if df >= 30:
        return 2.042 if df < 120 else 1.98
    return _T95[max(d for d in _T95 if d <= df)]


# %% [markdown]
# ## Step 1: the model
# Each channel is an Arrhenius term, so with x = 1000/T and E in kJ/mol
#
#     k(T) = exp(lnA1 - E1 x / R) + exp(lnA2 - E2 x / R)
#
# (R = 8.314 J/(mol K), E in kJ/mol, x = 1000/T: the 1000 that turns kJ into J cancels the 1000 in
# x, so the exponent is simply E x / R). We fit **ln k**, as in Sessions 1 to 3,
# so a 3 percent error is a 0.03 error in ln k at every temperature. ln(a + b) = logaddexp(ln a, ln b),
# which never overflows.
#
# The cool end of the plot is the low-Ea channel (a shallow line), the hot end is the high-Ea
# channel (a steep line), and the **crossover** is where the two terms are equal.

# %%
def two_channel_k(T, p=P_TRUE):
    """k (1/s) from p = (lnA1, E1, lnA2, E2)."""
    return np.exp(ln_k(p, T))


def ln_k(p, T):
    x = 1000.0 / np.asarray(T, dtype=float)
    return np.logaddexp(p[0] - p[1] * x / R_GAS, p[2] - p[3] * x / R_GAS)


def jacobian(p, T):
    """d ln k / d (lnA1, E1, lnA2, E2), shape (n, 4). The weights w1, w2 are each channel's share of k."""
    x = 1000.0 / np.asarray(T, dtype=float)
    t1, t2 = p[0] - p[1] * x / R_GAS, p[2] - p[3] * x / R_GAS
    y = np.logaddexp(t1, t2)
    w1, w2 = np.exp(t1 - y), np.exp(t2 - y)
    return np.column_stack([w1, -w1 * x / R_GAS, w2, -w2 * x / R_GAS])


def crossover_T(p):
    """Temperature (K) at which the two channels contribute equally; None if the lines never cross."""
    dE = p[1] - p[3]
    if dE == 0.0:
        return None
    x = R_GAS * (p[0] - p[2]) / dE
    return float(1000.0 / x) if x > 0 else None


def channel_share(p, T):
    """Fraction of k carried by the second (high-Ea) channel."""
    x = 1000.0 / np.asarray(T, dtype=float)
    return np.exp(p[2] - p[3] * x / R_GAS - ln_k(p, T))


def synthetic(T, rel_noise=0.03, seed=0, p=P_TRUE):
    rng = np.random.default_rng(seed)
    T = np.asarray(T, dtype=float)
    return two_channel_k(T, p) * np.exp(rel_noise * rng.standard_normal(T.size))


# %% [markdown]
# ## Step 2: fitting it
# Unlike a straight line there is no formula. Start from a guess p, linearise ln k around it with
# the Jacobian J (the table of slopes d ln k / d p), solve for the best step, and repeat:
#
#     (J^T J + lambda diag(J^T J)) step = J^T r,     r = ln k_data - ln k_model.
#
# This is **Levenberg-Marquardt**: lambda large = a short careful step downhill, lambda small =
# the full Gauss-Newton step. A step that lowers the residual sum of squares (RSS) is kept and
# lambda shrinks; a step that does not is rejected and lambda grows. Columns are scaled to unit
# length first, because ln A (about 30) and E (about 200) differ by a factor ten.
#
# A start guess matters because the surface has flat valleys. We try three: split the data
# into a cool and a hot part, fit a straight line to each, and use the lines as the two
# channels. Then we keep whichever start ends with the smallest RSS.

# %%
def _lm(y, T, p0, iters=400):
    p = np.array(p0, dtype=float)
    res = y - ln_k(p, T)
    cur = float(res @ res)
    lam = 1e-2
    for _ in range(iters):
        J = jacobian(p, T)
        s = np.sqrt((J ** 2).sum(axis=0)) + 1e-12
        Js = J / s
        A, g = Js.T @ Js, Js.T @ res
        moved = False
        for _try in range(60):
            try:
                step = np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-12), g) / s
            except np.linalg.LinAlgError:
                lam *= 10.0
                continue
            pn = p + step
            rn = y - ln_k(pn, T)
            new = float(rn @ rn)
            if np.isfinite(new) and new < cur:
                done = cur - new < 1e-14 * max(cur, 1e-300) or np.abs(step / s).max() < 1e-10
                p, res, cur, lam, moved = pn, rn, new, max(lam / 3.0, 1e-12), True
                break
            lam *= 4.0
        if not moved or done:
            break
    return p, cur


def start_values(T, k):
    """Three start guesses: split the data after 1/3, 1/2 and 2/3 of the points; a straight line on
    each part (ln k against 1000/T) gives one channel."""
    T, k = np.asarray(T, dtype=float), np.asarray(k, dtype=float)
    order = np.argsort(T)
    T, k = T[order], k[order]
    x, y = 1000.0 / T, np.log(k)                 # T rises, so x falls: the first points are the hot ones
    n = T.size
    out = []
    for h in sorted({max(2, n // 3), max(2, n // 2), max(2, (2 * n) // 3)}):
        h = min(h, n - 2)
        b1h, b0h = np.polyfit(x[:h], y[:h], 1)           # hot part
        b1c, b0c = np.polyfit(x[h:], y[h:], 1)           # cool part
        out.append([b0c, -b1c * R_GAS, b0h, -b1h * R_GAS])
    return out


def fit_two_channel(T, k, starts=None):
    """Nonlinear least squares of ln k. Needs at least 5 points (4 parameters + 1 degree of freedom).
    Returns dict: p (lnA1, E1, lnA2, E2 with E1 <= E2), cov (4x4), df, s (error of ln k), rss, n_starts."""
    T, k = np.asarray(T, dtype=float), np.asarray(k, dtype=float)
    n = T.size
    if n < 5:
        raise ValueError("need at least 5 points: 4 parameters and one degree of freedom to estimate the error")
    y = np.log(k)
    best = None
    starts = start_values(T, k) if starts is None else [list(s) for s in starts]
    for p0 in starts:
        p, rss = _lm(y, T, p0)
        if best is None or rss < best[1]:
            best = (p, rss)
    p, rss = best
    if p[1] > p[3]:                                       # label the cool channel 1: swap the channels
        p = p[[2, 3, 0, 1]]
    df = n - 4
    s = float(np.sqrt(rss / df))
    J = jacobian(p, T)
    sc = np.sqrt((J ** 2).sum(axis=0)) + 1e-300
    Js = J / sc
    with np.errstate(all="ignore"):
        cov = s ** 2 * np.linalg.pinv(Js.T @ Js, rcond=1e-14) / np.outer(sc, sc)
    return {"p": p, "cov": cov, "df": df, "s": s, "rss": float(rss), "n_starts": len(starts)}


def param_table(fit):
    """Standard errors and the correlation matrix of (lnA1, E1, lnA2, E2)."""
    sd = np.sqrt(np.maximum(np.diag(fit["cov"]), 0.0))
    with np.errstate(divide="ignore", invalid="ignore"):
        corr = fit["cov"] / np.outer(sd, sd)
    return {"se": sd, "corr": corr}


# %% [markdown]
# ## Step 3: why the parameters are hard to identify
# The covariance of the fitted parameters is s^2 (J^T J)^-1, the same idea as Session 3 with the
# Jacobian in place of the two columns (1, x). Look at its correlation matrix: lnA1 and E1
# move together (about +0.99), and so do lnA2 and E2. Raising E1 by a little and lnA1 by the
# matching amount leaves ln k almost unchanged over the data; the fit can tell the *combination*
# but not each one. The eigenvalues of J^T J (after scaling the columns) say the same thing:
# the ratio of the largest to the smallest is the *condition number*, and a large one means a
# long flat valley in which very different parameters fit almost equally well.
#
# The prediction is a different matter. It is one particular combination of the four parameters,
# and the data can fix that combination well even when each parameter alone is poorly known.

# %%
def condition_number(fit, T):
    """Largest over smallest eigenvalue of the column-scaled J^T J (a large number = a flat valley)."""
    J = jacobian(fit["p"], T)
    Js = J / (np.sqrt((J ** 2).sum(axis=0)) + 1e-300)
    w = np.linalg.eigvalsh(Js.T @ Js)
    return float(w[-1] / max(w[0], 1e-300))


# %% [markdown]
# ## Step 4: the band at any temperature
# The delta method: at temperature T the fitted ln k has gradient g = d ln k / d p (one row of
# the Jacobian), so its variance is g^T cov g, exactly like Session 3 but with four parameters.
# The 95 percent interval is ln k +- t * se with t for n - 4 degrees of freedom, and on the k
# axis it is a factor exp(+-t se). A Monte Carlo draw from the fitted covariance gives the same
# answer when the band is narrow, and shows when it is not.

# %%
def se_ln_k(fit, T):
    g = jacobian(fit["p"], np.atleast_1d(np.asarray(T, dtype=float)))
    return np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", g, fit["cov"], g), 0.0))


def band(fit, T):
    """(central k, lower k, upper k): 95 percent interval for the mean ln k."""
    T = np.atleast_1d(np.asarray(T, dtype=float))
    mid = ln_k(fit["p"], T)
    h = t95(fit["df"]) * se_ln_k(fit, T)
    with np.errstate(over="ignore"):
        return np.exp(mid), np.exp(mid - h), np.exp(mid + h)


def mc_predict(fit, T_target, draws=40000, seed=7):
    """(median k, 2.5 percent, 97.5 percent) at T_target from parameter draws with the fitted covariance."""
    rng = np.random.default_rng(seed)
    p = rng.multivariate_normal(fit["p"], fit["cov"], size=draws, check_valid="ignore")
    k = np.exp(ln_k(p.T, T_target))
    lo, med, hi = np.percentile(k, [2.5, 50, 97.5])
    return float(med), float(lo), float(hi)


# %% [markdown]
# ## Step 5: is the second channel justified?
# More parameters always fit better, so we need a fair comparison. The **corrected Akaike
# criterion** charges a price for each parameter:
#
#     AICc = n ln(RSS / n) + 2 m + 2 m (m + 1) / (n - m - 1),    m = number of parameters.
#
# A difference of more than about 10 in favour of one model is overwhelming. Also look at the
# residuals of the straight line: a curve leaves them in a run of positive, then negative,
# then positive again; noise would not.

# %%
def line_fit(T, k):
    """Straight line ln k = b0 + b1 * 1000/T. Returns dict b, rss, s, df."""
    x, y = 1000.0 / np.asarray(T, dtype=float), np.log(np.asarray(k, dtype=float))
    b1, b0 = np.polyfit(x, y, 1)
    res = y - (b0 + b1 * x)
    rss = float(res @ res)
    return {"b": np.array([b0, b1]), "rss": rss, "df": x.size - 2, "s": float(np.sqrt(rss / (x.size - 2))), "res": res}


def line_k(fit, T):
    return np.exp(fit["b"][0] + fit["b"][1] * 1000.0 / np.asarray(T, dtype=float))


def aicc(rss, n, m):
    if n - m - 1 <= 0:
        raise ValueError("AICc needs more points than parameters + 1")
    return n * np.log(max(rss, 1e-300) / n) + 2 * m + 2 * m * (m + 1) / (n - m - 1)


def compare_models(T, k):
    """AICc of the straight line (2 parameters) and of the two channels (4). Needs at least 6 points."""
    T, k = np.asarray(T, dtype=float), np.asarray(k, dtype=float)
    n = T.size
    if n < 6:
        raise ValueError("model comparison needs at least 6 points")
    fl, f2 = line_fit(T, k), fit_two_channel(T, k)
    a1, a2 = aicc(fl["rss"], n, 2), aicc(f2["rss"], n, 4)
    return {"aicc_line": float(a1), "aicc_two": float(a2), "delta": float(a1 - a2), "s_line": fl["s"], "s_two": f2["s"]}


def sign_runs(res):
    """Number of runs of equal sign in the residuals ordered by temperature (a curve gives few runs)."""
    sg = np.sign(res)
    return int(1 + np.sum(sg[1:] != sg[:-1]))


# %% [markdown]
# ## Step 6: validate against known truth
# Repeat the whole experiment many times with new noise and count (a) how often the prediction at
# 2000 K lands within a factor 1.5 of the truth (the goal), and (b) how often the 95 percent
# interval contains the truth (a correct method gives about 0.95).

# %%
def trials(T, T_target=T_TARGET, rel_noise=0.03, repeats=1000, seed=100, p=P_TRUE):
    """Repeat experiment+fit. Returns dict: within15, coverage, median_ratio (fit/true), median_factor (upper/lower)."""
    T = np.asarray(T, dtype=float)
    true = float(two_channel_k(T_target, p))
    w15 = cov_hit = 0
    ratios, facs = [], []
    for i in range(repeats):
        k = synthetic(T, rel_noise, seed + i, p)
        try:
            f = fit_two_channel(T, k)
            m, lo, hi = (v[0] for v in band(f, T_target))
        except (ValueError, np.linalg.LinAlgError, FloatingPointError):
            ratios.append(np.nan)
            facs.append(np.nan)
            continue
        if not (np.isfinite(m) and np.isfinite(lo) and np.isfinite(hi)):
            ratios.append(np.nan)
            facs.append(np.nan)
            continue
        r = m / true
        w15 += int(1.0 / 1.5 < r < 1.5)
        cov_hit += int(lo <= true <= hi)
        ratios.append(r)
        facs.append(hi / lo)
    return {"within15": w15 / repeats, "coverage": cov_hit / repeats,
            "median_ratio": float(np.nanmedian(ratios)), "median_factor": float(np.nanmedian(facs))}


# %% [markdown]
# ## Step 7: three failures
# (a) **The data stop too cool.** If the hottest measurement is below the crossover (1119 K),
# the second channel barely shows. The fit then has a wide range of E2 that all describe the
# data, and the prediction at 2000 K swings by orders of magnitude. The band is the
# warning, and `trials` over different hottest temperatures draws the line.
# (b) **A bad start.** A single start can end in a poorer valley; the three start guesses
# make that rare, and the RSS tells you which one won.
# (c) **Too few points.** Four parameters need at least five points; with five or six the
# t factor for 1 or 2 degrees of freedom makes the band very wide, honestly.

# %%
def reach_study(t_max_list, t_min=500.0, n=12, repeats=300, seed=100):
    """For data spanning t_min..t_max, the share within a factor 1.5 at 2000 K and the median band factor."""
    out = []
    for tm in t_max_list:
        r = trials(np.linspace(t_min, tm, n), repeats=repeats, seed=seed)
        out.append((float(tm), r["within15"], r["coverage"], r["median_factor"]))
    return out


# %% [markdown]
# ## Step 8: see it
# Left: the data, the straight line, the two-channel fit and its band out to 2000 K.
# Middle: the two channels and their sum; the crossover is where they meet.
# Right: the share of repeated experiments that land within a factor 1.5, against the hottest
# temperature measured.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    T = T_DATA
    k = synthetic(T, 0.03, seed=0)
    f = fit_two_channel(T, k)
    fl = line_fit(T, k)
    pt = param_table(f)
    mid, lo, hi = band(f, T_TARGET)
    true = float(two_channel_k(T_TARGET))
    print("p", np.round(f["p"], 3), "se", np.round(pt["se"], 3), "s", round(f["s"], 4), "df", f["df"])
    print("k(2000 K)", mid[0], lo[0], hi[0], "true", true, "line", float(line_k(fl, T_TARGET)))
    print("crossover", crossover_T(f["p"]), "cond", condition_number(f, T))
    print("model comparison", compare_models(T, k))
    print("MC", mc_predict(f, T_TARGET))

    fig, ax = plt.subplots(1, 3, figsize=(13, 3.9))
    Tg = 1000.0 / np.linspace(0.45, 2.05, 160)
    m, l, h = band(f, Tg)
    ax[0].fill_between(1000 / Tg, np.log(l), np.log(h), alpha=0.3, label="95 percent band")
    ax[0].plot(1000 / Tg, np.log(m), label="two-channel fit")
    ax[0].plot(1000 / Tg, np.log(line_k(fl, Tg)), "--", label="straight line")
    ax[0].plot(1000 / Tg, np.log(two_channel_k(Tg)), "k:", label="true law")
    ax[0].plot(1000 / T, np.log(k), "o", color="tab:red", label="data")
    ax[0].errorbar([1000.0 / T_TARGET], [np.log(mid[0])], yerr=[[np.log(mid[0] / lo[0])], [np.log(hi[0] / mid[0])]],
                   fmt="s", color="tab:green", capsize=4, label="2000 K, 95 percent")
    ax[0].set_xlabel("1000 / T (1/K x 1000)")
    ax[0].set_ylabel("ln k (k in 1/s)")
    ax[0].set_title("The line misses 2000 K, the fit does not")
    ax[0].legend(fontsize=8, loc="upper right")
    ax[0].grid(alpha=0.3)

    xx = 1000.0 / Tg
    ax[1].plot(xx, (P_TRUE[0] - P_TRUE[1] * xx / R_GAS), label="channel 1 (E = 50)")
    ax[1].plot(xx, (P_TRUE[2] - P_TRUE[3] * xx / R_GAS), label="channel 2 (E = 200)")
    ax[1].plot(xx, np.log(two_channel_k(Tg)), "k", lw=2, label="sum")
    ax[1].axvline(1000.0 / crossover_T(P_TRUE), color="gray", ls=":")
    ax[1].set_ylim(-6, 22)
    ax[1].set_xlabel("1000 / T (1/K x 1000)")
    ax[1].set_ylabel("ln k (k in 1/s)")
    ax[1].set_title("Two lines add up to a curve")
    ax[1].legend(fontsize=8, loc="lower left")
    ax[1].grid(alpha=0.3)

    rs = reach_study([700, 800, 900, 1000, 1100, 1200, 1300, 1450, 1600], repeats=150)
    ax[2].plot([r[0] for r in rs], [100 * r[1] for r in rs], "o-")
    ax[2].axvline(crossover_T(P_TRUE), color="gray", ls=":")
    ax[2].set_xlabel("hottest measured temperature (K)")
    ax[2].set_ylabel("predictions within factor 1.5 (%)")
    ax[2].set_title("Measure past the crossover")
    ax[2].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "curved_fit.png", dpi=120)
    print("trials 500-1600 K:", trials(T, repeats=600))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
