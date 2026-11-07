"""Session 4 (Level 3): a fourth-order symplectic solver built from the midpoint rule.

Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: a fourth-order symplectic solver
# **A. Real-world problem.** In Session 3 the implicit midpoint rule kept the energy error of the
# double pendulum bounded, but only at the price of a *large* error at a coarse step: with
# h = 0.02 s it wanders by 1.6 percent of the energy scale. Satellite orbits, molecules and planets
# are simulated for billions of steps, so people want a solver that is both symplectic **and**
# accurate. Today we build one by composing three midpoint steps, check that it really is
# fourth order, count what it costs, and find out where it stops working.
#
# Equal balls (1 kg), equal 1 m rods, no friction. The solver ideas here are general; the numbers
# are for this pendulum released from rest with both rods at the same angle.

# %%
import math
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81                 # gravity, m/s^2
E_REF = 3 * G            # energy scale (m1 + m2) g l1 + m2 g l2 = 29.43 J
CALLS = [0]              # how many times the Hamiltonian rate function has been evaluated (our measure of work)
NOT_CONVERGED = [0]      # how many midpoint solves gave up after max_iter tries


# %% [markdown]
# ## Step 1: the pieces from Sessions 2 and 3
# The equations of motion and RK4 (the reference), and the implicit midpoint rule on the
# Hamiltonian form. Two small additions: every evaluation of the rate is counted in `CALLS`, so
# we can measure *work* instead of guessing it, and a midpoint solve that fails to converge is
# counted in `NOT_CONVERGED` instead of failing silently.

# %%
def rate(state):
    """(theta1', theta2', omega1', omega2') for state (theta1, theta2, omega1, omega2)."""
    t1, t2, w1, w2 = state
    d = t1 - t2
    den = 3.0 - math.cos(2 * d)
    a1 = (-3 * G * math.sin(t1) - G * math.sin(t1 - 2 * t2) - 2 * math.sin(d) * (w2 ** 2 + w1 ** 2 * math.cos(d))) / den
    a2 = (2 * math.sin(d) * (2 * w1 ** 2 + 2 * G * math.cos(t1) + w2 ** 2 * math.cos(d))) / den
    return (w1, w2, a1, a2)


def energy(state):
    """Total energy E = T + V in joules (pivot is the zero of height)."""
    t1, t2, w1, w2 = state
    return w1 ** 2 + 0.5 * w2 ** 2 + w1 * w2 * math.cos(t1 - t2) - 2 * G * math.cos(t1) - G * math.cos(t2)


def release(a_deg):
    a = math.radians(a_deg)
    return (a, a, 0.0, 0.0)


def rk4_step(state, h):
    """Runge-Kutta 4: four slopes per step (not symplectic)."""
    def shift(s, k, f):
        return tuple(a + f * b for a, b in zip(s, k))
    k1 = rate(state)
    k2 = rate(shift(state, k1, h / 2))
    k3 = rate(shift(state, k2, h / 2))
    k4 = rate(shift(state, k3, h))
    return tuple(a + h / 6 * (b + 2 * c + 2 * d + e) for a, b, c, d, e in zip(state, k1, k2, k3, k4))


def _to_momenta(state):
    t1, t2, w1, w2 = state
    c = math.cos(t1 - t2)
    return (t1, t2, 2 * w1 + c * w2, c * w1 + w2)


def _to_rates(z):
    q1, q2, p1, p2 = z
    c = math.cos(q1 - q2)
    det = 2.0 - c * c
    return (q1, q2, (p1 - c * p2) / det, (2 * p2 - c * p1) / det)


def _hamilton_rate(z):
    CALLS[0] += 1
    q1, q2, p1, p2 = z
    w1, w2 = _to_rates(z)[2:]
    sd = math.sin(q1 - q2)
    return (w1, w2, -w1 * w2 * sd - 2 * G * math.sin(q1), w1 * w2 * sd - G * math.sin(q2))


def midpoint_step(state, h, tol=1e-14, max_iter=60):
    """One implicit-midpoint step (symplectic, second order). h may be negative (a step backward)."""
    z = _to_momenta(state)
    y = tuple(a + h * b for a, b in zip(z, _hamilton_rate(z)))
    for _ in range(max_iter):
        mid = tuple((a + b) / 2 for a, b in zip(z, y))
        y_new = tuple(a + h * b for a, b in zip(z, _hamilton_rate(mid)))
        change = max(abs(a - b) for a, b in zip(y, y_new))
        y = y_new
        if change < tol:
            break
    else:
        if change > 1e-9:              # tol is at round-off level, so only a clearly unsettled solve counts as a failure
            NOT_CONVERGED[0] += 1      # the substitution did not settle: this step is not trustworthy
    return _to_rates(y)


# %% [markdown]
# ## Step 2: composing three midpoint steps
# The midpoint step is *symmetric* (stepping forward h and then back -h returns to the start), and
# its error per step starts with an h^3 term. Take three steps of sizes gamma1 h, gamma0 h, gamma1 h
# in a row (a "triple jump"). Two conditions decide the sizes:
#
#     2 gamma1 + gamma0 = 1            (the three steps add up to one step h)
#     2 gamma1^3 + gamma0^3 = 0        (the h^3 error terms cancel)
#
# The solution is gamma1 = 1 / (2 - 2^(1/3)) = 1.3512 and gamma0 = -2^(1/3) / (2 - 2^(1/3)) = -1.7024.
# So one step of the new solver goes forward 1.35 h, **backward** 1.70 h, then forward 1.35 h. A
# composition of symplectic steps is symplectic, and the symmetric order keeps the method
# reversible, so the energy error stays bounded, now with the error of a fourth-order method.

# %%
GAMMA1 = 1.0 / (2.0 - 2.0 ** (1.0 / 3.0))
GAMMA0 = -(2.0 ** (1.0 / 3.0)) / (2.0 - 2.0 ** (1.0 / 3.0))
TRIPLE_JUMP = (GAMMA1, GAMMA0, GAMMA1)


def order_conditions(gammas):
    """(sum of the sizes, sum of their cubes): a triple jump needs (1, 0)."""
    return sum(gammas), sum(g ** 3 for g in gammas)


def composed_step(state, h, gammas=TRIPLE_JUMP):
    """One step of the fourth-order solver: a midpoint step for each size in gammas times h."""
    for g in gammas:
        state = midpoint_step(state, g * h)
    return state


def reversibility_error(step, state, h):
    """Largest change of the state after a step h followed by a step -h (zero for a reversible method)."""
    back = step(step(state, h), -h)
    return max(abs(a - b) for a, b in zip(back, state))


# %% [markdown]
# ## Step 3: measuring the order
# A method of order p has a global error that shrinks like h^p, so halving the step divides the
# error by 2^p: 4 for the midpoint rule (p = 2), 16 for the composition (p = 4). We compare with a
# very fine RK4 reference (h = 0.0005 s) after a short time T, starting from a gentle motion where
# the error has not been amplified by chaos yet.

# %%
START_GENTLE = (0.5, -0.3, 0.2, 0.1)


def run(step, state0, duration, h):
    s = tuple(float(v) for v in state0)
    for _ in range(int(round(duration / h))):
        s = step(s, h)
    return s


def reference_state(state0, duration, h_ref=0.0005):
    return run(rk4_step, state0, duration, h_ref)


def state_error(step, state0, duration, h, ref=None):
    """Largest difference of any of the four state numbers from the fine RK4 reference."""
    ref = reference_state(state0, duration) if ref is None else ref
    return float(np.max(np.abs(np.array(run(step, state0, duration, h)) - np.array(ref))))


def observed_orders(errors):
    """For errors measured at steps h, h/2, h/4, ...: log2 of each error ratio (the observed order)."""
    return [math.log2(a / b) for a, b in zip(errors[:-1], errors[1:])]


# %% [markdown]
# ## Step 4: energy over a long run
# This is the test the roadmap sets: 1000 s at h = 0.02 s for the 120 degree release. `drift_curve`
# records the energy error (E - E0) / E_REF every `stride` steps, here every 2 s.
#
# **A warning about chaos.** This pendulum is chaotic, so a change of 1e-13 rad in the start (the
# size of round-off) gives a different orbit after about 30 s, and the *largest* energy error of
# one run is a lucky-or-unlucky number: for the composition it ranges from about 0.005 to 0.012
# over nearby starts. So we also use `typical_worst_error`: the median, over a handful of nearby
# starts, of the largest energy error. That number does not depend on the computer's last bit.

# %%
def drift_curve(step, state0, duration, h, stride=100):
    """Times and relative energy error (E - E0) / E_REF, sampled every `stride` steps."""
    n = int(round(duration / h))
    s = tuple(float(v) for v in state0)
    e0 = energy(s)
    ts, ds = [], []
    for i in range(1, n + 1):
        s = step(s, h)
        if i % stride == 0:
            ts.append(i * h)
            ds.append((energy(s) - e0) / E_REF)
    return np.array(ts), np.array(ds)


def nearby_starts(a_deg, n=5, spread=1e-9, seed=11):
    """n starts that differ from the release by random amounts of about `spread` in all four numbers."""
    rng = np.random.default_rng(seed)
    base = np.array(release(a_deg))
    return [tuple(float(v) for v in base + spread * rng.standard_normal(4)) for _ in range(n)]


# %% [markdown]
# ## Step 5: what it costs
# One step of the composition is three midpoint solves, and each solve repeats the substitution
# until it settles. So the right comparison is not "same step" but **same work**: we count the rate
# evaluations (`CALLS`) and ask how much work each solver needs to reach a given accuracy. We
# measure two accuracies: the typical largest energy error over a chaotic run, and the error of
# the state after 5 s compared with the fine reference.

# %%
def worst_energy_error(step, state0, duration, h, every=1.0):
    """(largest |E - E0| / E_REF seen every `every` seconds, rate evaluations used). Failure gives (inf, work)."""
    CALLS[0] = 0
    s = tuple(float(v) for v in state0)
    e0 = energy(s)
    n = int(round(duration / h))
    k = max(1, int(round(every / h)))
    worst = 0.0
    try:
        for i in range(1, n + 1):
            s = step(s, h)
            if i % k == 0:
                e = abs(energy(s) - e0) / E_REF
                if not math.isfinite(e):
                    return math.inf, CALLS[0]
                worst = max(worst, e)
    except (ValueError, OverflowError):
        return math.inf, CALLS[0]
    return worst, CALLS[0]


def typical_worst_error(step, a_deg, duration, h, n=5):
    """(median over n nearby starts of the largest energy error, median work, solves that did not settle)."""
    errs, works = [], []
    NOT_CONVERGED[0] = 0
    for s in nearby_starts(a_deg, n):
        e, w = worst_energy_error(step, s, duration, h)
        errs.append(e)
        works.append(w)
    return float(np.median(errs)), int(np.median(works)), NOT_CONVERGED[0]


def trajectory_error_and_work(step, state0, duration, h, ref):
    CALLS[0] = 0
    err = state_error(step, state0, duration, h, ref)
    return err, CALLS[0]


def ladder_results(step, a_deg, duration, ladder, n=5):
    """List of (h, typical largest energy error, typical work, unsettled solves) for each step in `ladder`."""
    return [(h,) + typical_worst_error(step, a_deg, duration, h, n) for h in ladder]


def cheapest_for_tolerance(results, tol):
    """(work, h, error) of the cheapest entry of `ladder_results` with error at most `tol`, or None."""
    ok = [(w, h, e) for h, e, w, _ in results if e <= tol]
    return min(ok) if ok else None


# %% [markdown]
# ## Step 6: where it stops working
# The midpoint step is *implicit*: we solve it by repeating a substitution, and that only settles
# when h times the fastest rate of change is smaller than about 2. The composition steps **backward**
# by 1.70 h, so its middle solve is the hardest one. When the repetition does not settle, the step
# is wrong, and the energy error jumps. `ladder_results` reports, for each step, the typical energy
# error and the number of solves that gave up (`inf` means the run produced garbage or crashed).

# %% [markdown]
# ## See it
# Figure 1: the energy error of RK4, the midpoint rule and the composition over 1000 s. Figure 2:
# the error against the step, with slopes 2 and 4. Figure 3: error against work. Figure 4: what
# happens at coarse steps.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib.ticker import NullFormatter

    def tidy(ax):
        """Light grid, and no crowded minor tick labels on log axes."""
        ax.grid(alpha=0.3, which="both")
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.yaxis.set_minor_formatter(NullFormatter())

    def xticks(ax, vals):
        ax.set_xticks(vals)
        ax.set_xticklabels([f"{v:g}" for v in vals])

    OUT.mkdir(exist_ok=True)
    BLUE, ORANGE, MAGENTA, GREY = "#0072b2", "#c86a00", "#d81b60", "#555555"
    s0 = release(120.0)
    print("triple jump sizes:", round(GAMMA1, 6), round(GAMMA0, 6), "conditions (1, 0):", order_conditions(TRIPLE_JUMP))
    print("reversibility (step h then -h), h = 0.05 from the gentle start:",
          {n: f"{reversibility_error(f, START_GENTLE, 0.05):.1e}" for n, f in (("rk4", rk4_step), ("midpoint", midpoint_step), ("composed", composed_step))})

    # --- Figure 1: energy over 1000 s at h = 0.02
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    for name, f, col, ls in (("RK4", rk4_step, MAGENTA, "-"), ("midpoint (order 2)", midpoint_step, ORANGE, "--"), ("composition (order 4)", composed_step, BLUE, "-")):
        NOT_CONVERGED[0] = 0
        t, d = drift_curve(f, s0, 1000.0, 0.02)
        ax1.semilogy(t, np.maximum(np.abs(d), 1e-6), color=col, ls=ls, lw=1.6, label=name)
        print(f"  {name:24s} worst energy error {np.abs(d).max():.4f} of E_ref   solves that did not converge: {NOT_CONVERGED[0]}")
    ax1.axhline(1e-2, color=GREY, ls=":", lw=1.2)
    ax1.text(995, 1.15e-2, "roadmap limit 1e-2", color=GREY, fontsize=8, ha="right")
    ax1.set_ylim(1e-6, 0.5)
    ax1.set_xlabel("time (s)")
    ax1.set_ylabel("|E - E0| / E_ref")
    ax1.set_title("Energy error of three solvers, 120 degree release, h = 0.02 s (one run)")
    tidy(ax1)
    ax1.legend(fontsize=8, loc="lower right")
    fig1.tight_layout()
    fig1.savefig(OUT / "energy_1000s.png", dpi=120)
    print("largest energy error over 1000 s for 5 nearby starts (h = 0.02):")
    for name, f in (("RK4", rk4_step), ("midpoint", midpoint_step), ("composition", composed_step)):
        worsts = [float(np.abs(drift_curve(f, s, 1000.0, 0.02)[1]).max()) for s in nearby_starts(120.0, 5)]
        print(f"  {name:12s}", [round(w, 4) for w in worsts], "median", round(float(np.median(worsts)), 4))

    # --- Figure 2: order
    hs = [0.1, 0.05, 0.025, 0.0125]
    ref = reference_state(START_GENTLE, 0.4)
    e_mid = [state_error(midpoint_step, START_GENTLE, 0.4, h, ref) for h in hs]
    e_com = [state_error(composed_step, START_GENTLE, 0.4, h, ref) for h in hs]
    print("order test errors (midpoint):", [f"{e:.2e}" for e in e_mid], "observed orders", [round(o, 2) for o in observed_orders(e_mid)])
    print("order test errors (composed):", [f"{e:.2e}" for e in e_com], "observed orders", [round(o, 2) for o in observed_orders(e_com)])
    fig2, ax2 = plt.subplots(figsize=(6.5, 4.2))
    ax2.loglog(hs, e_mid, "o--", color=ORANGE, label="midpoint (order 2)")
    ax2.loglog(hs, e_com, "s-", color=BLUE, label="composition (order 4)")
    xs = np.array([hs[0], hs[-1]])
    ax2.loglog(xs, 0.5 * e_mid[0] * (xs / hs[0]) ** 2, ":", color=GREY, label="slope 2 (shifted down)")
    ax2.loglog(xs, e_com[1] * (xs / hs[1]) ** 4 * 0.5, "-.", color=GREY, label="slope 4 (shifted down)")
    ax2.set_xlabel("step h (s)")
    ax2.set_ylabel("largest state error after 0.4 s")
    ax2.set_title("Halving h: error / 4 for order 2, error / 16 for order 4")
    tidy(ax2)
    xticks(ax2, [0.0125, 0.025, 0.05, 0.1])
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "order_test.png", dpi=120)

    # --- Figure 3: work and precision (typical energy error over 60 s; state error after 5 s)
    ladder_m = [0.03, 0.02, 0.015, 0.01, 0.0075, 0.005, 0.0035, 0.0025]
    ladder_c = [0.03, 0.025, 0.02, 0.015, 0.01, 0.0075, 0.005]
    ref5 = reference_state(s0, 5.0)
    res = {"midpoint": ladder_results(midpoint_step, 120.0, 60.0, ladder_m),
           "composition": ladder_results(composed_step, 120.0, 60.0, ladder_c)}
    tr = {}
    for name, f in (("midpoint", midpoint_step), ("composition", composed_step)):
        tr[name] = [trajectory_error_and_work(f, s0, 5.0, h, ref5) for h in [0.05, 0.025, 0.0125, 0.00625, 0.003125]]
        print(name, "energy (h, typical error, work, unsettled):", [(h, f"{e:.1e}", w, b) for h, e, w, b in res[name]])
        print(name, "state error after 5 s (error, work):", [(f"{e:.1e}", w) for e, w in tr[name]])
    fig3, axs3 = plt.subplots(1, 2, figsize=(9.6, 4.0))
    for name, col, mk in (("midpoint", ORANGE, "o--"), ("composition", BLUE, "s-")):
        good = [(w, max(e, 1e-7)) for _, e, w, _ in res[name] if math.isfinite(e)]
        axs3[0].loglog(*zip(*good), mk, color=col, label=name)
        axs3[1].loglog([w for e, w in tr[name]], [e for e, w in tr[name]], mk, color=col, label=name)
    axs3[0].set_xlabel("rate evaluations (work)")
    axs3[0].set_ylabel("typical largest |E - E0| / E_ref over 60 s")
    axs3[0].set_title("Energy error: the midpoint rule is cheaper for loose limits", fontsize=10)
    axs3[1].set_xlabel("rate evaluations (work)")
    axs3[1].set_ylabel("state error after 5 s")
    axs3[1].set_title("State error after 5 s: order 4 is far cheaper", fontsize=10)
    for a in axs3:
        tidy(a)
        a.legend(fontsize=8)
    xticks(axs3[0], [2e4, 5e4, 1e5, 2e5, 4e5])
    xticks(axs3[1], [3e3, 5e3, 1e4, 2e4, 4e4])
    fig3.tight_layout()
    fig3.savefig(OUT / "work_precision.png", dpi=120)
    for tol in (1e-2, 1e-3, 1e-4):
        print(f"tolerance {tol:g}: midpoint {cheapest_for_tolerance(res['midpoint'], tol)}   composition {cheapest_for_tolerance(res['composition'], tol)}")

    # --- Figure 4: coarse steps
    ladder = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.05]
    surveys = {n: ladder_results(f, 120.0, 60.0, ladder) for n, f in (("midpoint", midpoint_step), ("composition", composed_step))}
    fig4, ax4 = plt.subplots(figsize=(6.8, 4.2))
    for name, col, mk in (("midpoint", ORANGE, "o--"), ("composition", BLUE, "s-")):
        rows = surveys[name]
        ok = [(h, e) for h, e, _, _ in rows if math.isfinite(e)]
        ax4.loglog([h for h, _ in ok], [max(e, 1e-6) for _, e in ok], mk, color=col, label=name)
        bad = [h for h, e, _, _ in rows if not math.isfinite(e)]
        ax4.plot(bad, [3.0] * len(bad), "x", color=MAGENTA, ms=9, mew=2, label="solver failed" if name == "composition" else None)
        print(name, [(h, f"{e:.1e}", n) for h, e, _, n in rows])
    ax4.axhline(1.0, color=GREY, ls=":", lw=1)
    ax4.set_xlabel("step h (s)")
    ax4.set_ylabel("typical largest |E - E0| / E_ref over 60 s")
    ax4.set_title("The fourth-order solver gives up at a smaller step than the midpoint rule", fontsize=10)
    tidy(ax4)
    xticks(ax4, [0.005, 0.01, 0.02, 0.04])
    ax4.legend(fontsize=8)
    fig4.tight_layout()
    fig4.savefig(OUT / "step_limit.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
