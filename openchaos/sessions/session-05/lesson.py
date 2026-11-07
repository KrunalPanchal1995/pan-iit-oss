"""Session 5 (Level 3): ensemble forecasts, with probabilities instead of a single path.

Run:  python start.py 5
"""
# %% [markdown]
# # Session 5: ensemble forecasts
# **A. Real-world problem.** In Session 3 we forecast the double pendulum from one start with one
# assumed error, and found the forecast fails after a horizon. Weather services do something
# different: they run *a cloud* of forecasts from slightly different starts and report what
# fraction of them do something ("70 percent of the runs bring rain"). Today we start 1000 runs
# of the pendulum from a Gaussian cloud of start errors (1e-6 rad), measure how fast the cloud
# spreads, and turn the cloud into a probability that the outer rod has flipped. We also ask how
# much that probability can be trusted: it has a sampling error (too few members) and a numerical
# error (too coarse a time step), and the second one is the sneaky one.
#
# Equal balls (1 kg), equal 1 m rods, no friction, released from rest with both rods at the same
# angle. The cloud perturbs only the two start angles.

# %%
import math
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81                 # gravity, m/s^2


# %% [markdown]
# ## Step 1: the equations and RK4, for one start or a thousand at once
# These are the Session 3 functions. Every operation works on single numbers or on NumPy arrays,
# so one call of `rk4_step` advances the whole cloud: the four state variables are arrays with one
# entry per member.

# %%
def rate(state):
    """(theta1', theta2', omega1', omega2') for state (theta1, theta2, omega1, omega2); numbers or arrays."""
    t1, t2, w1, w2 = state
    m = np if isinstance(t1, np.ndarray) else math
    d = t1 - t2
    den = 3.0 - m.cos(2 * d)
    a1 = (-3 * G * m.sin(t1) - G * m.sin(t1 - 2 * t2) - 2 * m.sin(d) * (w2 ** 2 + w1 ** 2 * m.cos(d))) / den
    a2 = (2 * m.sin(d) * (2 * w1 ** 2 + 2 * G * m.cos(t1) + w2 ** 2 * m.cos(d))) / den
    return (w1, w2, a1, a2)


def rk4_step(state, h):
    """Runge-Kutta 4: four slopes per step, error per unit time about h^4."""
    def shift(s, k, f):
        return tuple(a + f * b for a, b in zip(s, k))
    k1 = rate(state)
    k2 = rate(shift(state, k1, h / 2))
    k3 = rate(shift(state, k2, h / 2))
    k4 = rate(shift(state, k3, h))
    return tuple(a + h / 6 * (b + 2 * c + 2 * d + e) for a, b, c, d, e in zip(state, k1, k2, k3, k4))


def release(a_deg):
    a = math.radians(a_deg)
    return (a, a, 0.0, 0.0)


# %% [markdown]
# ## Step 2: the cloud of forecasts
# Each member starts from the release angles plus a random error with a Gaussian distribution of
# standard deviation `sigma` (1e-6 rad), drawn independently for the two angles. The generator is
# seeded, so a run can be repeated exactly. We follow all members with the same RK4 step, store the
# outer-rod angle theta2 every `every` seconds, and note for each member the first time the outer rod
# goes over the top (|theta2| above pi): its **flip time** (infinity if it never flips).

# %%
def run_ensemble(a_deg, n=1000, sigma=1e-6, duration=25.0, h=0.005, seed=1, every=0.05):
    """Run n members. Returns a dict: t (sample times), theta2 (samples x n) and flip (n flip times, inf if none)."""
    rng = np.random.default_rng(seed)
    t1, t2, w1, w2 = release(a_deg)
    s = (t1 + sigma * rng.standard_normal(n), t2 + sigma * rng.standard_normal(n), np.full(n, w1), np.full(n, w2))
    steps = int(round(duration / h))
    k = max(1, int(round(every / h)))
    times, samples = [0.0], [s[1].copy()]
    flip = np.full(n, np.inf)
    for i in range(1, steps + 1):
        s = rk4_step(s, h)
        newly = (np.abs(s[1]) > math.pi) & np.isinf(flip)
        flip[newly] = i * h
        if i % k == 0:
            times.append(i * h)
            samples.append(s[1].copy())
    return {"t": np.array(times), "theta2": np.array(samples), "flip": flip, "n": n, "sigma": sigma, "h": h, "a_deg": a_deg}


# %% [markdown]
# ## Step 3: the spread of the cloud
# The **spread** at time t is the standard deviation of theta2 over the members. At first it equals
# sigma (1e-6 rad). While it is small it grows like sigma exp(lambda t), the same exponential
# growth as in Session 3, so ln(spread) is a straight line whose slope estimates lambda. We call the
# first time the spread exceeds 0.5 rad the **spread time**: after it the members disagree about
# where the outer rod is by more than half a radian, and the forecast of the path is worthless.

# %%
def spread_curve(ens):
    """Standard deviation of theta2 over the members at each sample time (rad)."""
    return ens["theta2"].std(axis=1)


def first_time_above(t, y, limit):
    """First time at which y exceeds limit, or None."""
    idx = np.flatnonzero(np.asarray(y) > limit)
    return float(t[idx[0]]) if idx.size else None


def growth_rate_from_spread(t, spread, lo=1e-5, hi=1e-2):
    """Slope of ln(spread) against t over the samples where lo < spread < hi (units 1/s)."""
    m = (spread > lo) & (spread < hi)
    if m.sum() < 5:
        raise ValueError("too few samples in the exponential window")
    return float(np.polyfit(t[m], np.log(spread[m]), 1)[0])


# %% [markdown]
# ## Step 4: from a cloud to a probability
# The **flip probability** P(t) is the fraction of members that have flipped by time t. With N members
# it is an estimate with a **sampling error** (standard error) sqrt(P (1 - P) / N): about 0.014 at
# P = 0.77 and N = 1000. To halve that error you need four times as many members. To read a
# probability with a given error, `members_needed` inverts the formula.

# %%
def flip_probability(flip, t):
    """Fraction of members whose flip time is at most t."""
    return float(np.mean(np.asarray(flip) <= t))


def flip_probability_curve(ens):
    """P(t) at each sample time."""
    f = np.sort(ens["flip"])
    return np.searchsorted(f, ens["t"], side="right") / len(f)


def standard_error(p, n):
    return math.sqrt(p * (1.0 - p) / n)


def members_needed(p, se):
    """Smallest number of members for which the standard error of a probability near p is at most se."""
    return int(math.ceil(p * (1.0 - p) / se ** 2))


# %% [markdown]
# ## Step 5: is the answer converged?
# A forecast has two numerical knobs. A different random seed changes the members (sampling error).
# A different time step changes the *physics each member sees*: RK4's own error is a tiny extra
# start error, and the chaos amplifies it exactly like the 1e-6 we put in on purpose. So we repeat
# the ensemble with different seeds and with a halved step until the probability stops moving.

# %%
def seed_repeat(a_deg, seeds, **kw):
    """List of (seed, spread time, flip probability by 20 s) for several seeds."""
    out = []
    for sd in seeds:
        e = run_ensemble(a_deg, seed=sd, **kw)
        out.append((sd, first_time_above(e["t"], spread_curve(e), 0.5), flip_probability(e["flip"], 20.0)))
    return out


def step_convergence(a_deg, steps, **kw):
    """List of (h, spread time, flip probability by 20 s) for several time steps (same seed)."""
    out = []
    for hh in steps:
        e = run_ensemble(a_deg, h=hh, **kw)
        out.append((hh, first_time_above(e["t"], spread_curve(e), 0.5), flip_probability(e["flip"], 20.0)))
    return out


def deterministic_flip_time(a_deg, h=0.0025, duration=40.0):
    """First flip time of the single exact start (no cloud), or None."""
    s = release(a_deg)
    for i in range(1, int(round(duration / h)) + 1):
        s = rk4_step(s, h)
        if abs(s[1]) > math.pi:
            return i * h
    return None


# %% [markdown]
# ## Step 6: how good must the instrument be?
# Session 3 said the horizon grows only like the logarithm of the precision. The cloud shows the same
# thing: making the start error a hundred times smaller delays the spread time by about
# ln(100) / lambda, a few seconds, not a factor of a hundred. `precision_ladder` runs one ensemble
# per sigma and reports the spread time, the flip probability by 20 s and its standard error.

# %%
def precision_ladder(a_deg, sigmas, duration=30.0, **kw):
    """List of (sigma, spread time, P(flip by 20 s), standard error) for each start-error size."""
    out = []
    for sg in sigmas:
        e = run_ensemble(a_deg, sigma=sg, duration=duration, **kw)
        p = flip_probability(e["flip"], 20.0)
        out.append((sg, first_time_above(e["t"], spread_curve(e), 0.5), p, standard_error(p, e["n"])))
    return out


# %% [markdown]
# ## See it
# Figure 1: 40 of the 1000 members for the 120 degree release, with the cloud mean and its spread.
# Figure 2: spread against time on a log axis for two releases. Figure 3: the flip probability for
# the 95 degree release at three time steps. Figure 4: spread time and flip probability against the
# size of the start error.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib.ticker import NullFormatter

    OUT.mkdir(exist_ok=True)
    BLUE, ORANGE, MAGENTA, GREY = "#0072b2", "#c86a00", "#d81b60", "#555555"
    e120 = run_ensemble(120.0)
    e95 = run_ensemble(95.0)
    for name, e in (("120", e120), ("95", e95)):
        sp = spread_curve(e)
        print(f"release {name}: spread time {first_time_above(e['t'], sp, 0.5)} s, lambda from the spread {growth_rate_from_spread(e['t'], sp):.2f} /s, "
              f"flip probability by 10/15/20/25 s: {[round(flip_probability(e['flip'], x), 3) for x in (10, 15, 20, 25)]}, "
              f"sampling error at 20 s: {standard_error(flip_probability(e['flip'], 20.0), 1000):.3f}")
    print("deterministic (no cloud) first flip: 120 deg", deterministic_flip_time(120.0), "s;  95 deg", deterministic_flip_time(95.0), "s")
    print("members needed for a standard error of 0.01 at p = 0.77:", members_needed(0.77, 0.01))

    # Figure 1: the cloud
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    t = e120["t"]
    for j in range(40):
        ax1.plot(t, e120["theta2"][:, j], color=GREY, lw=0.6, alpha=0.5)
    mu, sd = e120["theta2"].mean(axis=1), e120["theta2"].std(axis=1)
    ax1.plot(t, mu, color=BLUE, lw=2.2, label="cloud mean")
    ax1.fill_between(t, mu - sd, mu + sd, color=BLUE, alpha=0.25, label="mean +/- spread")
    ax1.axhline(math.pi, color=MAGENTA, ls="--", lw=1.2)
    ax1.axhline(-math.pi, color=MAGENTA, ls="--", lw=1.2, label="outer rod over the top")
    st = first_time_above(t, spread_curve(e120), 0.5)
    ax1.axvline(st, color=ORANGE, ls=":", lw=2, label=f"spread reaches 0.5 rad at {st:.1f} s")
    ax1.set_xlabel("time (s)")
    ax1.set_ylabel("outer rod angle theta2 (rad)")
    ax1.set_title("1000 forecasts from a 1e-6 rad cloud (40 shown), 120 degree release")
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=8, loc="lower left")
    fig1.tight_layout()
    fig1.savefig(OUT / "ensemble_cloud.png", dpi=120)

    # Figure 2: spread against time
    fig2, ax2 = plt.subplots(figsize=(7.5, 4.2))
    for e, name, col, ls in ((e120, "120 degrees", BLUE, "-"), (e95, "95 degrees", ORANGE, "--")):
        ax2.semilogy(e["t"][1:], spread_curve(e)[1:], color=col, ls=ls, lw=2, label=name)
    ax2.axhline(0.5, color=MAGENTA, ls=":", lw=1.5, label="0.5 rad")
    ax2.axhline(1e-6, color=GREY, ls=":", lw=1.2, label="start error 1e-6 rad")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("spread of theta2 over the members (rad)")
    ax2.set_title("The spread grows exponentially, then saturates")
    ax2.grid(alpha=0.3, which="both")
    ax2.xaxis.set_minor_formatter(NullFormatter())
    ax2.legend(fontsize=8, loc="lower right")
    fig2.tight_layout()
    fig2.savefig(OUT / "spread_vs_time.png", dpi=120)

    # Figure 3: flip probability and the time step
    conv = {}
    fig3, ax3 = plt.subplots(figsize=(7.5, 4.2))
    for hh, col, ls in ((0.01, MAGENTA, ":"), (0.005, ORANGE, "--"), (0.0025, BLUE, "-")):
        e = run_ensemble(95.0, h=hh, duration=25.0)
        conv[hh] = e
        p = flip_probability_curve(e)
        ax3.plot(e["t"], p, color=col, ls=ls, lw=2, label=f"h = {hh} s")
        print(f"  h = {hh}: P(flip by 20 s) = {flip_probability(e['flip'], 20.0):.3f}, spread time {first_time_above(e['t'], spread_curve(e), 0.5)} s")
    p20 = flip_probability(conv[0.0025]["flip"], 20.0)
    ax3.axhline(p20, color=GREY, lw=0.8)
    ax3.axvline(20, color=GREY, lw=0.8)
    ax3.fill_between([0, 25], p20 - 2 * standard_error(p20, 1000), p20 + 2 * standard_error(p20, 1000), color=GREY, alpha=0.2, label="+/- 2 standard errors (N = 1000)")
    ax3.set_xlabel("time (s)")
    ax3.set_ylabel("probability the outer rod has flipped")
    ax3.set_title("95 degree release: the answer moves when the time step changes")
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8, loc="upper left")
    fig3.tight_layout()
    fig3.savefig(OUT / "flip_probability.png", dpi=120)

    # Figure 4: instrument precision
    sig = [1e-10, 1e-8, 1e-6, 1e-4, 1e-2]
    lad = {a: precision_ladder(a, sig, duration=40.0) for a in (95.0, 120.0)}
    for a, rows in lad.items():
        print(f"release {a:g}: (sigma, spread time, P20, standard error)", [(s, None if st is None else round(st, 2), round(p, 3), round(se, 3)) for s, st, p, se in rows])
    fig4, axs4 = plt.subplots(1, 2, figsize=(9.6, 4.0))
    for a, col, mk in ((95.0, ORANGE, "o--"), (120.0, BLUE, "s-")):
        rows = [r for r in lad[a] if r[1] is not None]
        axs4[0].semilogx([r[0] for r in rows], [r[1] for r in rows], mk, color=col, label=f"{a:g} degrees")
    axs4[0].set_xlabel("start error sigma (rad)")
    axs4[0].set_ylabel("time the spread reaches 0.5 rad (s)")
    axs4[0].set_title("A 100 times better instrument buys a few seconds", fontsize=10)
    axs4[0].legend(fontsize=8)
    axs4[0].grid(alpha=0.3)
    rows = lad[95.0]
    axs4[1].errorbar([r[0] for r in rows], [r[2] for r in rows], yerr=[2 * r[3] for r in rows], fmt="o--", color=ORANGE, capsize=3, label="95 degrees (bars: 2 standard errors)")
    axs4[1].set_xscale("log")
    for a_ in axs4:
        a_.set_xticks([1e-10, 1e-8, 1e-6, 1e-4, 1e-2])
        a_.xaxis.set_minor_formatter(NullFormatter())
    axs4[1].axhline(1.0, color=GREY, lw=0.8)
    axs4[1].set_xlabel("start error sigma (rad)")
    axs4[1].set_ylabel("probability of a flip by 20 s")
    axs4[1].set_title("The probability depends on the start error", fontsize=10)
    axs4[1].legend(fontsize=8, loc="lower right")
    axs4[1].grid(alpha=0.3)
    fig4.tight_layout()
    fig4.savefig(OUT / "precision.png", dpi=120)
    print("seed repeat 120:", seed_repeat(120.0, [1, 2]))
    print("seed repeat 95:", seed_repeat(95.0, [1, 2, 3, 4]))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
