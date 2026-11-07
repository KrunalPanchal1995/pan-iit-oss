"""Session 3 (Level 3): simulate the real pendulum with RK4, validate it, drive it to resonance.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: when the formulas stop being enough
# **A. Real-world problem.** The formula T = 2 pi sqrt(L / g) is only a small-angle
# approximation, because the true restoring force on a pendulum is proportional to sin(theta),
# not theta. Push a swing high and it takes visibly longer per swing. There is no neat formula
# for the whole motion, so we *simulate* it step by step, and then we must prove the simulation
# can be trusted: compare it with exact results, check that energy is conserved, and watch
# what happens when the method is used badly. Finally we push the oscillator with a periodic
# force and find its resonance, where a small push makes a large swing.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81          # gravity, m/s^2


# %% [markdown]
# ## Step 1: the equation and the RK4 solver
# With angle theta (rad) and angular velocity omega (rad/s):
#
#     theta' = omega
#     omega' = -(g / L) sin(theta) - c * omega        c = damping rate (1/s)
#
# We advance by small steps of size dt. *Explicit Euler* uses only the slope at the start of
# the step. *Runge-Kutta 4* (RK4) takes four slopes (start, two middles, end) and combines
# them; its error shrinks like dt^4 instead of dt.

# %%
def pendulum_rhs(y, L, g=G, c=0.0):
    """Derivative of the state y = (theta, omega)."""
    return np.array([y[1], -(g / L) * np.sin(y[0]) - c * y[1]])


def rk4_step(f, y, dt):
    k1 = f(y)
    k2 = f(y + 0.5 * dt * k1)
    k3 = f(y + 0.5 * dt * k2)
    k4 = f(y + dt * k3)
    return y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def euler_step(f, y, dt):
    return y + dt * f(y)


def simulate_pendulum(theta0_deg, L=1.0, c=0.0, g=G, dt=0.005, t_end=10.0, method="rk4"):
    """Release from rest at theta0_deg. Returns t, theta (rad), omega (rad/s) arrays."""
    step = {"rk4": rk4_step, "euler": euler_step}[method]
    n = int(round(t_end / dt))
    t = np.arange(n + 1) * dt
    y = np.zeros((n + 1, 2))
    y[0] = [np.radians(theta0_deg), 0.0]
    f = lambda s: pendulum_rhs(s, L, g, c)
    for i in range(n):
        y[i + 1] = step(f, y[i], dt)
    return t, y[:, 0], y[:, 1]


def energy_per_mass(theta, omega, L=1.0, g=G):
    """Mechanical energy per kilogram (J/kg): 1/2 (L omega)^2 + g L (1 - cos theta)."""
    return 0.5 * (L * omega) ** 2 + g * L * (1 - np.cos(theta))


# %% [markdown]
# ## Step 2: measuring the period and the exact answer
# The simulated period is the gap between upward zero crossings (interpolated). The exact
# period of the undamped pendulum is T = T0 * (2 / pi) K(k), with k = sin(theta0 / 2) and K
# the complete elliptic integral. Using the arithmetic-geometric mean (AGM) this simplifies
# to T = T0 / AGM(1, cos(theta0 / 2)), easy to compute with a short loop. A series gives
# T = T0 (1 + theta0^2 / 16 + 11 theta0^4 / 3072 + ...).

# %%
def measure_period(t, x):
    """Average gap (s) between upward zero crossings of x(t); nan if fewer than two."""
    idx = np.where((x[:-1] < 0) & (x[1:] >= 0))[0]
    if len(idx) < 2:
        return float("nan")
    tc = t[idx] - x[idx] * (t[idx + 1] - t[idx]) / (x[idx + 1] - x[idx])
    return float(np.mean(np.diff(tc)))


def small_angle_period(L=1.0, g=G):
    return float(2 * np.pi * np.sqrt(L / g))


def agm(a, b, tol=1e-15):
    """Arithmetic-geometric mean of a and b."""
    a, b = float(a), float(b)
    while abs(a - b) > tol:
        a, b = 0.5 * (a + b), np.sqrt(a * b)
    return a


def exact_period(theta0_deg, L=1.0, g=G):
    """Exact period (s) of the undamped pendulum released from rest at theta0 (degrees, below 180)."""
    if not 0 <= theta0_deg < 180:
        raise ValueError("amplitude must be from 0 up to (not including) 180 degrees")
    return small_angle_period(L, g) / agm(1.0, np.cos(np.radians(theta0_deg) / 2))


def series_period(theta0_deg, L=1.0, g=G, terms=2):
    """Series T0 (1 + th^2/16 + 11 th^4/3072), using 1 or 2 correction terms."""
    th = np.radians(theta0_deg)
    corr = th ** 2 / 16 + (11 * th ** 4 / 3072 if terms >= 2 else 0.0)
    return small_angle_period(L, g) * (1 + corr)


def small_angle_error(theta0_deg):
    """Relative error of the small-angle formula, (T_exact - T0) / T_exact."""
    T = exact_period(theta0_deg)
    return (T - small_angle_period()) / T


def angle_for_error(tol=0.05):
    """Amplitude (degrees) at which the small-angle formula is off by the fraction tol (bisection)."""
    lo, hi = 1.0, 120.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if small_angle_error(mid) < tol:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# %% [markdown]
# ## Step 3: three validation tests
# 1. **Analytic limit.** For a tiny swing, sin(theta) is about theta, so the simulation must
#    match theta0 cos(w t).
# 2. **Energy conservation.** With c = 0 the energy must stay constant.
# 3. **Damped envelope.** With c > 0 and a small swing, successive maxima shrink by the
#    factor exp(-c * Td / 2) per swing, where Td is the damped period.

# %%
def small_angle_solution(t, theta0_deg, L=1.0, g=G):
    return np.radians(theta0_deg) * np.cos(np.sqrt(g / L) * t)


def peaks(t, y):
    """Times and values of local maxima of y(t), refined by a parabola through three points."""
    i = np.where((y[1:-1] > y[:-2]) & (y[1:-1] >= y[2:]))[0] + 1
    a, b, c = y[i - 1], y[i], y[i + 1]
    d = a - 2 * b + c
    off = 0.5 * (a - c) / d
    dt = t[1] - t[0]
    return t[i] + off * dt, b - 0.25 * (a - c) * off


def energy_drift(theta0_deg, dt, method, t_end=20.0, L=1.0):
    """Relative change in energy between the start and the end of the run."""
    t, th, om = simulate_pendulum(theta0_deg, L=L, dt=dt, t_end=t_end, method=method)
    e = energy_per_mass(th, om, L)
    return float((e[-1] - e[0]) / e[0])


# %% [markdown]
# ## Step 4: a driven oscillator and resonance
# Add a push F cos(Omega t) (force per kilogram, m/s^2) to the linear oscillator
#
#     x'' + 2 zeta w0 x' + w0^2 x = F cos(Omega t)
#
# After the start-up wobble dies away, x oscillates at the driving frequency with amplitude
#
#     A(Omega) = F / sqrt((w0^2 - Omega^2)^2 + (2 zeta w0 Omega)^2)
#
# which peaks near Omega = w0. The sharpness of the peak is the quality factor Q = 1 / (2 zeta)
# (about w0 divided by the width of the peak at 1/sqrt(2) of its height).

# %%
def driven_amplitude_exact(Omega, w0, zeta, F=1.0):
    Omega = np.asarray(Omega, float)
    return F / np.sqrt((w0 ** 2 - Omega ** 2) ** 2 + (2 * zeta * w0 * Omega) ** 2)


def driven_amplitude_simulated(Omega, w0, zeta, F=1.0, dt=0.005, t_end=70.0, window=4.0):
    """Steady amplitude for each driving frequency, from an RK4 simulation of all of them at once."""
    Omega = np.asarray(Omega, float)
    n = int(round(t_end / dt))
    y = np.zeros((len(Omega), 2))

    def f(s, tt):
        return np.stack([s[:, 1], F * np.cos(Omega * tt) - 2 * zeta * w0 * s[:, 1] - w0 ** 2 * s[:, 0]], axis=1)

    amp = np.zeros(len(Omega))
    for i in range(n):
        tt = i * dt
        k1 = f(y, tt)
        k2 = f(y + 0.5 * dt * k1, tt + 0.5 * dt)
        k3 = f(y + 0.5 * dt * k2, tt + 0.5 * dt)
        k4 = f(y + dt * k3, tt + dt)
        y = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        if tt >= t_end - window:
            amp = np.maximum(amp, np.abs(y[:, 0]))
    return amp


def q_from_curve(Omega, amp):
    """Quality factor from a measured curve: peak frequency divided by the width at peak/sqrt(2)."""
    i = int(np.argmax(amp))
    level = amp[i] / np.sqrt(2)
    j = i
    while j > 0 and amp[j] > level:
        j -= 1
    k = i
    while k < len(amp) - 1 and amp[k] > level:
        k += 1
    lo = Omega[j] + (level - amp[j]) * (Omega[j + 1] - Omega[j]) / (amp[j + 1] - amp[j])
    hi = Omega[k - 1] + (amp[k - 1] - level) * (Omega[k] - Omega[k - 1]) / (amp[k - 1] - amp[k])
    return float(Omega[i] / (hi - lo))


# %% [markdown]
# ## Step 5: a failure case, and the mini-project helper
# Explicit Euler adds a little energy at every step: for a linear oscillator the energy is
# multiplied by (1 + (w dt)^2) each step. Small steps hide it, large steps explode.
#
# For the mini-project you tune a spring so that a phone on a spring bounces at a target
# frequency. The helper below chooses the best of a list of stock springs. The spring itself
# has mass, and one third of it moves with the load, so the moving mass is m + m_spring / 3.

# %%
def euler_growth_factor(w, dt, steps):
    """Predicted energy growth of explicit Euler for a linear oscillator."""
    return float((1 + (w * dt) ** 2) ** steps)


def damped_frequency_hz(m, k, b):
    """Damped oscillation frequency (Hz) of mass m (kg), stiffness k (N/m), damping b (kg/s)."""
    d = k / m - (b / (2 * m)) ** 2
    return float(np.sqrt(d) / (2 * np.pi)) if d > 0 else 0.0


def tune_spring(m_load, m_spring, f_target, springs, b=0.0):
    """Return (best_k, table); table rows are (k, f in Hz). Moving mass = m_load + m_spring / 3."""
    m_eff = m_load + m_spring / 3.0
    table = [(k, damped_frequency_hz(m_eff, k, b)) for k in springs]
    best = min(table, key=lambda row: abs(row[1] - f_target))
    return best[0], table


def ballast_for_target(k, m_load, m_spring, f_target, b=0.0):
    """Extra mass (kg) to add to the load so the damped frequency equals f_target (Hz).

    Solves (2 pi f)^2 = k / m - (b / 2m)^2 for the moving mass m, taking the larger root.
    """
    w2 = (2 * np.pi * f_target) ** 2
    disc = k ** 2 - w2 * b ** 2
    if disc < 0:
        raise ValueError("this spring and damping cannot reach that frequency")
    m_needed = (k + np.sqrt(disc)) / (2 * w2)
    return float(m_needed - m_load - m_spring / 3.0)


def simulate_spring_mass(m, k, b, x0=0.02, dt=0.002, t_end=10.0):
    """RK4 run of m x'' + b x' + k x = 0 from rest at x0 (m). Returns t, x, v."""
    n = int(round(t_end / dt))
    t = np.arange(n + 1) * dt
    y = np.zeros((n + 1, 2))
    y[0] = [x0, 0.0]
    f = lambda s: np.array([s[1], -(k * s[0] + b * s[1]) / m])
    for i in range(n):
        y[i + 1] = rk4_step(f, y[i], dt)
    return t, y[:, 0], y[:, 1]


# %% [markdown]
# ## Step 6: run everything

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    T0 = small_angle_period()
    print(f"T0 (small-angle, L = 1 m) = {T0:.4f} s")
    print("amplitude  T_rk4    T_exact  T_series  small-angle error")
    amps = [5, 10, 20, 30, 40, 60, 90, 120]
    rows = []
    for a in amps:
        t, th, om = simulate_pendulum(a, dt=0.002, t_end=40.0)
        Tm = measure_period(t, th)
        rows.append((a, Tm, exact_period(a), series_period(a), small_angle_error(a)))
        print(f"{a:6d} deg {Tm:.4f}  {exact_period(a):.4f}  {series_period(a):.4f}   {100 * small_angle_error(a):.2f} %")
    a5 = angle_for_error(0.05)
    print(f"the small-angle formula is 1 percent low at theta0 = {angle_for_error(0.01):.2f} degrees")
    print(f"the small-angle formula is 5 percent low at theta0 = {a5:.2f} degrees (exact T = {exact_period(a5):.4f} s)")

    t, th, om = simulate_pendulum(0.5, dt=0.005, t_end=10.0)
    err = np.max(np.abs(th - small_angle_solution(t, 0.5)))
    print(f"0.5 degree swing: largest difference from the analytic cosine = {err:.2e} rad (amplitude {np.radians(0.5):.4f} rad)")
    for dt in (0.05, 0.02, 0.005):
        print(f"energy drift over 20 s, 60 degrees, dt = {dt}: RK4 {energy_drift(60, dt, 'rk4'):+.2e}, Euler {energy_drift(60, dt, 'euler'):+.2e}")
    c = 0.4
    t, th, om = simulate_pendulum(3.0, c=c, dt=0.005, t_end=20.0)
    tp, vp = peaks(t, th)
    wd = np.sqrt(G - (c / 2) ** 2)
    print(f"damped c = {c}: measured peak ratio {vp[1] / vp[0]:.4f}, predicted exp(-c Td/2) = {np.exp(-c / 2 * 2 * np.pi / wd):.4f}")

    w0, zeta = 2 * np.pi, 0.05
    Om = np.linspace(0.5, 1.5, 201) * w0
    sim = driven_amplitude_simulated(Om, w0, zeta)
    ex = driven_amplitude_exact(Om, w0, zeta)
    print(f"resonance: max |simulated - exact| = {np.max(np.abs(sim - ex)):.2e} m; peak {sim.max():.4f} m vs static {1 / w0 ** 2:.4f} m")
    print(f"Q: peak/static = {sim.max() * w0 ** 2:.2f}, 1/(2 zeta) = {1 / (2 * zeta):.2f}, half-power width = {q_from_curve(Om, sim):.2f}")
    print(f"Euler, dt = 0.05, 10 periods: predicted energy growth x{euler_growth_factor(np.sqrt(G), 0.05, int(10 * T0 / 0.05)):.0f}")
    best, table = tune_spring(0.17, 0.03, 2.0, [10, 15, 20, 25, 30, 40, 60], b=0.2)
    print("spring table (N/m, Hz):", [(k, round(f, 3)) for k, f in table], "-> choose", best)
    ball = ballast_for_target(best, 0.17, 0.03, 2.0, b=0.2)
    mm = 0.17 + 0.03 / 3 + ball
    ts, xs, vs = simulate_spring_mass(mm, best, 0.2)
    print(f"ballast {1000 * ball:.2f} g -> moving mass {mm:.4f} kg; simulated frequency {1 / measure_period(ts, xs):.4f} Hz (target 2.0)")

    fig, ax = plt.subplots(figsize=(6.5, 4))
    aa = np.linspace(1, 150, 150)
    ax.plot(aa, [exact_period(a) / T0 for a in aa], label="exact (elliptic / AGM)")
    ax.plot(aa, [series_period(a) / T0 for a in aa], "--", label="series 1 + th^2/16 + 11 th^4/3072")
    ax.plot([r[0] for r in rows], [r[1] / T0 for r in rows], "o", label="RK4 simulation")
    ax.axhline(1, color="gray", lw=0.8, label="small-angle formula")
    ax.axvline(a5, color="C3", ls=":", label=f"5 percent error at {a5:.1f} degrees")
    ax.set_ylim(0.95, 2.1)
    ax.set_xlabel("amplitude theta0 (degrees)")
    ax.set_ylabel("period / small-angle period T0")
    ax.set_title("A bigger swing takes longer")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "period_vs_amplitude.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    ax2.plot(Om / w0, ex * w0 ** 2, label="formula A(Omega)")
    ax2.plot(Om[::6] / w0, sim[::6] * w0 ** 2, "o", ms=4, label="RK4 simulation")
    ax2.set_xlabel("driving frequency / natural frequency (Omega / w0)")
    ax2.set_ylabel("amplitude / static displacement")
    ax2.set_title("Resonance curve, zeta = 0.05 (Q = 10)")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "resonance_curve.png", dpi=120)

    t, th, om = simulate_pendulum(60, dt=0.02, t_end=40.0, method="euler")
    t2, th2, om2 = simulate_pendulum(60, dt=0.02, t_end=40.0, method="rk4")
    fig3, ax3 = plt.subplots(figsize=(6.5, 4))
    ax3.plot(t2, energy_per_mass(th2, om2), label="RK4, dt = 0.02 s")
    ax3.plot(t, energy_per_mass(th, om), label="explicit Euler, dt = 0.02 s")
    ax3.set_xlabel("time (s)")
    ax3.set_ylabel("energy per kilogram (J/kg)")
    ax3.set_title("Failure case: Euler gains energy")
    ax3.grid(alpha=0.3)
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(OUT / "euler_failure.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
