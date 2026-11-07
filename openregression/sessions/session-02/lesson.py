"""Session 2 (Level 2): least squares from the normal equations, R squared, residual plots, two inputs, prediction intervals.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the mathematics of the best line
# **A. Real-world problem.** Session 1 found the best line by a formula we did not derive. Now we
# derive it, measure how much of the ups and downs in yield the line explains (R squared), learn
# to read the residuals for warning signs, add a second input (fertiliser), and answer a design
# question: how much rain do we need to be 95 percent sure of reaching a target yield? All data
# are synthetic (made by code with known coefficients), so we can check our answers.
#
# **Plan.** (1) normal equations, (2) R squared, (3) residual patterns, (4) two inputs,
# (5) prediction interval and a coverage test, (6) extrapolation, (7) design problem.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# true coefficients used to generate the data (rain in hundreds of mm, yield in t/ha)
A_TRUE, B_TRUE, SIGMA = 1.0, 0.35, 0.30


def make_farm(n, seed, a=A_TRUE, b=B_TRUE, sigma=SIGMA):
    """n seasons: rain uniform in [3, 9] (100 mm), yield = a + b rain + normal noise (sd sigma)."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(3.0, 9.0, n)
    return x, a + b * x + rng.normal(0.0, sigma, n)


# %% [markdown]
# ## Step 1: the normal equations
# Write the model as y = X beta, where each row of X is (1, x) and beta = (a, b). The total
# squared miss is S(beta) = (y - X beta)^T (y - X beta). Setting its derivative with respect to
# beta to zero gives -2 X^T (y - X beta) = 0, i.e. the **normal equations**
#
#     (X^T X) beta = X^T y.
#
# For a line, X^T X = [[n, sum x], [sum x, sum x^2]] and the solution reduces to
# b = Sxy / Sxx, a = ybar - b xbar (Session 1).

# %%
def design_line(x):
    """Matrix X with a column of ones and a column of x."""
    x = np.asarray(x, float)
    return np.column_stack([np.ones_like(x), x])


def fit_normal(x, y):
    """Solve the normal equations for y = a + b x. Returns (a, b)."""
    X = design_line(x)
    a, b = np.linalg.solve(X.T @ X, X.T @ np.asarray(y, float))
    return float(a), float(b)


# %% [markdown]
# ## Step 2: R squared
# Without any model the best guess is the mean yield, with total squared miss
# SS_tot = sum (y - ybar)^2. The line leaves SS_res = sum (y - yhat)^2. The fraction of the
# variation explained is **R^2 = 1 - SS_res / SS_tot**. For one input it equals the square of the
# correlation r. R^2 = 1 is a perfect fit and R^2 = 0 means no better than the mean. It does not
# say the model is correct (see the residual plots next) or that x causes y.

# %%
def r_squared(y, yhat):
    y, yhat = np.asarray(y, float), np.asarray(yhat, float)
    return float(1.0 - np.sum((y - yhat) ** 2) / np.sum((y - y.mean()) ** 2))


# %% [markdown]
# ## Step 3: residual plots
# If a straight line is the right model, the residuals look like random scatter around zero with no
# pattern against x. A curve, a funnel (spread growing with x) or a drift means the model is wrong
# even when R^2 is high. We test with data from a saturating curve (extra rain helps less and less).

# %%
def saturating_yield(x):
    """A curved truth: yield levels off as rain grows (t/ha)."""
    return 0.2 + 5.0 * (1.0 - np.exp(-0.35 * np.asarray(x, float)))


def make_curved(n, seed, sigma=0.15, lo=1.0, hi=10.0):
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(lo, hi, n))
    return x, saturating_yield(x) + rng.normal(0.0, sigma, n)


def residual_curvature(x, resid):
    """Correlation of the residuals with (x - mean)^2. Near 0: no bend; near +-1: leftover curve."""
    x = np.asarray(x, float)
    return float(np.corrcoef((x - x.mean()) ** 2, resid)[0, 1])


# %% [markdown]
# ## Step 4: two inputs (multiple regression)
# With rain r and fertiliser f (in 10 kg/ha units): y = c0 + c1 r + c2 f. The matrix X now has
# three columns (1, r, f). `numpy.linalg.lstsq` solves the least-squares problem. The solution must
# satisfy the normal equations: X^T (y - X beta) = 0, meaning the residuals are perpendicular to
# every column of X. Standard errors come from s^2 (X^T X)^-1, with s^2 = SS_res / (n - p).

# %%
C_TRUE = np.array([0.8, 0.30, 0.12])


def make_two_inputs(n, seed, coef=C_TRUE, sigma=0.25):
    rng = np.random.default_rng(seed)
    rain = rng.uniform(3.0, 9.0, n)
    fert = rng.uniform(0.0, 10.0, n)
    X = np.column_stack([np.ones(n), rain, fert])
    return X, X @ coef + rng.normal(0.0, sigma, n)


def multi_fit(X, y):
    """Least squares by lstsq. Returns coefficients, standard errors and residuals."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    res = y - X @ beta
    s2 = res @ res / (len(y) - X.shape[1])
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    return beta, se, res


# %% [markdown]
# ## Step 5: prediction interval
# A *confidence* interval is about the average yield at rain x0; a *prediction* interval is about one
# new season's yield, so it must also include the season's own noise. With n points, p = 2 fitted
# coefficients and s^2 = SS_res / (n - 2):
#
#     yhat0 +- t * s * sqrt(1 + 1/n + (x0 - xbar)^2 / Sxx),    t = t quantile (0.975, n - 2 df).
#
# The interval is narrowest at xbar and widens away from the data. We need the t quantile; we
# compute it by integrating the t density (no scipy).

# %%
def t_cdf(t, df):
    """Cumulative distribution of Student's t, by Simpson integration of its density."""
    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
    u = np.linspace(0.0, abs(t), 2001)
    dens = c * (1 + u ** 2 / df) ** (-(df + 1) / 2)
    h = u[1] - u[0]
    area = h / 3 * (dens[0] + dens[-1] + 4 * dens[1:-1:2].sum() + 2 * dens[2:-1:2].sum())
    return 0.5 + math.copysign(area, t)


def t_quantile(p, df):
    """Inverse of t_cdf by bisection."""
    lo, hi = -50.0, 50.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if t_cdf(mid, df) < p else (lo, mid)
    return (lo + hi) / 2


def prediction_interval(x0, x, y, level=0.95):
    """(yhat, lower, upper) for one new observation at x0."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    a, b = fit_normal(x, y)
    s = math.sqrt(np.sum((y - a - b * x) ** 2) / (n - 2))
    sxx = np.sum((x - x.mean()) ** 2)
    half = t_quantile(0.5 + level / 2, n - 2) * s * np.sqrt(1 + 1 / n + (np.asarray(x0) - x.mean()) ** 2 / sxx)
    yh = a + b * np.asarray(x0)
    return yh, yh - half, yh + half


def t_approx(df, z=1.959964):
    """Cornish-Fisher approximation of the 0.975 t quantile (good for df >= 4); used by the app."""
    return z + (z ** 3 + z) / (4 * df) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * df ** 2)


def expected_half_width(x0, n, sigma=SIGMA):
    """Typical 95 percent prediction half-width (t/ha) at rain x0 for n seasons with rain uniform in [3, 9] (xbar 6, Sxx about 3 n)."""
    return t_approx(n - 2) * sigma * float(np.sqrt(1 + 1 / n + (x0 - 6.0) ** 2 / (3.0 * n)))


def coverage(n=20, x0=6.0, repeats=2000, seed=5, level=0.95):
    """Fraction of repeats in which the interval catches a brand new season's yield."""
    rng = np.random.default_rng(seed)
    hit = 0
    for _ in range(repeats):
        x = rng.uniform(3.0, 9.0, n)
        y = A_TRUE + B_TRUE * x + rng.normal(0.0, SIGMA, n)
        _, lo, hi = prediction_interval(x0, x, y, level)
        new = A_TRUE + B_TRUE * x0 + rng.normal(0.0, SIGMA)
        hit += lo <= new <= hi
    return hit / repeats


def coverage_hetero(x0=8.5, repeats=2000, seed=1):
    """Coverage of the same interval when the noise sd grows with rain: sd = 0.1 * rain - 0.1 (t/ha)."""
    rng = np.random.default_rng(seed)
    hit = 0
    for _ in range(repeats):
        x = rng.uniform(3.0, 9.0, 20)
        y = A_TRUE + B_TRUE * x + rng.normal(0.0, 0.1 * x - 0.1)
        _, lo, hi = prediction_interval(x0, x, y)
        new = A_TRUE + B_TRUE * x0 + rng.normal(0.0, 0.1 * x0 - 0.1)
        hit += lo <= new <= hi
    return hit / repeats


# %% [markdown]
# ## Step 6: extrapolation and the design question
# A line fitted on rain between 100 and 500 mm says nothing reliable about 1000 mm: the interval
# formula assumes the straight line still holds, and the real response levels off. For the design
# question ("how much rain for a target yield?") we invert the line, then check the *lower* end of
# the 95 percent prediction interval, because that is the yield we are nearly sure of.

# %%
def rain_for_target(target, x, y, level=0.95, lo=0.0, hi=15.0):
    """(rain for the fitted line to reach target, rain at which the lower prediction bound reaches target)."""
    a, b = fit_normal(x, y)
    point = (target - a) / b
    grid = np.linspace(lo, hi, 15001)
    low = prediction_interval(grid, x, y, level)[1]
    ok = np.where(low >= target)[0]
    return float(point), float(grid[ok[0]]) if len(ok) else float("nan")


def extrapolation_demo(fit_hi=5.0, x_new=10.0, seed=5):
    """Fit a line to curved data seen only up to rain fit_hi; return (line prediction, true yield) at x_new."""
    xc, yc = make_curved(30, seed, lo=1.0, hi=fit_hi)
    a, b = fit_normal(xc, yc)
    return float(a + b * x_new), float(saturating_yield(x_new))


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    x, y = make_farm(20, 10)
    a, b = fit_normal(x, y)
    print(f"normal equations: a = {a:.3f}, b = {b:.4f}   polyfit: {np.polyfit(x, y, 1)[::-1].round(4)}")
    print(f"R^2 = {r_squared(y, a + b * x):.3f}")
    xc, yc = make_curved(30, 3)
    ac, bc = fit_normal(xc, yc)
    rc = yc - ac - bc * xc
    print(f"curved data: R^2 = {r_squared(yc, ac + bc * xc):.3f}, residual curvature = {residual_curvature(xc, rc):.2f}")
    print(f"straight data: residual curvature = {residual_curvature(x, y - a - b * x):.2f}")
    X2, y2 = make_two_inputs(40, 2)
    beta, se, _ = multi_fit(X2, y2)
    print("two inputs: coefficients", beta.round(3), "standard errors", se.round(3))
    print("t quantile df=18:", round(t_quantile(0.975, 18), 3))
    print("coverage (2000 repeats):", coverage())
    for x0 in (6.0, 9.0, 12.0):
        print(f"prediction at {x0}: ", np.round(prediction_interval(x0, x, y), 2))
    print("extrapolation to 1000 mm (line, truth):", extrapolation_demo())
    print("rain for 3.5 t/ha:", rain_for_target(3.5, x, y))

    fig, axs = plt.subplots(1, 3, figsize=(14, 4))
    grid = np.linspace(2.0, 14.0, 200)
    yh, lo, hi = prediction_interval(grid, x, y)
    axs[0].scatter(x, y, zorder=3, label="seasons")
    axs[0].plot(grid, yh, color="tab:green", label="fitted line")
    axs[0].fill_between(grid, lo, hi, color="tab:green", alpha=0.2, label="95% prediction interval")
    axs[0].plot(grid, A_TRUE + B_TRUE * grid, color="gray", ls=":", label="true line")
    axs[0].axhline(3.5, color="tab:red", ls="--", lw=1)
    axs[0].set_xlabel("rainfall (hundreds of mm)")
    axs[0].set_ylabel("yield (t/ha)")
    axs[0].set_title("Interval widens away from the data")
    axs[0].legend(fontsize=8)
    axs[1].scatter(xc, rc, color="tab:red")
    axs[1].axhline(0, color="gray")
    axs[1].set_xlabel("rainfall (hundreds of mm)")
    axs[1].set_ylabel("residual (t/ha)")
    axs[1].set_title("A curve in the residuals: wrong model")
    axs[2].scatter(x, y - a - b * x, color="tab:blue")
    axs[2].axhline(0, color="gray")
    axs[2].set_xlabel("rainfall (hundreds of mm)")
    axs[2].set_ylabel("residual (t/ha)")
    axs[2].set_title("Random scatter: line is adequate")
    for ax in axs:
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "residuals_and_interval.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
