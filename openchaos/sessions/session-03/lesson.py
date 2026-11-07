"""Session 3 (Level 3): integrators, the Lyapunov exponent, a flip-time map and the limits of forecasting.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: measuring chaos and knowing when to stop trusting a forecast
# **A. Real-world problem.** Weather models, orbit predictions and robot arms all meet the same
# wall: a tiny error in the starting measurement grows until the forecast is useless. The double
# pendulum shows it in a table-top system. Today we (1) compare two solvers, (2) measure the
# growth rate of a tiny error (the *Lyapunov exponent*), (3) map which starts are regular and
# which are chaotic, and (4) compute how long a forecast can be trusted.
#
# All motion here is for equal balls (1 kg) and equal 1 m rods, started at rest unless stated.
# Chaos is a property of the *motion*, not of the system: the exponent depends on the start.

# %%
import math
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81                 # gravity, m/s^2
E_REF = 3 * G            # energy scale (m1 + m2) g l1 + m2 g l2 = 2 g + g = 29.43 J


# %% [markdown]
# ## Step 1: the equations, written once for numbers and for whole arrays
# These are the Session 2 equations for equal masses and rods. The same function works for a
# single start (Python numbers, fast) and for thousands of starts at once (NumPy arrays).

# %%
def rate(state):
    """(theta1', theta2', omega1', omega2') for state (theta1, theta2, omega1, omega2)."""
    t1, t2, w1, w2 = state
    m = np if isinstance(t1, np.ndarray) else math
    d = t1 - t2
    den = 3.0 - m.cos(2 * d)
    a1 = (-3 * G * m.sin(t1) - G * m.sin(t1 - 2 * t2) - 2 * m.sin(d) * (w2 ** 2 + w1 ** 2 * m.cos(d))) / den
    a2 = (2 * m.sin(d) * (2 * w1 ** 2 + 2 * G * m.cos(t1) + w2 ** 2 * m.cos(d))) / den
    return (w1, w2, a1, a2)


def energy(state):
    """Total energy E = T + V in joules (pivot is the zero of height)."""
    t1, t2, w1, w2 = state
    m = np if isinstance(t1, np.ndarray) else math
    return w1 ** 2 + 0.5 * w2 ** 2 + w1 * w2 * m.cos(t1 - t2) - 2 * G * m.cos(t1) - G * m.cos(t2)


def rk4_step(state, h):
    """Runge-Kutta 4: four slopes per step, error per unit time about h^4."""
    def shift(s, k, f):
        return tuple(a + f * b for a, b in zip(s, k))
    k1 = rate(state)
    k2 = rate(shift(state, k1, h / 2))
    k3 = rate(shift(state, k2, h / 2))
    k4 = rate(shift(state, k3, h))
    return tuple(a + h / 6 * (b + 2 * c + 2 * d + e) for a, b, c, d, e in zip(state, k1, k2, k3, k4))


def simulate(state0, duration, h, step=rk4_step):
    """States (one row per time step) from time 0 to duration."""
    n = int(round(duration / h))
    s = tuple(float(v) for v in state0)
    out = np.empty((n + 1, 4))
    out[0] = s
    for i in range(n):
        s = step(s, h)
        out[i + 1] = s
    return np.arange(n + 1) * h, out


def release(a_deg):
    a = math.radians(a_deg)
    return (a, a, 0.0, 0.0)


# %% [markdown]
# ## Step 2: a symplectic solver (implicit midpoint)
# RK4 is very accurate for a short time, but it slowly leaks energy. A *symplectic* method is built
# so that the energy error stays bounded however long you run. We use the implicit midpoint rule
# on the Hamiltonian form: positions q = (theta1, theta2), momenta p = M(q) * omega with
# M = [[2, cos d], [cos d, 1]] (kg m^2), and
#
#     q' = M^-1 p,    p1' = -w1 w2 sin d - 2 g sin(theta1),    p2' = +w1 w2 sin d - g sin(theta2).
#
# The midpoint rule solves z_new = z + h F((z + z_new)/2) by repeating the substitution a few times.

# %%
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
    q1, q2, p1, p2 = z
    w1, w2 = _to_rates(z)[2:]
    sd = math.sin(q1 - q2)
    return (w1, w2, -w1 * w2 * sd - 2 * G * math.sin(q1), w1 * w2 * sd - G * math.sin(q2))


def midpoint_step(state, h, tol=1e-14, max_iter=60):
    """One implicit-midpoint step (symplectic) for the double pendulum; state in (theta, omega) form."""
    z = _to_momenta(state)
    y = tuple(a + h * b for a, b in zip(z, _hamilton_rate(z)))
    for _ in range(max_iter):
        mid = tuple((a + b) / 2 for a, b in zip(z, y))
        y_new = tuple(a + h * b for a, b in zip(z, _hamilton_rate(mid)))
        change = max(abs(a - b) for a, b in zip(y, y_new))
        y = y_new
        if change < tol:
            break
    return _to_rates(y)


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


# %% [markdown]
# ## Step 3: sensitivity and the Lyapunov exponent
# Start two copies `delta0 = 1e-8` rad apart in theta1 and track the phase-space distance
# d(t) = sqrt of the sum of squares of the four differences. While d is small,
#
#     d(t) is about d0 * exp(lambda * t),   so   ln d(t) = ln d0 + lambda * t,
#
# a straight line whose slope is the largest Lyapunov exponent lambda (units 1/s). The line stops
# when d reaches the size of the whole motion (saturation), so we fit only between d = 1e-6 and 1e-2.
# A second method (Benettin) keeps the pair close by shrinking their gap back to d0 every 0.1 s and
# averages the logarithm of the growth; it needs no fit window. Both give lambda *for that start only*.

# %%
def separation_curve(state0, duration=30.0, h=0.01, delta0=1e-8, stride=10):
    """Times and phase-space distance between a run and its twin shifted by delta0 in theta1."""
    twin = (state0[0] + delta0,) + tuple(state0[1:])
    _, a = simulate(state0, duration, h)
    _, b = simulate(twin, duration, h)
    d = np.linalg.norm(a - b, axis=1)
    t = np.arange(len(d)) * h
    return t[::stride], d[::stride]


def fit_exponent(t, d, lo=1e-6, hi=1e-2):
    """Slope of ln d against t between the first time d > lo and the first time d > hi.
    Returns (lambda in 1/s, intercept, window start, window end)."""
    i0 = int(np.argmax(d > lo))
    i1 = int(np.argmax(d > hi))
    slope, intercept = np.polyfit(t[i0:i1 + 1], np.log(d[i0:i1 + 1]), 1)
    return float(slope), float(intercept), float(t[i0]), float(t[i1])


def benettin(starts, duration=60.0, h=0.01, delta0=1e-8, every=10):
    """Largest Lyapunov exponent (1/s) for each start in `starts` (array of shape (N, 4))."""
    s = np.asarray(starts, dtype=float)
    a = tuple(s[:, k].copy() for k in range(4))
    b = (a[0] + delta0,) + a[1:]
    total = np.zeros(len(s))
    for i in range(1, int(round(duration / h)) + 1):
        a = rk4_step(a, h)
        b = rk4_step(b, h)
        if i % every == 0:
            gap = np.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
            total += np.log(gap / delta0)
            b = tuple(x + (y - x) * (delta0 / gap) for x, y in zip(a, b))
    return total / duration


def rest_start_with_energy(th1_deg, energy_j):
    """Rest start with the given upper angle and total energy E = -2 g cos(th1) - g cos(th2).
    Returns None if no real angle exists."""
    c = (-energy_j - 2 * G * math.cos(math.radians(th1_deg))) / G
    if abs(c) > 1:
        return None
    return (math.radians(th1_deg), math.acos(c), 0.0, 0.0)


# %% [markdown]
# ## Step 4: the flip-time map
# Release the double pendulum from rest at (theta1, theta2). Record the time until the outer rod
# first swings over the top (|theta2| passes pi); give up after 10 s. Colour each start by that time.
# Dark = never flips (regular, low energy); stripes and speckle = chaos.
# *Validation by energy*: the kinetic energy is never negative, so the outer rod can only reach the top
# if E >= -g, i.e. the start must NOT satisfy 2 cos(theta1) + cos(theta2) > 1. Every start in that region
# must show "no flip".

# %%
def flip_time_map(n=80, duration=10.0, h=0.02):
    """Grid of n x n rest starts, theta1 and theta2 in (-pi, pi). Returns (angles, flip_times)
    with flip_times[j, i] for theta1 = angles[i], theta2 = angles[j]; value `duration` means no flip."""
    ang = (np.arange(n) + 0.5) / n * 2 * np.pi - np.pi
    t1, t2 = np.meshgrid(ang, ang)
    state = (t1.ravel(), t2.ravel(), np.zeros(n * n), np.zeros(n * n))
    first = np.full(n * n, duration)
    done = np.zeros(n * n, dtype=bool)
    for i in range(1, int(round(duration / h)) + 1):
        state = rk4_step(state, h)
        flipped = (np.abs(state[1]) > np.pi) & ~done
        first[flipped] = i * h
        done |= flipped
    return ang, first.reshape(n, n)


def cannot_flip(theta1, theta2):
    """True where energy alone forbids the outer rod from reaching the top (rest starts)."""
    return 2 * np.cos(theta1) + np.cos(theta2) > 1.0


# %% [markdown]
# ## Step 5: the linear limit, and a failure case
# Tiny swings must match the two normal modes (w = 2.397 and 5.787 rad/s). And a time step that is too
# big gives a wrong answer even before chaos amplifies anything.

# %%
OMEGA_MODES = (math.sqrt(G * (2 - math.sqrt(2))), math.sqrt(G * (2 + math.sqrt(2))))   # rad/s, by hand


def small_angle_error(mode, amp=1e-3, duration=3.0, h=0.002):
    """Largest difference (rad) between the full simulation and the exact linear mode, for a start
    at rest with amplitude amp (rad). mode 0 swings with theta2 = +sqrt 2 theta1; mode 1 with -sqrt 2."""
    shape = (1.0, (1, -1)[mode] * math.sqrt(2))
    start = (amp * shape[0], amp * shape[1], 0.0, 0.0)
    t, s = simulate(start, duration, h)
    w = OMEGA_MODES[mode]
    exact = amp * np.outer(np.cos(w * t), shape)
    return float(np.max(np.abs(s[:, :2] - exact)))


def departure_time(state0, h_test, h_ref=0.001, duration=30.0, tol=0.1):
    """First time (s) at which the angles from a run with step h_test differ from a fine reference
    run (step h_ref) by more than tol rad; None if never within `duration`."""
    t, a = simulate(state0, duration, h_ref)
    ratio = int(round(h_test / h_ref))
    _, b = simulate(state0, duration, h_test)
    diff = np.max(np.abs(a[::ratio, :2] - b[:, :2]), axis=1)
    idx = np.where(diff > tol)[0]
    return round(float(idx[0] * h_test), 4) if len(idx) else None


# %% [markdown]
# ## Step 6: the predictability horizon
# If the start is known to within delta0 and we accept an error up to Delta, the forecast is
# trustworthy until d(t) = d0 exp(lambda t) reaches Delta, that is
#
#     t_horizon = ln(Delta / delta0) / lambda.
#
# Making the measurement 1000 times better adds only ln(1000) / lambda, about 5 s here. That slow gain
# is why long-range chaotic forecasts do not become possible just by buying better instruments.

# %%
def predicted_horizon(delta0, big_delta, lam):
    return math.log(big_delta / delta0) / lam


def forecast_horizon(state0, err_vec, tol=0.1, duration=40.0, h=0.005):
    """First time (s) at which a forecast started from state0 + err_vec differs from the true run by more than
    tol rad in either angle; None if it stays within tol for the whole `duration`."""
    wrong = tuple(a + e for a, e in zip(state0, err_vec))
    t, a = simulate(state0, duration, h)
    _, b = simulate(wrong, duration, h)
    diff = np.max(np.abs(a[:, :2] - b[:, :2]), axis=1)
    idx = np.where(diff > tol)[0]
    return float(t[idx[0]]) if len(idx) else None


def median_horizon(state0, err, n_dirs=20, seed=7, tol=0.1, duration=40.0, h=0.01):
    """Median forecast horizon (s) over n_dirs random directions of a measurement error whose total size
    (4 numbers together) is err. Returns None if some run never leaves the tolerance."""
    rng = np.random.default_rng(seed)
    times = []
    for _ in range(n_dirs):
        v = rng.normal(size=4)
        v *= err / np.linalg.norm(v)
        times.append(forecast_horizon(state0, tuple(v), tol, duration, h))
    return None if any(x is None for x in times) else float(np.median(times))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    s0 = release(120.0)

    # --- solvers: energy drift over 500 s
    t_rk, d_rk = drift_curve(rk4_step, s0, 500.0, 0.01)
    t_mp, d_mp = drift_curve(midpoint_step, s0, 500.0, 0.01)
    print(f"h = 0.01 s over 500 s: RK4 worst energy error {np.abs(d_rk).max():.1e}, midpoint {np.abs(d_mp).max():.1e}")
    print(f"   after 50 s: RK4 {np.abs(d_rk[t_rk <= 50]).max():.1e}, midpoint {np.abs(d_mp[t_mp <= 50]).max():.1e}")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(t_rk, d_rk, label="RK4 (leaks energy steadily)")
    ax.plot(t_mp, d_mp, label="implicit midpoint (bounded)")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("relative energy error (E - E0) / E_ref")
    ax.set_title("Two solvers, same step h = 0.01 s, chaotic start")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "solver_energy.png", dpi=120)

    # --- separation growth and the fit
    t, d = separation_curve(s0)
    lam_fit, icpt, tw0, tw1 = fit_exponent(t, d)
    lam_ben = float(benettin(np.array([s0]))[0])
    print(f"start 120 deg: fitted lambda = {lam_fit:.2f} /s (window {tw0:.1f} to {tw1:.1f} s); Benettin lambda = {lam_ben:.2f} /s")
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.semilogy(t, d, label="distance between the twins")
    tt = np.array([tw0, tw1])
    ax2.semilogy(tt, np.exp(icpt + lam_fit * tt), "r-", lw=3, alpha=0.7, label=f"fit: slope lambda = {lam_fit:.2f} /s")
    ax2.axhline(1e-8, color="gray", ls=":", label="starting gap 1e-8")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("phase-space distance d(t)")
    ax2.set_title("ln d grows as a straight line, then saturates")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "lyapunov_fit.png", dpi=120)

    # --- lambda versus energy (rest starts at theta1 = theta2 = a) and spread at one energy
    angles = np.arange(20, 180, 20)
    lam_a = benettin(np.array([release(a) for a in angles]))
    e_a = np.array([energy(release(a)) for a in angles])
    e_same = energy(release(145.0))
    same = [rest_start_with_energy(a, e_same) for a in (140, 150, 160, 170)]
    same = [x for x in same if x is not None]
    lam_same = benettin(np.array(same))
    for a, e, l in zip(angles, e_a, lam_a):
        print(f"  release {a:3d} deg: E = {e:7.2f} J   lambda = {l:5.2f} /s")
    print(f"same energy E = {e_same:.2f} J, different starts: lambda =", np.round(lam_same, 2), "(release 145 deg:", round(float(benettin(np.array([release(145.0)]))[0]), 2), ")")
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    ax3.plot(e_a, lam_a, "o-", label="rest starts, both rods at the same angle")
    ax3.plot([e_same] * len(lam_same), lam_same, "rs", label="other starts with the same energy as 145 degrees")
    ax3.set_xlabel("total energy E (J)")
    ax3.set_ylabel("estimated lambda (1/s)")
    ax3.set_title("lambda depends on the start, not just on the energy")
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "lambda_vs_energy.png", dpi=120)

    # --- flip-time map
    ang, ft = flip_time_map()
    deg = np.degrees(ang)
    fig4, ax4 = plt.subplots(figsize=(6, 5.2))
    im = ax4.imshow(ft, origin="lower", extent=[deg[0], deg[-1], deg[0], deg[-1]], cmap="magma", vmin=0, vmax=10)
    g1, g2 = np.meshgrid(ang, ang)
    ax4.contour(deg, deg, cannot_flip(g1, g2).astype(float), levels=[0.5], colors="cyan", linewidths=1)
    ax4.set_xlabel("start angle theta1 (degrees)")
    ax4.set_ylabel("start angle theta2 (degrees)")
    ax4.set_title("Flip-time map (cyan: energy forbids a flip)")
    fig4.colorbar(im, label="time to first flip (s); 10 = none")
    fig4.tight_layout()
    fig4.savefig(OUT / "flip_time_map.png", dpi=120)
    inside = cannot_flip(g1, g2)
    print(f"map: {np.mean(ft >= 10):.1%} of starts never flip in 10 s; flips inside the forbidden region: {int(np.sum(ft[inside] < 10))}")

    # --- validation and failure
    print("small-angle errors (rad):", [f"{small_angle_error(k):.1e}" for k in (0, 1)])
    for h in (0.1, 0.05, 0.02, 0.01, 0.005):
        print(f"  step {h:5.3f} s: departs from the fine reference after {departure_time(s0, h)} s")

    # --- predictability horizon
    lam = lam_ben
    print(f"predicted horizon for err 1e-6, tol 0.1: {predicted_horizon(1e-6, 0.1, lam):.1f} s")
    print("measured (error 1e-6 in theta1):", forecast_horizon(s0, (1e-6, 0, 0, 0)), "s")
    for a in (100, 120, 140):
        st = release(a)
        lam_a_ = float(benettin(np.array([st]), duration=40.0)[0])
        print(f"  release {a} deg: lambda {lam_a_:.2f} /s, predicted {predicted_horizon(1e-6, 0.1, lam_a_):.1f} s, "
              f"median measured {median_horizon(st, 1e-6, n_dirs=10, duration=30.0):.2f} s")
    print(f"  release 120 deg with a 1000 times better measurement (1e-9): median {median_horizon(release(120.0), 1e-9, n_dirs=10, duration=40.0):.2f} s")

    # Figure 5: the two forecasts drifting apart (error 1e-6)
    wrong = (s0[0] + 1e-6,) + s0[1:]
    tf, a_run = simulate(s0, 25.0, 0.01)
    _, b_run = simulate(wrong, 25.0, 0.01)
    fig5, ax5 = plt.subplots(figsize=(7, 4))
    ax5.plot(tf, a_run[:, 1], label="true motion (theta2)")
    ax5.plot(tf, b_run[:, 1], "--", label="forecast from a start 1e-6 rad off")
    hz = forecast_horizon(s0, (1e-6, 0, 0, 0))
    ax5.axvline(hz, color="red", ls=":", label=f"forecast off by 0.1 rad at {hz:.1f} s")
    ax5.set_xlabel("time (s)")
    ax5.set_ylabel("outer rod angle theta2 (rad)")
    ax5.set_title("A forecast is good until the horizon, then useless")
    ax5.grid(alpha=0.3)
    ax5.legend(fontsize=8)
    fig5.tight_layout()
    fig5.savefig(OUT / "forecast_horizon.png", dpi=120)

# %% [markdown]
# ## Where this stops
# We estimated one exponent from one pair of paths and one map at one resolution. The Target (see
# `promo/roadmap.md`) goes further: it shows the divergence live and in 2D. The honest limit: beyond about
# t_horizon the simulation shows a possible motion, not the real one.
