"""Session 3 (Level 3): a dynamic model of body mass, validated, with uncertainty.

General education only. Not medical or dietary advice. The people are made up. This is a
simplified model, not a clinical tool: real bodies also change composition and metabolism.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: mass changes, and expenditure changes with it
# **A. Real-world problem.** The 7700 kcal-per-kg rule treats energy use as fixed. But a
# heavier body uses more energy, so a constant surplus raises mass more and more slowly: mass
# approaches a new steady state. We simulate this, check it against a closed-form answer,
# compare it with the naive rule, and measure how much uncertain inputs blur the result.
# (General education only, not medical or dietary advice.)

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

RHO = 7700.0   # kcal per kg, rough short-term rule


# %% [markdown]
# ## Step 1: expenditure that depends on mass
# With Mifflin-St Jeor, E(M) = PAL x (10 M + 6.25 h - 5 a + s). That is a straight line
# E = A M + B (A in kcal/day per kg, B in kcal/day). Extra activity per kg of body mass (for
# example walking) simply adds to A.

# %%
def exp_params(pal, height_cm, age, sex, extra_per_kg=0.0, scale=1.0):
    """Returns (A, B) so that expenditure E(M) = A*M + B (kcal/day).

    scale multiplies the BMR (used for uncertainty: 1.1 means BMR is 10 percent higher)."""
    s = 5.0 if sex == "male" else -161.0
    A = scale * pal * 10.0 + extra_per_kg
    B = scale * pal * (6.25 * height_cm - 5.0 * age + s)
    return A, B


ASHA = dict(m0=60.0, height_cm=165.0, age=20, sex="female", pal=1.55)   # made up


# %% [markdown]
# ## Step 2: the model and its exact answer
# dM/dt = (I - E(M)) / RHO = (I - A M - B) / RHO. This is a linear equation. Its solution is
#
#     M(t) = M_ss + (M0 - M_ss) exp(-t / tau),   M_ss = (I - B) / A,   tau = RHO / A
#
# so mass moves toward M_ss and the speed is proportional to the distance left. We solve it
# numerically (Euler, step dt days) and compare with this formula.

# %%
def steady_state(intake, A, B):
    return (intake - B) / A


def time_constant(A):
    """tau in days."""
    return RHO / A


def exact_mass(m0, intake, A, B, t_days):
    mss = steady_state(intake, A, B)
    return mss + (m0 - mss) * np.exp(-np.asarray(t_days, dtype=float) * A / RHO)


def simulate(m0, intake, A, B, days, dt=1.0):
    """Euler solution. Returns (t, M) with t in days from 0 to days."""
    n = int(round(days / dt))
    t = np.arange(n + 1) * dt
    m = np.empty(n + 1)
    m[0] = m0
    for i in range(n):
        m[i + 1] = m[i] + dt * (intake - (A * m[i] + B)) / RHO
    return t, m


def naive_mass(m0, intake, A, B, t_days):
    """The 7700 rule: expenditure frozen at its starting value."""
    e0 = A * m0 + B
    return m0 + (intake - e0) * np.asarray(t_days, dtype=float) / RHO


# %% [markdown]
# ## Step 3: uncertainty by Monte Carlo
# Suppose Asha logs her food and plans to eat exactly what her estimate says she uses, so the
# prediction is "no change". But logging can be off by up to 10 percent, and the BMR estimate
# can be off by up to 10 percent. We draw both errors at random (uniform), run the exact solution
# for each draw and look at the spread of the 12-week mass change.

# %%
def monte_carlo(m0, logged_intake, A_nom, B_nom, days, n=5000, intake_err=0.10, bmr_err=0.10, seed=2024):
    """Mass change (kg) after `days` for n random error draws. Returns an array of length n."""
    rng = np.random.default_rng(seed)
    ui = rng.uniform(-intake_err, intake_err, n)
    ub = rng.uniform(-bmr_err, bmr_err, n)
    A = A_nom * (1.0 + ub)
    B = B_nom * (1.0 + ub)
    true_intake = logged_intake * (1.0 + ui)
    return exact_mass(m0, true_intake, A, B, days) - m0


# %% [markdown]
# ## Step 4: a failure case
# Two common logging errors: (a) trusting a label that is rounded (here to the nearest 10 kcal,
# so each label is off by at most 5), and (b) underestimating portions. Compare their size.

# %%
def rounding_worst_case(labels_per_day, step=10.0):
    """Largest possible daily error (kcal) from rounding each label to the nearest `step`."""
    return labels_per_day * step / 2.0


def portion_error(logged_intake, underestimate):
    """True intake if portions were underestimated by this fraction (0.2 = logged 20 percent too low)."""
    return logged_intake / (1.0 - underestimate)


# %% [markdown]
# ## Step 5: a mini-project helper for a made-up planner
# Net energy of walking above resting: (MET - 1) x mass x hours, with MET = 3.5 for walking
# (approximate textbook value). Per kg of mass it is 2.5 x hours.

# %%
WALK_NET_MET = 2.5   # (3.5 - 1)


def plan_balance(intake, walk_hours, m0=60.0, pal=1.2, height_cm=165.0, age=20, sex="female"):
    """Daily balance (kcal) at the start for a meal-and-walk plan, sedentary base plus walking."""
    A, B = exp_params(pal, height_cm, age, sex, extra_per_kg=WALK_NET_MET * walk_hours)
    return intake - (A * m0 + B)


def find_plans(meals=(1400.0, 1500.0, 1600.0, 1700.0), walks=(0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5), lo=-225.0, hi=-175.0):
    """All (meal kcal, walk hours) pairs whose starting daily balance lies in [lo, hi]."""
    return [(m, w) for m in meals for w in walks if lo <= plan_balance(m, w) <= hi]


def plan_outcome(intake, walk_hours, days=84, m0=60.0):
    """Dynamic-model mass change (kg) over `days` for the plan (sedentary base plus walking)."""
    A, B = exp_params(1.2, 165.0, 20, "female", extra_per_kg=WALK_NET_MET * walk_hours)
    return float(exact_mass(m0, intake, A, B, days) - m0)


def plan_spread(intake, walk_hours, days=84, m0=60.0, n=5000, seed=2024):
    """5th and 95th percentile of the mass change when the logged intake and BMR are each off by up to 10 percent."""
    A, B = exp_params(1.2, 165.0, 20, "female", extra_per_kg=WALK_NET_MET * walk_hours)
    d = monte_carlo(m0, intake, A, B, days, n=n, seed=seed)
    return tuple(np.percentile(d, [5, 95]))


# %% [markdown]
# ## Step 6: see it
# Left: dynamic model against the naive line, with the exact solution. Right: spread of the
# 12-week result from the Monte Carlo draws.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    A, B = exp_params(ASHA["pal"], ASHA["height_cm"], ASHA["age"], ASHA["sex"])
    E0 = A * ASHA["m0"] + B
    I = 2400.0
    print(f"A = {A:.2f} kcal/day per kg, B = {B:.2f}, E0 = {E0:.1f}, tau = {time_constant(A):.0f} days")
    print(f"steady state at {I:.0f} kcal/day: {steady_state(I, A, B):.2f} kg")
    t, m = simulate(ASHA["m0"], I, A, B, 730)
    i84 = 84
    print(f"12 weeks: dynamic {m[i84]:.2f}, exact {float(exact_mass(60, I, A, B, 84)):.2f}, naive {float(naive_mass(60, I, A, B, 84)):.2f} kg")
    print(f"2 years:  dynamic {m[730]:.2f}, naive {float(naive_mass(60, I, A, B, 730)):.2f} kg")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.plot(t / 7, m, label="dynamic model (Euler)")
    ax1.plot(t / 7, exact_mass(60, I, A, B, t), "k:", label="closed form")
    ax1.plot(t / 7, naive_mass(60, I, A, B, t), "--", label="naive 7700 rule")
    ax1.axhline(steady_state(I, A, B), color="gray", lw=0.8)
    ax1.axvline(12, color="gray", ls=":")
    ax1.set_xlabel("time (weeks)")
    ax1.set_ylabel("body mass (kg)")
    ax1.set_title("Mass approaches a steady state (grey line)")
    ax1.grid(alpha=0.3)
    ax1.legend()

    logged = E0
    d = monte_carlo(60.0, logged, A, B, 84)
    p5, p50, p95 = np.percentile(d, [5, 50, 95])
    print(f"Monte Carlo (logged intake = {logged:.0f}): 5th {p5:.2f}, median {p50:.2f}, 95th {p95:.2f} kg, sd {d.std():.2f}")
    print(f"label rounding worst case for 8 labels: {rounding_worst_case(8):.0f} kcal/day")
    print(f"20 percent under-logging of {logged:.0f} kcal: true intake {portion_error(logged, 0.2):.0f} kcal/day")
    ax2.hist(d, bins=40, color="#457b9d")
    ax2.axvline(p5, color="k", ls="--")
    ax2.axvline(p95, color="k", ls="--", label="5th and 95th percentile")
    ax2.set_xlabel("12-week mass change (kg)")
    ax2.set_ylabel("number of draws (of 5000)")
    ax2.set_title("Logging and BMR errors of up to 10 percent")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig.tight_layout()
    fig.savefig(OUT / "dynamic_and_spread.png", dpi=120)

    # the mini-project table
    print("walk (h)  balance with 1500 kcal meals")
    for h in (0.0, 0.25, 0.5, 0.75, 1.0):
        print(f"{h:5.2f}    {plan_balance(1500.0, h):8.1f}")
    print("passing plans:", find_plans())
    print("outcome (1500, 0.25):", round(plan_outcome(1500, 0.25), 2), plan_spread(1500, 0.25))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
