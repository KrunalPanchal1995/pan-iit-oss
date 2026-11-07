"""Session 3 (Level 3): overfitting, ridge, cross-validation, bias and variance, robust lines, confounders, collinearity.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: when a model learns the noise
# **A. Real-world problem.** A model with enough knobs can pass through every training point and still
# predict next season badly. Today we measure that (train versus test error), tame it (ridge
# regression), choose settings honestly (k-fold cross-validation), see why (bias and variance),
# defend against bad data points (robust lines), and meet two traps: correlation that is not
# causation, and two inputs that say the same thing. All data are synthetic, so we know the truth.
# This is general education about modelling, not agronomic advice.
#
# **Plan.** (1) polynomial degree and the U-shaped test error, (2) ridge, (3) cross-validation,
# (4) bias-variance, (5) robust lines, (6) confounding, (7) multicollinearity, (8) coefficient
# recovery, (9) mini-project: audit a farm yield model.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

SIGMA = 0.30


def truth(z):
    """True yield response (t/ha) to scaled rainfall z in [-1, 1]."""
    return 3.0 + 1.5 * np.sin(2.5 * np.asarray(z, float))


def make_response(n, seed, sigma=SIGMA):
    rng = np.random.default_rng(seed)
    z = rng.uniform(-1.0, 1.0, n)
    return z, truth(z) + rng.normal(0.0, sigma, n)


# %% [markdown]
# ## Step 1: polynomial degree and overfitting
# A degree-d polynomial has d + 1 coefficients. Low degree cannot bend enough (high *bias*); high
# degree bends to follow the noise (high *variance*). We fit on 20 training seasons and score on 500
# fresh ones. The error measure is the root mean squared error (RMSE, t/ha). Training error only
# ever falls as d grows; test error falls and then rises: a U shape.

# %%
def poly_design(z, degree):
    """Columns 1, z, z^2, ..., z^degree."""
    return np.vander(np.asarray(z, float), degree + 1, increasing=True)


def fit_poly(z, y, degree):
    return np.linalg.lstsq(poly_design(z, degree), np.asarray(y, float), rcond=None)[0]


def rmse(y, yhat):
    return float(np.sqrt(np.mean((np.asarray(y, float) - np.asarray(yhat, float)) ** 2)))


def degree_curve(max_degree=12, n_train=20, seed=1):
    """Train and test RMSE for degrees 0..max_degree."""
    zt, yt = make_response(n_train, seed)
    zs, ys = make_response(500, seed + 1000)
    tr, te = [], []
    for d in range(max_degree + 1):
        c = fit_poly(zt, yt, d)
        tr.append(rmse(yt, poly_design(zt, d) @ c))
        te.append(rmse(ys, poly_design(zs, d) @ c))
    return np.array(tr), np.array(te)


# %% [markdown]
# ## Step 2: ridge regression and standardising
# Ridge adds a penalty lambda * (sum of squared coefficients) to the squared miss, shrinking the
# coefficients. The intercept is not penalised, and because the penalty treats all coefficients
# alike we first **standardise** each feature (subtract its mean, divide by its standard
# deviation) so no feature wins just because of its units. Closed form, on centred data:
#
#     beta = (X^T X + lambda I)^-1 X^T y.
#
# With lambda = 0 this is ordinary least squares.

# %%
def standardise(F, mean=None, sd=None):
    F = np.asarray(F, float)
    mean = F.mean(axis=0) if mean is None else mean
    sd = F.std(axis=0) if sd is None else sd
    return (F - mean) / sd, mean, sd


def ridge_fit(F, y, lam):
    """Ridge on raw features F (no constant column). Returns a dict that ridge_predict can use."""
    Fs, mean, sd = standardise(F)
    ym = float(np.mean(y))
    p = Fs.shape[1]
    beta = np.linalg.solve(Fs.T @ Fs + lam * np.eye(p), Fs.T @ (np.asarray(y, float) - ym))
    return {"beta": beta, "mean": mean, "sd": sd, "ym": ym}


def ridge_predict(model, F):
    Fs = (np.asarray(F, float) - model["mean"]) / model["sd"]
    return model["ym"] + Fs @ model["beta"]


def poly_features(z, degree):
    """z, z^2, ..., z^degree (no constant column)."""
    return poly_design(z, degree)[:, 1:]


def ridge_path(lams, degree=9, n_train=20, seed=1):
    """Largest |standardised coefficient| and test RMSE for each lambda."""
    zt, yt = make_response(n_train, seed)
    zs, ys = make_response(500, seed + 1000)
    big, te = [], []
    for lam in lams:
        m = ridge_fit(poly_features(zt, degree), yt, lam)
        big.append(float(np.abs(m["beta"]).max()))
        te.append(rmse(ys, ridge_predict(m, poly_features(zs, degree))))
    return np.array(big), np.array(te)


def expected_test_rmse(predict, sigma=SIGMA):
    """Population test RMSE (t/ha): sqrt(noise variance + mean squared gap between model and truth over z in [-1, 1])."""
    g = np.linspace(-1.0, 1.0, 2001)
    return float(np.sqrt(sigma ** 2 + np.mean((predict(g) - truth(g)) ** 2)))


# %% [markdown]
# ## Step 3: k-fold cross-validation
# We cannot use the test data to choose settings (that would leak). Instead split the training
# seasons into k folds; train on k - 1 of them, score on the held-out fold, rotate, and average.
# We use it to choose lambda (or the degree).

# %%
def kfold_indices(n, k, seed=0):
    """List of k arrays of held-out indices that together cover 0..n-1 exactly once."""
    idx = np.random.default_rng(seed).permutation(n)
    return [np.sort(f) for f in np.array_split(idx, k)]


def cv_rmse(fit, predict, F, y, k=5, seed=0):
    """Average held-out RMSE. fit(F_train, y_train) -> model, predict(model, F_test) -> yhat."""
    F, y = np.asarray(F, float), np.asarray(y, float)
    errs = []
    for hold in kfold_indices(len(y), k, seed):
        keep = np.setdiff1d(np.arange(len(y)), hold)
        errs.append(rmse(y[hold], predict(fit(F[keep], y[keep]), F[hold])))
    return float(np.mean(errs))


def cv_choose_degree(z, y, max_degree=8, k=5):
    scores = []
    for d in range(1, max_degree + 1):
        scores.append(cv_rmse(lambda F, t: np.linalg.lstsq(np.column_stack([np.ones(len(t)), F]), t, rcond=None)[0],
                              lambda m, F: np.column_stack([np.ones(len(F)), F]) @ m,
                              poly_features(z, d), y, k))
    return int(np.argmin(scores)) + 1, np.array(scores)


def cv_choose_lambda(z, y, lams, degree=9, k=5):
    scores = [cv_rmse(lambda F, t, l=lam: ridge_fit(F, t, l), ridge_predict, poly_features(z, degree), y, k) for lam in lams]
    return float(lams[int(np.argmin(scores))]), np.array(scores)


# %% [markdown]
# ## Step 4: bias and variance by refitting
# Draw many training sets from the same farm, fit each, and look at the predictions at one fixed
# rain value z0. The spread of those predictions is the **variance**; the gap between their mean
# and the truth is the **bias**. Flexible models: small bias, large variance.

# %%
def bias_variance(degree, z0=0.9, repeats=300, n_train=20, seed=0):
    """(bias, variance of the prediction at z0 over refits)."""
    preds = []
    for r in range(repeats):
        z, y = make_response(n_train, seed * 100000 + r)
        preds.append(float((poly_design([z0], degree) @ fit_poly(z, y, degree))[0]))
    preds = np.array(preds)
    return float(preds.mean() - truth(z0)), float(preds.var())


# %% [markdown]
# ## Step 5: outliers and robust lines
# One broken sensor reading can drag a least-squares line far off. Two robust alternatives we write
# ourselves: the **Theil-Sen** line (slope = median of all pairwise slopes, intercept = median of
# y - slope x) and a **Huber** fit (iteratively reweighted least squares: points with large
# residuals get weight k s / |r|, others weight 1; here k = 1.345 and s is the median absolute
# residual / 0.6745).

# %%
def ols_line(x, y):
    X = np.column_stack([np.ones(len(x)), x])
    return tuple(float(v) for v in np.linalg.lstsq(X, np.asarray(y, float), rcond=None)[0])


def theil_sen_line(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    i, j = np.triu_indices(len(x), 1)
    keep = x[j] != x[i]
    slope = float(np.median((y[j] - y[i])[keep] / (x[j] - x[i])[keep]))
    return float(np.median(y - slope * x)), slope


def huber_line(x, y, k=1.345, iters=50):
    x, y = np.asarray(x, float), np.asarray(y, float)
    X = np.column_stack([np.ones(len(x)), x])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    for _ in range(iters):
        r = y - X @ beta
        s = max(np.median(np.abs(r - np.median(r))) / 0.6745, 1e-12)
        w = np.minimum(1.0, k * s / np.maximum(np.abs(r), 1e-12))
        sw = np.sqrt(w)
        beta = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]
    return float(beta[0]), float(beta[1])


def with_outliers(seed=4, n=20):
    """Farm data (Session 2 style) with the three highest-rain seasons wrongly recorded as 0.5 t/ha."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(3.0, 9.0, n)
    y = 1.0 + 0.35 * x + rng.normal(0.0, 0.3, n)
    bad = np.argsort(x)[-3:]
    y = y.copy()
    y[bad] = 0.5
    return x, y


# %% [markdown]
# ## Step 6: correlation is not causation
# Hot days raise ice-cream sales and (through more swimming) drownings. Ice cream does not cause
# drowning: temperature is a **confounder**. The *partial correlation* of A and B given T is the
# correlation of what is left of A and of B after removing the straight-line effect of T. If it
# vanishes, T explained the link.

# %%
def make_confounded(n=500, seed=2):
    rng = np.random.default_rng(seed)
    temp = rng.normal(25.0, 5.0, n)                    # degrees C
    ice = 10.0 + 2.0 * temp + rng.normal(0.0, 5.0, n)  # sales index
    drown = 0.5 + 0.15 * temp + rng.normal(0.0, 0.8, n)
    return temp, ice, drown


def partial_corr(a, b, control):
    """Correlation of a and b after removing the linear effect of control from both."""
    def resid(v):
        c = ols_line(control, v)
        return np.asarray(v, float) - c[0] - c[1] * np.asarray(control, float)
    return float(np.corrcoef(resid(a), resid(b))[0, 1])


# %% [markdown]
# ## Step 7: failure case, multicollinearity
# If two inputs are almost copies of each other (say rain gauge A and rain gauge B), the model
# cannot tell which deserves credit. The columns of X are nearly dependent, the condition number
# of X^T X explodes, and the coefficients swing wildly from one data set to the next, but the
# *predictions* (their sum) stay fine.

# %%
def make_collinear(n=40, seed=0, gap=0.02):
    rng = np.random.default_rng(seed)
    x1 = rng.uniform(3.0, 9.0, n)
    x2 = x1 + rng.normal(0.0, gap * 5, n)               # nearly the same gauge
    y = 1.0 + 0.35 * x1 + rng.normal(0.0, 0.3, n)       # truth uses rain once
    return np.column_stack([np.ones(n), x1, x2]), y


def collinear_experiment(repeats=500, gap=0.02):
    """Coefficient sd of x1, sd of the sum x1 + x2, sd of a prediction at (6, 6), condition number."""
    coefs, preds, conds = [], [], []
    for r in range(repeats):
        X, y = make_collinear(40, r, gap)
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        coefs.append(beta)
        preds.append(beta @ np.array([1.0, 6.0, 6.0]))
        conds.append(np.linalg.cond(X.T @ X))
    coefs = np.array(coefs)
    return {"sd_b1": float(coefs[:, 1].std()), "sd_sum": float((coefs[:, 1] + coefs[:, 2]).std()),
            "sd_pred": float(np.std(preds)), "cond": float(np.median(conds))}


# %% [markdown]
# ## Step 8: recovery of the true coefficients and sensitivity
# Because we generated the data, we can check the fit against the truth: a 95 percent range
# beta +- 1.96 SE should contain the true slope in about 95 percent of repeated data sets. And SE of
# the slope is sigma / sqrt(Sxx), so quadrupling n halves it, and doubling the noise doubles it.

# %%
def slope_stats(n, sigma, repeats=2000, seed=0, a=1.0, b=0.35):
    """(fraction of repeats whose slope +- 1.96 SE holds b, mean SE of the slope, sd of the fitted slopes)."""
    rng = np.random.default_rng(seed)
    hit, ses, slopes = 0, [], []
    for _ in range(repeats):
        x = rng.uniform(3.0, 9.0, n)
        y = a + b * x + rng.normal(0.0, sigma, n)
        a_h, b_h = ols_line(x, y)
        s = math.sqrt(np.sum((y - a_h - b_h * x) ** 2) / (n - 2))
        se = s / math.sqrt(np.sum((x - x.mean()) ** 2))
        hit += abs(b_h - b) <= 1.96 * se
        ses.append(se)
        slopes.append(b_h)
    return hit / repeats, float(np.mean(ses)), float(np.std(slopes))


# %% [markdown]
# ## Step 9: mini-project, build and audit a yield model
# A synthetic farm data set of 60 seasons: rain, fertiliser, mean temperature. We build the model
# by least squares, audit it (R^2, residual checks, cross-validation against a mean-only model and
# against a too-flexible one), and report a 95 percent prediction interval for next season.

# %%
FARM_COEF = np.array([0.5, 0.30, 0.10, -0.04])   # intercept, rain (100 mm), fertiliser (10 kg/ha), temperature (C)


def farm_dataset(n=60, seed=21, sigma=0.35):
    rng = np.random.default_rng(seed)
    rain = rng.uniform(3.0, 9.0, n)
    fert = rng.uniform(0.0, 10.0, n)
    temp = rng.normal(24.0, 2.5, n)
    X = np.column_stack([np.ones(n), rain, fert, temp])
    return X, X @ FARM_COEF + rng.normal(0.0, sigma, n)


def prediction_interval_multi(X, y, x0, level=0.95):
    """Prediction interval for one new season with inputs x0 (including the leading 1)."""
    n, p = X.shape
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    s2 = np.sum((y - X @ beta) ** 2) / (n - p)
    lev = float(x0 @ np.linalg.solve(X.T @ X, x0))
    # t quantile by bisection on the normal-free approach: reuse a simple series-free Simpson integral
    c = math.exp(math.lgamma((n - p + 1) / 2) - math.lgamma((n - p) / 2)) / math.sqrt((n - p) * math.pi)

    def cdf(t):
        u = np.linspace(0.0, abs(t), 2001)
        d = c * (1 + u ** 2 / (n - p)) ** (-(n - p + 1) / 2)
        h = u[1] - u[0]
        return 0.5 + math.copysign(h / 3 * (d[0] + d[-1] + 4 * d[1:-1:2].sum() + 2 * d[2:-1:2].sum()), t)

    lo, hi = 0.0, 20.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if cdf(mid) < 0.5 + level / 2 else (lo, mid)
    half = (lo + hi) / 2 * math.sqrt(s2 * (1 + lev))
    yh = float(x0 @ beta)
    return yh, yh - half, yh + half


def _ls_fit(F, t):
    return np.linalg.lstsq(np.column_stack([np.ones(len(t)), F]), t, rcond=None)[0]


def _ls_predict(m, F):
    return np.column_stack([np.ones(len(F)), F]) @ m


def expand_quadratic(F):
    """Inputs plus all their squares and pairwise products (a much more flexible model)."""
    F = np.asarray(F, float)
    cols = [F[:, i] for i in range(F.shape[1])]
    cols += [F[:, i] * F[:, j] for i in range(F.shape[1]) for j in range(i, F.shape[1])]
    return np.column_stack(cols)


def farm_audit(X, y, k=6):
    """Cross-validated RMSE (t/ha) of: mean only, rain only, three inputs, three inputs with squares and products."""
    F = X[:, 1:]
    zero = lambda F_, t: float(np.mean(t))
    return {
        "mean only": cv_rmse(zero, lambda m, F_: np.full(len(F_), m), F, y, k),
        "rain only": cv_rmse(_ls_fit, _ls_predict, F[:, :1], y, k),
        "three inputs": cv_rmse(_ls_fit, _ls_predict, F, y, k),
        "too flexible": cv_rmse(_ls_fit, _ls_predict, expand_quadratic(F), y, k),
    }


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    tr, te = degree_curve()
    print("train RMSE by degree:", tr.round(2))
    print("test  RMSE by degree:", te.round(2))
    print("best degree on test:", int(np.argmin(te)), "with RMSE", round(float(te.min()), 3), "(noise sd 0.30)")
    lams = np.array([0, 0.01, 0.1, 1, 10, 100, 1000])
    big, tte = ridge_path(lams)
    print("ridge: max |coef|", big.round(2), "test RMSE", tte.round(3))
    zt, yt = make_response(20, 1)
    print("CV degree:", cv_choose_degree(zt, yt)[0], " CV lambda:", cv_choose_lambda(zt, yt, np.array([1e-3, 1e-2, 1e-1, 1, 10, 100]))[0])
    for d in (1, 3, 9):
        print("bias, variance at z0=0.9, degree", d, np.round(bias_variance(d), 4))
    x, y = with_outliers()
    print("ols", np.round(ols_line(x, y), 3), "theil-sen", np.round(theil_sen_line(x, y), 3), "huber", np.round(huber_line(x, y), 3), "(true 1.0, 0.35)")
    t, i, d = make_confounded()
    print("raw corr", round(float(np.corrcoef(i, d)[0, 1]), 3), "partial given temp", round(partial_corr(i, d, t), 3))
    print("collinear:", {k: round(v, 3) for k, v in collinear_experiment().items()})
    for n, s in ((25, 0.3), (100, 0.3), (25, 0.6)):
        print("slope stats n, sigma", n, s, np.round(slope_stats(n, s), 4))
    X, yy = farm_dataset()
    beta = np.linalg.lstsq(X, yy, rcond=None)[0]
    print("farm coefficients", beta.round(3), "R2", round(1 - np.sum((yy - X @ beta) ** 2) / np.sum((yy - yy.mean()) ** 2), 3))
    print("audit:", {k: round(v, 3) for k, v in farm_audit(X, yy).items()})
    print("next season (550 mm, 60 kg/ha, 25 C):", np.round(prediction_interval_multi(X, yy, np.array([1.0, 5.5, 6.0, 25.0])), 2))

    fig, axs = plt.subplots(1, 3, figsize=(14, 4))
    axs[0].plot(range(len(tr)), tr, "o-", label="training error")
    axs[0].plot(range(len(te)), te, "s-", label="test error")
    axs[0].set_ylim(0, 1.5)
    axs[0].axvline(int(np.argmin(te)), color="gray", ls=":")
    axs[0].set_xlabel("polynomial degree")
    axs[0].set_ylabel("RMSE (t/ha)")
    axs[0].set_title("Test error is U-shaped")
    axs[0].legend()
    axs[1].semilogx(lams[1:], tte[1:], "o-")
    axs[1].axhline(tte[0], color="tab:red", ls="--", label="lambda = 0 (least squares)")
    axs[1].set_xlabel("ridge lambda")
    axs[1].set_ylabel("test RMSE (t/ha)")
    axs[1].set_title("Ridge tames degree 9")
    axs[1].legend()
    xo, yo = with_outliers()
    g = np.linspace(3, 9, 10)
    axs[2].scatter(xo, yo)
    for name, f in (("least squares", ols_line), ("Theil-Sen", theil_sen_line), ("Huber", huber_line)):
        a_, b_ = f(xo, yo)
        axs[2].plot(g, a_ + b_ * g, label=name)
    axs[2].set_xlabel("rainfall (hundreds of mm)")
    axs[2].set_ylabel("yield (t/ha)")
    axs[2].set_title("Three wrong records drag least squares")
    axs[2].legend()
    for ax in axs:
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "overfit_ridge_robust.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
