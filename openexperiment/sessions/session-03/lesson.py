"""Session 3 (Level 3): designing the experiment, and checking it by simulation.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: designing the experiment, and checking it by simulation
# **A. Real-world problem.** A sensor drifts slowly while you work. If you test all of
# treatment A first and all of treatment B afterwards, the drift looks like a treatment
# effect. Good design (randomise, balance, replicate, vary factors together) protects you
# before any data exist. We test each design on a simulated world where the true answer is
# known, so we can measure bias and scatter of the answer each design gives.
#
# **Plan.** (1) run order under drift, (2) how many replicates, (3) a 2x2 factorial design
# versus one-factor-at-a-time, (4) calibration drift and re-calibration, (5) a failure case,
# (6) a two-factor calibration (the mini-project).

# %%
import math
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# --- part 1: run order under drift ----------------------------------------------------------
N_RUNS = 20          # 10 runs of treatment A (code 0) and 10 of B (code 1)
TRUE_EFFECT = 0.30   # B reads higher than A by this much (degrees C)
DRIFT = 0.05         # sensor drift per run (degrees C per run)
NOISE = 0.50         # random scatter of one run (degrees C)


# %% [markdown]
# ## Step 1: five run orders
# `naive` = all A then all B. `alternating` = ABAB... `abba` = ABBA ABBA... (a drift that is
# a straight line cancels exactly). `random` = shuffle all 20. `blocked` = in every pair of
# neighbouring runs one A and one B, in random order (randomised blocks).

# %%
def make_order(kind, rng):
    """Array of 0 (A) and 1 (B) of length N_RUNS."""
    half = N_RUNS // 2
    if kind == "naive":
        return np.array([0] * half + [1] * half)
    if kind == "alternating":
        return np.array([0, 1] * half)
    if kind == "abba":
        return np.array([0, 1, 1, 0] * (N_RUNS // 4))
    if kind == "random":
        return rng.permutation(np.array([0] * half + [1] * half))
    if kind == "blocked":
        pairs = [rng.permutation([0, 1]) for _ in range(half)]
        return np.concatenate(pairs)
    raise ValueError(kind)


def effect_estimate(order, rng, drift=DRIFT, effect=TRUE_EFFECT, noise=NOISE):
    """Run the experiment once: mean(B) - mean(A) in the drifting world."""
    t = np.arange(N_RUNS)
    y = effect * order + drift * t + rng.normal(0.0, noise, N_RUNS)
    return float(y[order == 1].mean() - y[order == 0].mean())


def order_study(kind, reps, seed, drift=DRIFT):
    """(bias, scatter) of the effect estimate over many repeats of the whole experiment."""
    rng = np.random.default_rng(seed)
    est = np.array([effect_estimate(make_order(kind, rng), rng, drift=drift) for _ in range(reps)])
    return float(est.mean() - TRUE_EFFECT), float(est.std(ddof=1))


def drift_bias(order, drift=DRIFT):
    """Exact bias a straight-line drift adds to mean(B) - mean(A): drift * (mean time of B - mean time of A)."""
    t = np.arange(len(order))
    return float(drift * (t[order == 1].mean() - t[order == 0].mean()))


# %% [markdown]
# ## Step 2: replication and power
# To detect a true difference d between two group means (each run has scatter sigma), with
# n runs per group, a two-sided z-test at 5 percent significance with power 80 percent needs
#
#     n = 2 (z_a + z_b)^2 sigma^2 / d^2,   z_a = 1.96 (5 percent two-sided), z_b = 0.8416 (80 percent power).
#
# *Power* is the chance the test finds the difference when it is real. We check the formula
# with a seeded Monte Carlo simulation (known sigma, so a z-test).

# %%
ZA = 1.959964
ZB = 0.841621


def sample_size(d, sigma, za=ZA, zb=ZB):
    return int(math.ceil(2.0 * (za + zb) ** 2 * sigma ** 2 / d ** 2 - 1e-12))


def phi(z):
    """Standard normal cumulative distribution."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def power_formula(n, d, sigma, za=ZA):
    shift = d / (sigma * math.sqrt(2.0 / n))
    return phi(shift - za) + phi(-shift - za)


def simulate_power(n, d, sigma, reps, seed, za=ZA):
    rng = np.random.default_rng(seed)
    a = rng.normal(0.0, sigma, (reps, n)).mean(axis=1)
    b = rng.normal(d, sigma, (reps, n)).mean(axis=1)
    z = (b - a) / (sigma * math.sqrt(2.0 / n))
    return float(np.mean(np.abs(z) > za))


# %% [markdown]
# ## Step 3: 2x2 factorial design versus one factor at a time
# Two factors A and B, each at a low (-1) and high (+1) setting, give four runs:
# (-,-), (+,-), (-,+), (+,+). The main effect of A is mean(response at A high) minus
# mean(response at A low); the interaction AB is half the difference between the effect of
# A when B is high and the effect of A when B is low. The made-up system below has
# response = 50 + A + B + 6 A B: the two factors only help when changed together.

# %%
def system(a, b):
    """Noise-free response of the made-up system (a, b are -1 or +1)."""
    return 50.0 + a + b + 6.0 * a * b


RUNS = [(-1, -1), (1, -1), (-1, 1), (1, 1)]


def factorial_effects(y):
    """y = responses of the four runs in the order of RUNS. Returns (A, B, AB) effects."""
    y1, y2, y3, y4 = y
    ea = ((y2 + y4) - (y1 + y3)) / 2.0
    eb = ((y3 + y4) - (y1 + y2)) / 2.0
    eab = ((y1 + y4) - (y2 + y3)) / 2.0
    return ea, eb, eab


def one_factor_at_a_time(f=system):
    """Start at (-1,-1); change A and keep the better; then change B and keep the better.
    Returns (a, b, response) of the setting it ends at."""
    a, b = -1, -1
    if f(1, b) > f(a, b):
        a = 1
    if f(a, 1) > f(a, b):
        b = 1
    return a, b, f(a, b)


# %% [markdown]
# ## Step 4: calibration drift and the re-calibration schedule
# Right after calibration the offset error is random with sd U_CAL; then it drifts at RATE
# degrees per day. We want the error to stay within TOL. Using 1.96 * U_CAL as the worst
# starting error, we must re-calibrate before 1.96 * U_CAL + RATE * t reaches TOL.

# %%
U_CAL = 0.10   # standard uncertainty of the offset right after calibration (degrees C)
RATE = 0.02    # drift (degrees C per day)
TOL = 0.50     # allowed error (degrees C)


def recal_days(tol=TOL, u_cal=U_CAL, rate=RATE, z=ZA):
    """Largest whole number of days t with z * u_cal + rate * t <= tol."""
    return max(0, int(math.floor((tol - z * u_cal) / rate + 1e-9)))


def p_exceed(t, tol=TOL, u_cal=U_CAL, rate=RATE):
    """Chance the error is above +tol after t days (upper tail only)."""
    return 1.0 - phi((tol - rate * t) / u_cal)


def simulate_exceed(t, reps, seed, tol=TOL, u_cal=U_CAL, rate=RATE):
    rng = np.random.default_rng(seed)
    return float(np.mean(rng.normal(0.0, u_cal, reps) + rate * t > tol))


# %% [markdown]
# ## Step 5: a failure case - extrapolating a nonlinear sensor
# The made-up sensor below bends: reading = T + 0.002 T^2 (degrees C). Calibrated with a
# straight line on 0..50 degrees it looks fine inside that range, but outside it the line
# is badly wrong. The residuals show a systematic curve - the warning sign.

# %%
def curved(T):
    T = np.asarray(T, dtype=float)
    return T + 0.002 * T ** 2


def extrapolation_demo(lo=0.0, hi=50.0, n=11):
    """Fit a line on [lo, hi]; returns (slope, intercept, max |residual| inside, error at 100)."""
    x = np.linspace(lo, hi, n)
    y = curved(x)
    m, c = np.polyfit(x, y, 1)
    inside = float(np.max(np.abs(y - (m * x + c))))
    err100 = float(curved(100.0) - (m * 100.0 + c))
    return float(m), float(c), inside, err100


# %% [markdown]
# ## Step 6: mini-project - calibrate across temperature and supply voltage
# The made-up sensor also depends on its supply voltage V (volts) around 5 V:
#
#     reading = 0.98 T + 0.5 + (V - 5) (0.8 + 0.004 T) + drift + noise
#
# We run a 2x2 factorial: T in {20, 80} degrees C and V in {4.5, 5.5} V, 5 replicates per
# corner (20 runs), in randomised blocks (every block of 4 runs has each corner once). We
# estimate the effects, then fit reading = b0 + b1 T + b2 dV + b3 T dV (dV = V - 5) by
# least squares and invert it for T when V is known.

# %%
TS = (20.0, 80.0)
VS = (4.5, 5.5)
SENSOR_NOISE = 0.30
RUN_DRIFT = 0.01   # sensor drift per run (degrees C per run)


def reading2(T, V, run=0, rng=None, noise=SENSOR_NOISE):
    r = 0.98 * T + 0.5 + (V - 5.0) * (0.8 + 0.004 * T) + RUN_DRIFT * run
    if rng is not None:
        r = r + rng.normal(0.0, noise, np.shape(r))
    return r


def design_runs(reps, rng):
    """Randomised blocks: list of (T, V) for 4*reps runs."""
    corners = [(t, v) for t in TS for v in VS]
    runs = []
    for _ in range(reps):
        for k in rng.permutation(4):
            runs.append(corners[k])
    return runs


def run_experiment(reps, seed):
    rng = np.random.default_rng(seed)
    runs = design_runs(reps, rng)
    T = np.array([r[0] for r in runs])
    V = np.array([r[1] for r in runs])
    y = reading2(T, V, np.arange(len(runs)), rng)
    return T, V, y


def two_factor_effects(T, V, y):
    """Main effects of T and V and their interaction (standard 2x2 definitions), from corner means."""
    def mean_at(t, v):
        return float(y[(T == t) & (V == v)].mean())
    y1, y2, y3, y4 = (mean_at(TS[0], VS[0]), mean_at(TS[1], VS[0]), mean_at(TS[0], VS[1]), mean_at(TS[1], VS[1]))
    return factorial_effects((y1, y2, y3, y4))


def fit_two_factor(T, V, y):
    """Least squares for [b0, b1, b2, b3] in reading = b0 + b1 T + b2 dV + b3 T dV; and residual sd."""
    dV = V - 5.0
    X = np.column_stack([np.ones_like(T), T, dV, T * dV])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ b
    s = math.sqrt(float(resid @ resid) / (len(y) - 4))
    return b, s


def estimate_T(b, reading, V):
    dV = V - 5.0
    return (reading - b[0] - b[2] * dV) / (b[1] + b[3] * dV)


def mini_project_stats(reps, trials, seed, T_test=50.0, V_test=5.4):
    """Over many repeats of the whole experiment: (sd of T error with V-aware calibration,
    bias of T if V is ignored). A single new reading at (T_test, V_test) is inverted."""
    rng = np.random.default_rng(seed)
    errs = []
    for _ in range(trials):
        T, V, y = run_experiment(reps, int(rng.integers(1 << 30)))
        b, _s = fit_two_factor(T, V, y)
        ynew = float(reading2(T_test, V_test, 25, rng))
        errs.append(estimate_T(b, ynew, V_test) - T_test)
    errs = np.array(errs)
    # calibration that ignores V: line through all runs, evaluated for the same reading
    T, V, y = run_experiment(reps, seed)
    m, c = np.polyfit(T, y, 1)
    naive_err = (float(reading2(T_test, V_test, 25)) - c) / m - T_test
    return float(errs.std(ddof=1)), float(naive_err)


# %% [markdown]
# ## Step 7: see it
# Four figures: run orders under drift, power against n, the 2x2 interaction plot, and the
# extrapolation failure.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    kinds = ["naive", "alternating", "abba", "random", "blocked"]
    bias, sd = [], []
    for k in kinds:
        b_, s_ = order_study(k, 4000, 3)
        bias.append(b_)
        sd.append(s_)
        print("%-12s bias %+.3f  scatter %.3f" % (k, b_, s_))
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.6))
    axs[0].bar(kinds, bias)
    axs[0].axhline(0, color="k", lw=0.8)
    axs[0].set_ylabel("bias of effect estimate (degrees C)")
    axs[0].set_title("Bias caused by drift")
    axs[1].bar(kinds, sd, color="tab:orange")
    axs[1].set_ylabel("scatter of effect estimate (degrees C)")
    axs[1].set_title("Scatter of the estimate")
    for a in axs:
        a.tick_params(axis="x", labelrotation=30)
        a.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(OUT / "run_orders.png", dpi=120)

    print("sample size d=0.5, sigma=1:", sample_size(0.5, 1.0),
          "power", round(power_formula(63, 0.5, 1.0), 3), "sim", round(simulate_power(63, 0.5, 1.0, 20000, 1), 3))
    ns = np.arange(2, 120)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(ns, [power_formula(int(n), 0.5, 1.0) for n in ns], label="formula")
    ax2.plot(ns[::8], [simulate_power(int(n), 0.5, 1.0, 5000, 2) for n in ns[::8]], "o", label="simulation")
    ax2.axhline(0.8, color="gray", ls=":")
    ax2.axvline(63, color="gray", ls=":")
    ax2.set_xlabel("runs per group, n")
    ax2.set_ylabel("power (chance to detect d = 0.5, sigma = 1)")
    ax2.set_title("Power against replication")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "power_vs_n.png", dpi=120)

    fig3, ax3 = plt.subplots(figsize=(5.5, 4))
    for bv, st in ((-1, "--"), (1, "-")):
        ax3.plot([-1, 1], [system(-1, bv), system(1, bv)], st, marker="o", label="B = %+d" % bv)
    ax3.set_xlabel("factor A (coded level)")
    ax3.set_ylabel("response")
    ax3.set_title("Interaction: lines are not parallel")
    ax3.legend()
    ax3.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "interaction.png", dpi=120)
    print("factorial effects:", factorial_effects([system(a, b) for a, b in RUNS]), "OFAT ends at", one_factor_at_a_time())

    m, c, inside, err100 = extrapolation_demo()
    xs = np.linspace(0, 100, 101)
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    ax4.plot(xs, curved(xs), label="real (curved) sensor")
    ax4.plot(xs, m * xs + c, "--", label="line fitted on 0..50")
    ax4.axvspan(0, 50, color="green", alpha=0.1, label="calibrated range")
    ax4.set_xlabel("true temperature (degrees C)")
    ax4.set_ylabel("sensor reading (degrees C)")
    ax4.set_title("Extrapolation error at 100 degrees C: %.1f" % err100)
    ax4.legend(fontsize=8)
    ax4.grid(alpha=0.3)
    fig4.tight_layout()
    fig4.savefig(OUT / "extrapolation.png", dpi=120)
    print("recal every", recal_days(), "days; P(exceed) at 15 days:", round(p_exceed(15), 4))
    T_, V_, y_ = run_experiment(5, 1)
    print("effects (T, V, TV):", np.round(two_factor_effects(T_, V_, y_), 3))
    print("calibration fit b, s:", fit_two_factor(T_, V_, y_))
    print("mini-project:", mini_project_stats(5, 400, 7))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
