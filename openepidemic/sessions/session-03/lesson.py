"""Session 3 (Level 3): solve SIR with RK4, fit it to synthetic data, and see chance at work.

TEACHING TOOL ONLY. All data here are synthetic. Not a forecast, not medical advice, and
not a basis for public-health decisions.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulate, fit, and check
# **A. Real-world problem.** Case counts arrive as noisy daily numbers. A modeller wants to
# find the contact rate beta and recovery rate gamma that reproduce them, and then ask
# "what if a share of the town were vaccinated first?". Today you (1) solve the SIR
# equations with your own Runge-Kutta 4 (RK4) code and check it against exact results,
# (2) generate synthetic noisy data from a *known* truth, (3) fit beta and gamma back,
# (4) see why early data cannot separate them, (5) watch small outbreaks die out by chance,
# and (6) test vaccination.
#
# **Important.** These models are teaching tools. They are not forecasts, not medical
# advice, and not a basis for public-health decisions. Every data set here is invented.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# the invented "truth" used to make synthetic data
TRUE_BETA, TRUE_GAMMA, TOWN, SEED_CASES = 0.4, 0.2, 10000, 10


# %% [markdown]
# ## Step 1: your own RK4 solver
# State = (S, I, R). One RK4 step of size h uses four slopes and a weighted average. The
# arrays may hold many (beta, gamma) pairs at once, so one call can run a whole grid.

# %%
def sir_rhs(S, I, R, beta, gamma, N):
    """Slopes dS/dt, dI/dt, dR/dt (people per day)."""
    flow = beta * S * I / N
    return -flow, flow - gamma * I, gamma * I


def rk4_step(state, h, beta, gamma, N):
    S, I, R = state
    k1 = sir_rhs(S, I, R, beta, gamma, N)
    k2 = sir_rhs(S + h / 2 * k1[0], I + h / 2 * k1[1], R + h / 2 * k1[2], beta, gamma, N)
    k3 = sir_rhs(S + h / 2 * k2[0], I + h / 2 * k2[1], R + h / 2 * k2[2], beta, gamma, N)
    k4 = sir_rhs(S + h * k3[0], I + h * k3[1], R + h * k3[2], beta, gamma, N)
    return tuple(x + h / 6 * (a + 2 * b + 2 * c + d) for x, a, b, c, d in zip(state, k1, k2, k3, k4))


def solve_sir(beta, gamma, N=TOWN, I0=SEED_CASES, days=100, R0_init=0.0, h=0.25):
    """Daily values of (S, I, R). Returns an array of shape (days + 1, 3, ...) (extra axes if beta/gamma are arrays)."""
    beta, gamma = np.asarray(beta, float), np.asarray(gamma, float)
    one = np.ones(np.broadcast(beta, gamma).shape)
    state = ((N - I0 - R0_init) * one, I0 * one, R0_init * one)
    out = [np.array(state)]
    steps = int(round(1.0 / h))
    for _ in range(days):
        for _ in range(steps):
            state = rk4_step(state, h, beta, gamma, N)
        out.append(np.array(state))
    return np.array(out)


def final_size(R0, tol=1e-12):
    """Fraction ever infected: solve z = 1 - exp(-R0 z) by bisection (z > 0 only if R0 > 1)."""
    if R0 <= 1.0:
        return 0.0
    lo, hi = 1e-9, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mid - (1 - np.exp(-R0 * mid)) < 0:   # below the nonzero root, 1 - exp(-R0 z) is above z
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


# %% [markdown]
# ## Step 2: validate the solver
# Three trusted references: people are conserved (S + I + R = N), the final size obeys
# z = 1 - exp(-R0 z), and early on I grows like exp(r t) with r = gamma (R0 - 1).

# %%
def growth_rate_measured(beta, gamma, t0=2, t1=12, N=TOWN, I0=SEED_CASES):
    """Slope of ln I between day t0 and t1 (early exponential phase)."""
    Y = solve_sir(beta, gamma, N, I0, days=t1)
    t = np.arange(t0, t1 + 1)
    return float(np.polyfit(t, np.log(Y[t0:t1 + 1, 1]), 1)[0])


def conservation_error(Y, N=TOWN):
    return float(np.abs(Y.sum(axis=1) - N).max())


# %% [markdown]
# ## Step 3: synthetic data with noise
# New infections on day k = S(k) - S(k+1). Real surveillance counts are noisy, so we draw
# each day from a Poisson distribution with that mean (seeded, so everyone gets the same data).

# %%
def daily_incidence(beta, gamma, N=TOWN, I0=SEED_CASES, days=60, R0_init=0.0):
    """Expected new infections on days 0 .. days-1 (shape (days, ...))."""
    S = solve_sir(beta, gamma, N, I0, days, R0_init)[:, 0]
    return S[:-1] - S[1:]


def make_data(seed, days=60, beta=TRUE_BETA, gamma=TRUE_GAMMA, N=TOWN, I0=SEED_CASES, delay=0):
    """Synthetic reported daily cases. `delay` shifts reports later by that many days."""
    rng = np.random.default_rng(seed)
    mean = daily_incidence(beta, gamma, N, I0, days + 100)
    mean = np.concatenate([np.zeros(delay), mean])[:days]
    return rng.poisson(mean).astype(float)


# %% [markdown]
# ## Step 4: fitting by least squares
# Least squares: choose (beta, gamma) that minimise the sum of squared differences between
# the model's daily incidence and the data. Two simple tools, numpy only:
# 1. a grid search over many (beta, gamma) pairs (all solved in one batch), and
# 2. Gauss-Newton, which uses the slope of the model to polish the answer and gives an
#    uncertainty estimate through the matrix (J^T J)^-1.

# %%
BETAS = np.arange(0.10, 1.001, 0.01)
GAMMAS = np.arange(0.05, 0.901, 0.01)


def model_grid(days):
    """Model incidence for every (beta, gamma) on the grid: shape (days, nb, ng)."""
    b, g = np.meshgrid(BETAS, GAMMAS, indexing="ij")
    return daily_incidence(b, g, days=days)


def grid_fit(data, grid=None):
    """Return (beta, gamma) on the grid with the smallest sum of squared errors."""
    grid = model_grid(len(data)) if grid is None else grid
    sse = ((grid - data[:, None, None]) ** 2).sum(axis=0)
    i, j = np.unravel_index(np.argmin(sse), sse.shape)
    return float(BETAS[i]), float(GAMMAS[j])


def _jacobian(th, days):
    f = daily_incidence(th[0], th[1], days=days)
    J = np.empty((days, 2))
    for k in range(2):
        d = np.zeros(2)
        d[k] = 1e-5
        J[:, k] = (daily_incidence(*(th + d), days=days) - f) / 1e-5
    return f, J


def gauss_newton(data, start, iters=30):
    """Polish (beta, gamma) by Gauss-Newton. Returns (theta, covariance 2x2)."""
    days = len(data)
    th = np.array(start, float)
    for _ in range(iters):
        f, J = _jacobian(th, days)
        step = np.linalg.lstsq(J, data - f, rcond=None)[0]
        th = np.clip(th + step, 0.02, 3.0)
        if np.abs(step).max() < 1e-9:
            break
    f, J = _jacobian(th, days)
    s2 = ((data - f) ** 2).sum() / (days - 2)
    return th, s2 * np.linalg.inv(J.T @ J)


def repeat_fits(n_days, n_rep=100, seed0=1000, delay=0):
    """Fit n_rep fresh noisy data sets (first n_days days). Returns array (n_rep, 2) of (beta, gamma)."""
    grid = model_grid(n_days)
    return np.array([grid_fit(make_data(seed0 + k, n_days, delay=delay), grid) for k in range(n_rep)])


# %% [markdown]
# ## Step 5: chance. A stochastic (Gillespie) version
# Instead of smooth curves, simulate one person at a time. Two kinds of event: an infection
# (rate beta S I / N) or a recovery (rate gamma I). The next event time is random and which
# event happens is chosen in proportion to the rates. With ONE starting case, early on the
# outbreak can end by luck before it ever grows.

# %%
def gillespie(beta, gamma, N, I0, rng, tmax=400.0, stop_at=None):
    """One stochastic run. Returns (times, infected_counts). Stops when I = 0, tmax, or I >= stop_at."""
    S, I, t = N - I0, I0, 0.0
    ts, Is = [0.0], [I0]
    while I > 0 and t < tmax:
        if stop_at is not None and I >= stop_at:
            break
        r_inf, r_rec = beta * S * I / N, gamma * I
        total = r_inf + r_rec
        t += rng.exponential(1.0 / total)
        if rng.random() < r_inf / total:
            S, I = S - 1, I + 1
        else:
            I -= 1
        ts.append(t)
        Is.append(I)
    return np.array(ts), np.array(Is)


def extinction_probability(beta, gamma, n_runs=2000, N=TOWN, seed=7, major=100):
    """Fraction of runs (one starting case) that die out before reaching `major` infected."""
    rng = np.random.default_rng(seed)
    dead = 0
    for _ in range(n_runs):
        _, Is = gillespie(beta, gamma, N, 1, rng, stop_at=major)
        dead += int(Is[-1] == 0)
    return dead / n_runs


# %% [markdown]
# ## Step 6: vaccination at the start
# Vaccination before the outbreak moves people from S to R. With coverage v and protection
# efficacy e, a fraction v*e of the town starts protected (R). We measure the peak.

# %%
def peak_with_vaccination(coverage, efficacy=0.9, beta=TRUE_BETA, gamma=TRUE_GAMMA, N=50000, I0=10, days=300):
    """Peak number infected at once, after vaccinating a fraction `coverage` first."""
    protected = coverage * efficacy * N
    Y = solve_sir(beta, gamma, N, I0, days, R0_init=protected)
    return float(Y[:, 1].max())


def min_coverage_for_peak(limit, efficacy=0.9, step=0.01, **kw):
    """Smallest coverage (on a grid of `step`) whose peak is at most `limit`; None if none works."""
    for c in np.arange(0.0, 1.0 + 1e-9, step):
        if peak_with_vaccination(c, efficacy, **kw) <= limit:
            return float(round(c, 10))
    return None


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    R0 = TRUE_BETA / TRUE_GAMMA
    Y = solve_sir(TRUE_BETA, TRUE_GAMMA, days=100)
    print("conservation error:", conservation_error(Y))
    print("peak day, peak:", int(Y[:, 1].argmax()), round(Y[:, 1].max(), 1))
    print("final size model vs formula:", round(Y[-1, 2] / TOWN, 4), round(final_size(R0), 4))
    print("growth rate measured vs gamma(R0-1):", round(growth_rate_measured(TRUE_BETA, TRUE_GAMMA), 4), TRUE_GAMMA * (R0 - 1))

    # Figure 1: model, data, fit after the peak
    data = make_data(3, 60)
    th, cov = gauss_newton(data, grid_fit(data))
    t = np.arange(60)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(t, data, "k.", label="synthetic daily cases (Poisson noise)")
    ax.plot(t, daily_incidence(TRUE_BETA, TRUE_GAMMA, days=60), "g-", label="truth beta=0.40, gamma=0.20")
    ax.plot(t, daily_incidence(th[0], th[1], days=60), "r--", label=f"fit beta={th[0]:.3f}, gamma={th[1]:.3f}")
    ax.set_xlabel("day")
    ax.set_ylabel("new cases per day (people/day)")
    ax.set_title("Fitting SIR to 60 days of synthetic data")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "fit_full.png", dpi=120)
    print("fit on 60 days:", th.round(3), "sd:", np.sqrt(np.diag(cov)).round(3))

    # Figure 2: identifiability - scatter of repeated fits, early vs late data
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharex=True, sharey=True)
    for ax, nd in zip(axes, (14, 60)):
        F = repeat_fits(nd, 100)
        ax.plot(F[:, 0], F[:, 1], "o", ms=4, alpha=0.6)
        ax.plot([TRUE_BETA], [TRUE_GAMMA], "r*", ms=14, label="truth")
        c = np.corrcoef(F.T)[0, 1]
        ax.set_title(f"first {nd} days: sd(beta)={F[:, 0].std():.3f}, corr={c:.2f}")
        ax.set_xlabel("fitted beta (per day)")
        ax.grid(alpha=0.3)
        print(f"{nd} days: mean {F.mean(axis=0).round(3)}, sd {F.std(axis=0).round(3)}, corr {c:.3f}")
    axes[0].set_ylabel("fitted gamma (per day)")
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(OUT / "identifiability.png", dpi=120)

    # Figure 3: stochastic runs
    rng = np.random.default_rng(11)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for _ in range(25):
        ts, Is = gillespie(TRUE_BETA, TRUE_GAMMA, TOWN, 1, rng, tmax=150)
        ax.step(ts, Is, where="post", lw=1, alpha=0.7)
    ax.set_xlabel("day")
    ax.set_ylabel("people infected now")
    ax.set_title("25 stochastic outbreaks from ONE case (R0 = 2)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "stochastic.png", dpi=120)
    print("extinction prob R0=2:", extinction_probability(0.4, 0.2), "R0=3:", extinction_probability(0.6, 0.2))

    # Figure 4: vaccination
    covs = np.linspace(0, 0.9, 19)
    peaks = [peak_with_vaccination(c) for c in covs]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(100 * covs, peaks, "o-")
    ax.axhline(3000, color="r", ls="--", label="hospital line 3000 people")
    ax.set_xlabel("vaccination coverage (percent of town)")
    ax.set_ylabel("peak infected at once (people)")
    ax.set_title("Vaccination lowers the peak (synthetic town, 50000 people)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "vaccination_peak.png", dpi=120)
    print("min coverage for 3000:", min_coverage_for_peak(3000))

# %% [markdown]
# ## Where this stops
# Real outbreaks have age groups, networks, changing behaviour and reporting delays. This
# model has none of them, so it can only teach ideas; it cannot predict a real outbreak.
