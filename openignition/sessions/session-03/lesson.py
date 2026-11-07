"""Session 3 (Level 3): stiffness, two integrators, and validation of the ignition delay.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: stiffness, solvers and validation
# **A. Real-world problem.** Combustion codes spend most of their time on ignition-type chemistry
# because it is *stiff*: for a long time nothing happens, then everything changes within a few
# microseconds, and afterwards a very fast mode remains that must be integrated without blowing up.
# How do we compute the delay reliably, and how do we know the answer is right?
#
# **Still a toy.** One Arrhenius step with toy numbers. Real hydrogen-oxygen ignition is a chain-
# branching network (radicals multiply, with explosion limits that depend on pressure and
# temperature); it is not a single-step thermal runaway, and these numbers are not hydrogen's.
#
# **Plan.** (1) the model and its Jacobian, (2) an exact reference, (3) explicit RK4 (fixed and
# adaptive), (4) implicit trapezoid with Newton (adaptive), (5) cost and accuracy, (6) failure,
# (7) sensitivity, pressure and the Semenov criterion.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R_GAS = 8.314      # J/(mol K)
RISE = 400.0       # ignition criterion: temperature rise, K


def make_params(A=2.5e9, Ea=150e3, dT=1500.0, h=0.0, Ta=0.0, frozen=False):
    """Toy reactor: rate k = A exp(-Ea/(R T)) (1/s, J/mol), dT = Q/cp (K), heat loss h (1/s) to
    surroundings at Ta (K). `frozen=True` keeps the fuel fixed at c = 1 (used for the Semenov test)."""
    return dict(A=A, Ea=Ea, dT=dT, h=h, Ta=Ta, frozen=frozen)


def rate_k(T, p):
    return p["A"] * np.exp(-p["Ea"] / (R_GAS * T))


# %% [markdown]
# ## Step 1: right-hand side and Jacobian
# State `y = (T, c)`. With loss: `dT/dt = dT k c - h (T - Ta)`, `dc/dt = -k c`.
# The Jacobian `J = d f / d y` (a 2x2 matrix) tells how fast small errors grow or decay. Its
# eigenvalues are the model's *time scales*. After ignition `c` is almost 0 and `J` is about
# `-k(T_final)`: a decay rate of millions per second. That is the stiffness.

# %%
def rhs(y, p):
    T, c = y
    burn = rate_k(T, p) * c
    dc = 0.0 if p["frozen"] else -burn
    return np.array([p["dT"] * burn - p["h"] * (T - p["Ta"]), dc])


def jacobian(y, p):
    T, c = y
    k = rate_k(T, p)
    dk = k * p["Ea"] / (R_GAS * T * T)
    return np.array([[p["dT"] * dk * c - p["h"], p["dT"] * k],
                     [0.0 if p["frozen"] else -dk * c, 0.0 if p["frozen"] else -k]])


# %% [markdown]
# ## Step 2: a trusted reference
# Without heat loss, `T + dT c` is constant, so `tau = integral of dc / (k c)` from the fuel level at
# ignition up to 1. Gauss-Legendre quadrature gives it to many digits with no time-stepping.
# We use it to judge the integrators.

# %%
_X, _W = np.polynomial.legendre.leggauss(200)


def reference_delay(T0, p=None, rise=RISE):
    p = p or make_params()
    cs = 1.0 - rise / p["dT"]
    c = 0.5 * (1 - cs) * _X + 0.5 * (1 + cs)
    f = 1.0 / (rate_k(T0 + p["dT"] * (1 - c), p) * c)
    return float(0.5 * (1 - cs) * np.sum(_W * f))


def crossing_time(t0, y0, f0, t1, y1, f1, level):
    """Time at which T crosses `level` inside one step, from a cubic Hermite fit of T
    (uses the values and slopes at both ends)."""
    h = t1 - t0

    def T_at(s):
        return ((2 * s ** 3 - 3 * s ** 2 + 1) * y0[0] + (s ** 3 - 2 * s ** 2 + s) * h * f0[0]
                + (-2 * s ** 3 + 3 * s ** 2) * y1[0] + (s ** 3 - s ** 2) * h * f1[0])
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if T_at(mid) < level else (lo, mid)
    return t0 + 0.5 * (lo + hi) * h


# %% [markdown]
# ## Step 3: explicit RK4
# Fourth-order Runge-Kutta evaluates the right-hand side four times per step and needs no solving.
# But an explicit method is stable only if `step * (fastest decay rate)` is below about 2.8. After
# ignition the decay rate is millions per second, so the step must stay at about a microsecond even
# when nothing interesting is happening any more. This is the price of stiffness.

# %%
def rk4_step(y, h, p):
    k1 = rhs(y, p)
    k2 = rhs(y + h / 2 * k1, p)
    k3 = rhs(y + h / 2 * k2, p)
    k4 = rhs(y + h * k3, p)
    return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def rk4_fixed(T0, p, dt, t_end, rise=RISE):
    """Fixed-step RK4 to t_end. Returns (delay or None, final state, steps, finite_flag).
    finite_flag is False if the state became non-finite or absurd (above 1e5 K): a blow-up."""
    y = np.array([T0, 1.0])
    t, n, tau = 0.0, 0, None
    while t < t_end - 1e-15:
        f0 = rhs(y, p)
        yn = rk4_step(y, dt, p)
        n += 1
        if not np.all(np.isfinite(yn)) or abs(yn[0]) > 1e5:
            return tau, yn, n, False
        if tau is None and yn[0] >= T0 + rise:
            tau = crossing_time(t, y, f0, t + dt, yn, rhs(yn, p), T0 + rise)
        y, t = yn, t + dt
    return tau, y, n, True


def rk4_adaptive(T0, p, t_end, rtol, rise=RISE):
    """RK4 with step doubling: compare one step h with two steps h/2; accept if the
    difference (divided by 15) is within tolerance. Returns dict with delay, steps and RHS calls."""
    y, t, h = np.array([T0, 1.0]), 0.0, 1e-6
    acc = rej = nf = 0
    tau = None
    while t < t_end:
        h = min(h, t_end - t)
        big = rk4_step(y, h, p)
        half = rk4_step(rk4_step(y, h / 2, p), h / 2, p)
        nf += 12
        err = float(np.max(np.abs(half - big) / (15 * (rtol * np.abs(half) + 1e-10))))
        if err <= 1.0:
            if tau is None and half[0] >= T0 + rise:
                tau = crossing_time(t, y, rhs(y, p), t + h, half, rhs(half, p), T0 + rise)
            y, t = half, t + h
            acc += 1
        else:
            rej += 1
        h *= min(4.0, max(0.2, 0.9 * (1.0 / max(err, 1e-10)) ** 0.2))
    return dict(tau=tau, final=y, steps=acc, rejected=rej, rhs_calls=nf)


# %% [markdown]
# ## Step 4: implicit trapezoid with Newton
# An implicit method defines the new state by an equation that contains the new state:
# `z = y + h/2 (f(y) + f(z))`. We solve it with Newton's method (using the Jacobian), which costs a
# few right-hand sides and a 2x2 linear solve per step but stays stable for large steps.
# The trapezoid rule is second order; combining a full step with two half steps lets us estimate the
# error and improve the answer by extrapolation (Richardson).

# %%
def trapezoid_solve(y, h, p, f0):
    """Solve z = y + h/2 (f(y) + f(z)) by Newton. Returns (z, newton_iterations, converged)."""
    z = y + h * f0
    nit = 0
    for _ in range(12):
        if not (np.all(np.isfinite(z)) and 200.0 < z[0] < 20000.0):
            return z, nit, False
        g = z - y - h / 2 * (f0 + rhs(z, p))
        nit += 1
        try:
            dz = np.linalg.solve(np.eye(2) - h / 2 * jacobian(z, p), -g)
        except np.linalg.LinAlgError:
            return z, nit, False
        z = z + dz
        if np.max(np.abs(dz) / (1e-8 * np.abs(z) + 1e-10)) < 1.0:
            return z, nit, True
    return z, nit, False


def trapezoid_adaptive(T0, p, t_end, rtol, rise=RISE, stop_at_event=False):
    """Adaptive trapezoid (step doubling + extrapolation). Returns dict with delay, steps, RHS calls.
    If the event (T0 + rise) is found and stop_at_event is True, it stops there."""
    y, t, h = np.array([T0, 1.0]), 0.0, 1e-6
    acc = rej = nf = 0
    tau = None
    while t < t_end:
        h = min(h, t_end - t)
        f0 = rhs(y, p)
        big, n1, ok1 = trapezoid_solve(y, h, p, f0)
        mid, n2, ok2 = trapezoid_solve(y, h / 2, p, f0)
        half, n3, ok3 = trapezoid_solve(mid, h / 2, p, rhs(mid, p)) if ok2 else (mid, 0, False)
        nf += 2 + n1 + n2 + n3
        if not (ok1 and ok2 and ok3):
            rej += 1
            h *= 0.25
            continue
        err = float(np.max(np.abs(half - big) / (3 * (rtol * np.abs(half) + 1e-10))))
        if err <= 1.0:
            new = half + (half - big) / 3.0
            if tau is None and new[0] >= T0 + rise:
                tau = crossing_time(t, y, f0, t + h, new, rhs(new, p), T0 + rise)
                if stop_at_event:
                    acc += 1
                    break
            y, t = new, t + h
            acc += 1
        else:
            rej += 1
        h *= min(4.0, max(0.2, 0.9 * (1.0 / max(err, 1e-10)) ** (1.0 / 3.0)))
    return dict(tau=tau, final=y, steps=acc, rejected=rej, rhs_calls=nf)


def backward_euler_fixed(T0, p, dt, t_end, rise=RISE):
    """Fixed-step backward Euler: z = y + h f(z). Always stable, only first-order accurate.
    Returns (delay or None, final state, steps)."""
    y, t, n, tau = np.array([T0, 1.0]), 0.0, 0, None
    while t < t_end - 1e-15:
        z = y.copy()
        for _ in range(60):
            g = z - y - dt * rhs(z, p)
            dz = np.linalg.solve(np.eye(2) - dt * jacobian(z, p), -g)
            z = z + dz
            z[0] = max(z[0], 200.0)
            if np.max(np.abs(dz) / (1e-9 * np.abs(z) + 1e-12)) < 1.0:
                break
        n += 1
        if tau is None and z[0] >= T0 + rise:
            tau = t + dt * (T0 + rise - y[0]) / (z[0] - y[0])     # straight-line interpolation
        y, t = z, t + dt
    return tau, y, n


# %% [markdown]
# ## Step 5: sensitivity, pressure and the Semenov criterion
# *Normalised sensitivity*: `S_x = d ln(tau) / d ln(x)` is the percentage change of the delay for a
# one-percent change of x (we use a central difference). *Pressure*: in the toy model the rate
# scales as `k proportional to (P/P0)^m` with an illustrative exponent m = 1 (real hydrogen
# behaviour is not a simple power law: it changes sign across the explosion limits).
# *Semenov*: with heat loss `h` to surroundings at `Ta`, and fuel taken as constant, a steady state
# exists only if `psi = dT k(Ta) Ea / (R Ta^2 h)` is at most `1/e`; above that the gas ignites.

# %%
def delay_for(T0, **kw):
    return reference_delay(T0, make_params(**kw))


def log_sensitivity(fn, x, rel=1e-3):
    """d ln fn / d ln x by a central difference."""
    return float((np.log(fn(x * (1 + rel))) - np.log(fn(x * (1 - rel)))) / (np.log(1 + rel) - np.log(1 - rel)))


def delay_at_pressure(T0, P_atm, m=1.0, P0_atm=1.0):
    """Toy pressure effect: A scales as (P/P0)^m, so the delay scales as (P/P0)^(-m)."""
    return delay_for(T0, A=2.5e9 * (P_atm / P0_atm) ** m)


def semenov_psi(Ta, h, A=2.5e9, Ea=150e3, dT=1500.0):
    return dT * A * np.exp(-Ea / (R_GAS * Ta)) * Ea / (R_GAS * Ta ** 2 * h)


def critical_Ta_analytic(h, **kw):
    """Smallest surrounding temperature (K) for which psi >= 1/e (bisection)."""
    lo, hi = 400.0, 2000.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if semenov_psi(mid, h, **kw) < np.exp(-1.0) else (lo, mid)
    return 0.5 * (lo + hi)


def ignites_with_loss(Ta, h, frozen=True, rtol=1e-6, t_end=None):
    """Simulate the lossy reactor from T = Ta; True if T reaches Ta + 400 K."""
    p = make_params(h=h, Ta=Ta, frozen=frozen)
    t_end = t_end or 40.0 / h
    return trapezoid_adaptive(Ta, p, t_end, rtol, stop_at_event=True)["tau"] is not None


def critical_Ta_numeric(h, frozen=True, lo=700.0, hi=1100.0):
    """Bisection on the simulated yes/no ignition result."""
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if ignites_with_loss(mid, h, frozen) else (mid, hi)
    return 0.5 * (lo + hi)


# %% [markdown]
# ## Step 6: tabulate a fuel (the mini-project tool)
# `delay_table` runs the adaptive implicit solver at many starting temperatures; `fit_line` fits
# `ln(tau)` against `1000/T0`. "Toy fuel B" (a different set of made-up numbers) is used in the
# mini-project.

# %%
FUEL_B = dict(A=1.0e7, Ea=110e3, dT=1200.0)


def delay_table(T0s, rtol=1e-5, **kw):
    """Ignition delays (s) from the adaptive trapezoid solver, stopped at the event."""
    p = make_params(**kw)
    out = []
    for T0 in T0s:
        fk = R_GAS * T0 ** 2 / (p["Ea"] * p["dT"] * rate_k(T0, p))      # a rough time scale
        out.append(trapezoid_adaptive(T0, p, 5.0 * fk, rtol, stop_at_event=True)["tau"])
    return np.array(out)


def fit_line(T0s, taus):
    """Fit ln(tau) = a + b * 1000/T0. Returns slope b, intercept a, R^2."""
    x, y = 1000.0 / np.asarray(T0s, dtype=float), np.log(taus)
    b, a = np.polyfit(x, y, 1)
    return float(b), float(a), float(1 - np.sum((y - a - b * x) ** 2) / np.sum((y - y.mean()) ** 2))


def temperature_for_delay(T0s, taus, target):
    """T0 at which the fitted line gives `target` seconds."""
    b, a, _ = fit_line(T0s, taus)
    return float(1000.0 / ((np.log(target) - a) / b))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    p = make_params()
    T0 = 1000.0
    ref = reference_delay(T0, p)
    print(f"reference delay at {T0:.0f} K: {ref * 1e3:.5f} ms")
    ev = np.linalg.eigvals(jacobian(np.array([2500.0, 1e-12]), p))
    print(f"Jacobian eigenvalues after ignition: {ev.real.min():.3g} and {ev.real.max():.3g} per second")

    print("\nfixed-step RK4 to 3 ms (steps, delay error, state at the end)")
    for dt in (1e-6, 5e-6, 2e-5, 1e-4, 1e-3, 2e-3):
        tau, y, n, fin = rk4_fixed(T0, p, dt, 3e-3)
        err = "none" if tau is None else f"{100 * (tau / ref - 1):+.2f}%"
        print(f"  dt = {dt * 1e6:7.0f} us  steps = {n:5d}  delay error {err:>8}  final T = {y[0]:.4g} K  finite = {fin}")
    print("\nfixed-step backward Euler to 3 ms")
    for dt in (1e-5, 1e-4, 1e-3, 2e-3):
        tau, y, n = backward_euler_fixed(T0, p, dt, 3e-3)
        err = "none" if tau is None else f"{100 * (tau / ref - 1):+.2f}%"
        print(f"  dt = {dt * 1e6:7.0f} us  steps = {n:5d}  delay error {err:>8}  final T = {y[0]:.1f} K")

    print("\nadaptive solvers to 30 ms: tolerance -> delay error, steps, rhs calls")
    rows = []
    for rtol in (1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7):
        a = rk4_adaptive(T0, p, 30e-3, rtol)
        b = trapezoid_adaptive(T0, p, 30e-3, rtol)
        rows.append((rtol, a, b))
        print(f"  rtol {rtol:.0e}  RK4: err {100 * (a['tau'] / ref - 1):+.4f}% steps {a['steps']:5d} calls {a['rhs_calls']:6d}"
              f" | trapezoid: err {100 * (b['tau'] / ref - 1):+.4f}% steps {b['steps']:4d} calls {b['rhs_calls']:5d}")
    print("\nhorizon (rtol 1e-4): steps to reach the end time")
    for te in (3e-3, 1e-2, 3e-2):
        a = rk4_adaptive(T0, p, te, 1e-4)
        b = trapezoid_adaptive(T0, p, te, 1e-4)
        print(f"  t_end {te * 1e3:6.0f} ms  RK4 steps {a['steps']:6d}  trapezoid steps {b['steps']:4d}")

    print("\nsensitivities at 1000 K (d ln tau / d ln x):")
    print(f"  activation energy Ea (A fixed): {log_sensitivity(lambda x: delay_for(T0, Ea=x), 150e3):+.2f}")
    print(f"  heat release dT (fuel richness): {log_sensitivity(lambda x: delay_for(T0, dT=x), 1500.0):+.3f}")
    print(f"  pre-exponential A:               {log_sensitivity(lambda x: delay_for(T0, A=x), 2.5e9):+.3f}")
    print(f"  start temperature T0:            {log_sensitivity(lambda T: delay_for(T), 1000.0):+.2f}")
    for P in (1, 2, 5, 10, 20):
        print(f"  pressure {P:2d} atm (m = 1): delay {delay_at_pressure(T0, P) * 1e3:.4f} ms")

    print("\nSemenov: critical surrounding temperature for loss rate h")
    for h in (500.0, 1000.0):
        ca = critical_Ta_analytic(h)
        cn = critical_Ta_numeric(h, frozen=True)
        cb = critical_Ta_numeric(h, frozen=False)
        print(f"  h = {h:6.0f} /s  analytic {ca:.1f} K  simulated (fuel frozen) {cn:.1f} K  simulated (fuel burns) {cb:.1f} K")

    # figure 1: step counts
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.loglog([r[0] for r in rows], [r[1]["steps"] for r in rows], "o-", color="#d9534f", label="explicit RK4 (adaptive)")
    ax.loglog([r[0] for r in rows], [r[2]["steps"] for r in rows], "s-", color="#1f6feb", label="implicit trapezoid (adaptive)")
    ax.invert_xaxis()
    ax.set_xlabel("relative tolerance")
    ax.set_ylabel("accepted steps to reach 30 ms")
    ax.set_title("Steps needed to cover 30 ms of a 1 ms ignition")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "steps_vs_tolerance.png", dpi=120)

    # figure 2: failure of a coarse step
    from_c = np.linspace(1.0, 0.01, 4000)
    f = 1.0 / (rate_k(T0 + 1500 * (1 - from_c), p) * from_c)
    t_exact = np.concatenate([[0.0], np.cumsum(0.5 * (f[1:] + f[:-1]) * (from_c[:-1] - from_c[1:]))])
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(t_exact * 1e3, T0 + 1500 * (1 - from_c), color="k", lw=2, label="reference")
    for dt, col in ((1e-4, "#1f6feb"), (3e-4, "#d9534f")):
        ts, Ts = [0.0], [T0]
        y = np.array([T0, 1.0])
        t = 0.0
        while t < 2.5e-3 - 1e-12:
            y = rk4_step(y, dt, p)
            t += dt
            ts.append(t)
            Ts.append(y[0])
        ax2.plot(np.array(ts) * 1e3, np.clip(Ts, 0, 4000), "o-", ms=3, color=col, label=f"RK4, step {dt * 1e6:.0f} us")
    ax2.set_ylim(900, 4000)
    ax2.set_xlabel("time (ms)")
    ax2.set_ylabel("temperature (K)")
    ax2.set_title("Explicit RK4 with a coarse step: right delay, wrong afterwards")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "coarse_step_failure.png", dpi=120)

    T0B = np.arange(800.0, 1301.0, 50.0)
    tB = delay_table(T0B, **FUEL_B)
    bB, aB, r2B = fit_line(T0B, tB)
    print("\ntoy fuel B (A 1e7, Ea 110 kJ/mol, dT 1200 K):")
    for x, y in zip(T0B, tB):
        print(f"  T0 = {x:6.0f} K  delay = {y * 1e3:9.3f} ms")
    print(f"  fit: slope {bB:.3f}, R^2 {r2B:.5f}; temperature for 1 ms = {temperature_for_delay(T0B, tB, 1e-3):.1f} K")
    fig3, ax3 = plt.subplots(figsize=(6.4, 4.2))
    ax3.plot(1000 / T0B, np.log(tB), "o", color="#1f6feb", label="adaptive solver")
    xx = np.linspace(1000 / T0B.max(), 1000 / T0B.min(), 20)
    ax3.plot(xx, aB + bB * xx, "-", color="#d9534f", label=f"fit, slope {bB:.2f}")
    ax3.set_xlabel("1000 / T0  (1/K)")
    ax3.set_ylabel("ln( delay / 1 s )")
    ax3.set_title("Toy fuel B: ignition-delay law")
    ax3.grid(alpha=0.3)
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(OUT / "fuel_b_delay_law.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
