"""Session 2 (Level 2): the equations of motion, energy, and how to check a simulation.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: equations, energy and a trustworthy simulation
# **A. Real-world problem.** Before you believe a simulation you must be able to check it. For a
# double pendulum we cannot write the motion as a formula, but we know two things for sure:
# the total energy (movement plus height) must stay constant, and for tiny swings the motion
# must reduce to two simple back-and-forth patterns with frequencies we can calculate by hand.
# Today we write the equations, build both checks, and use them to choose a time step.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81                                  # gravity, m/s^2
EQUAL = dict(m1=1.0, m2=1.0, l1=1.0, l2=1.0)   # masses in kg, rod lengths in m


# %% [markdown]
# ## Step 1: the equations of motion
# The angles `th1`, `th2` are measured from straight down. With masses m1, m2 and lengths l1, l2
# the Lagrangian method gives (d = th1 - th2, w = angular speed in rad/s):
#
#     den = 2 m1 + m2 - m2 cos(2d)
#     th1'' = [ -g (2 m1 + m2) sin th1 - m2 g sin(th1 - 2 th2) - 2 sin d m2 (w2^2 l2 + w1^2 l1 cos d) ] / (l1 den)
#     th2'' = [ 2 sin d ( w1^2 l1 (m1 + m2) + g (m1 + m2) cos th1 + w2^2 l2 m2 cos d ) ] / (l2 den)
#
# Units: rad/s^2. We check them in two independent ways. First, a second form of the same
# equations written as a matrix problem, M(th) * (th1'', th2'') = force terms, solved with
# `numpy.linalg.solve`. Second, energy conservation below.

# %%
def accel(state, m1=1.0, m2=1.0, l1=1.0, l2=1.0, g=G):
    """Angular accelerations (rad/s^2) from the closed-form equations."""
    t1, t2, w1, w2 = state
    d = t1 - t2
    den = 2 * m1 + m2 - m2 * np.cos(2 * d)
    a1 = (-g * (2 * m1 + m2) * np.sin(t1) - m2 * g * np.sin(t1 - 2 * t2)
          - 2 * np.sin(d) * m2 * (w2 ** 2 * l2 + w1 ** 2 * l1 * np.cos(d))) / (l1 * den)
    a2 = (2 * np.sin(d) * (w1 ** 2 * l1 * (m1 + m2) + g * (m1 + m2) * np.cos(t1)
                           + w2 ** 2 * l2 * m2 * np.cos(d))) / (l2 * den)
    return a1, a2


def accel_matrix(state, m1=1.0, m2=1.0, l1=1.0, l2=1.0, g=G):
    """The same accelerations from the mass-matrix form (a different route to the same answer)."""
    t1, t2, w1, w2 = state
    d = t1 - t2
    M = np.array([[(m1 + m2) * l1 ** 2, m2 * l1 * l2 * np.cos(d)],
                  [m2 * l1 * l2 * np.cos(d), m2 * l2 ** 2]])
    rhs = np.array([-m2 * l1 * l2 * np.sin(d) * w2 ** 2 - (m1 + m2) * g * l1 * np.sin(t1),
                    m2 * l1 * l2 * np.sin(d) * w1 ** 2 - m2 * g * l2 * np.sin(t2)])
    return tuple(np.linalg.solve(M, rhs))


def rate(state, **p):
    a1, a2 = accel(state, **p)
    return np.array([state[2], state[3], a1, a2])


# %% [markdown]
# ## Step 2: energy, the first check
# Kinetic energy T (movement) and potential energy V (height), in joules, zero of height at the pivot:
#
#     T = 1/2 (m1 + m2) l1^2 w1^2 + 1/2 m2 l2^2 w2^2 + m2 l1 l2 w1 w2 cos(th1 - th2)
#     V = -(m1 + m2) g l1 cos th1 - m2 g l2 cos th2
#
# There is no friction, so E = T + V must stay constant. A simulation that lets E wander is wrong.
# We measure the *relative energy drift* = max |E(t) - E(0)| / E_ref, with the energy scale
# E_ref = (m1 + m2) g l1 + m2 g l2 (the height energy of the whole system, always above zero).

# %%
def energy(state, m1=1.0, m2=1.0, l1=1.0, l2=1.0, g=G):
    t1, t2, w1, w2 = state
    kinetic = (0.5 * (m1 + m2) * l1 ** 2 * w1 ** 2 + 0.5 * m2 * l2 ** 2 * w2 ** 2
               + m2 * l1 * l2 * w1 * w2 * np.cos(t1 - t2))
    potential = -(m1 + m2) * g * l1 * np.cos(t1) - m2 * g * l2 * np.cos(t2)
    return kinetic + potential


def energy_scale(m1=1.0, m2=1.0, l1=1.0, l2=1.0, g=G):
    return (m1 + m2) * g * l1 + m2 * g * l2


def rk4_step(state, h, **p):
    """One Runge-Kutta 4 step of size h (s)."""
    k1 = rate(state, **p)
    k2 = rate(state + 0.5 * h * k1, **p)
    k3 = rate(state + 0.5 * h * k2, **p)
    k4 = rate(state + h * k3, **p)
    return state + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate(state0, duration, h, **p):
    n = int(round(duration / h))
    out = np.empty((n + 1, 4))
    out[0] = state0
    for i in range(n):
        out[i + 1] = rk4_step(out[i], h, **p)
    return np.arange(n + 1) * h, out


def energy_drift(state0, duration, h, **p):
    """Largest |E(t) - E(0)| / E_ref over the run (no unit)."""
    _, s = simulate(state0, duration, h, **p)
    e = np.array([energy(x, **p) for x in s])
    return float(np.max(np.abs(e - e[0])) / energy_scale(**p))


def release(a_deg):
    """State at rest with both rods at the same angle a (degrees from straight down)."""
    a = np.radians(a_deg)
    return np.array([a, a, 0.0, 0.0])


# %% [markdown]
# ## Step 3: the small-angle limit, the second check
# For tiny angles sin x is about x and cos x about 1. The equations become linear:
# M * th'' = -K * th with M = [[(m1+m2) l1^2, m2 l1 l2], [m2 l1 l2, m2 l2^2]] and
# K = diag((m1+m2) g l1, m2 g l2). Solutions are two *normal modes*: the angles swing together
# at one frequency pattern, each with its own frequency w (rad/s) from det(K - w^2 M) = 0.
# For equal masses and rods, w^2 = (g / l)(2 -/+ sqrt 2): 2.40 rad/s (in step) and 5.79 rad/s (opposite).

# %%
def normal_modes(m1=1.0, m2=1.0, l1=1.0, l2=1.0, g=G):
    """Return (frequencies in rad/s ascending, mode shapes as columns scaled so th1 = 1)."""
    M = np.array([[(m1 + m2) * l1 ** 2, m2 * l1 * l2], [m2 * l1 * l2, m2 * l2 ** 2]])
    K = np.diag([(m1 + m2) * g * l1, m2 * g * l2])
    vals, vecs = np.linalg.eig(np.linalg.solve(M, K))
    order = np.argsort(vals.real)
    w = np.sqrt(vals.real[order])
    vecs = vecs[:, order].real
    vecs = vecs / vecs[0]          # th1 = 1 in every mode
    return w, vecs


def small_angle_error(mode, amp=1e-3, duration=3.0, h=0.002, **p):
    """Largest difference (rad) between the full nonlinear simulation and the exact linear mode,
    for a start at rest with shape = mode and amplitude amp (rad)."""
    w, vecs = normal_modes(**p)
    shape = vecs[:, mode]
    state0 = np.array([amp * shape[0], amp * shape[1], 0.0, 0.0])
    t, s = simulate(state0, duration, h, **p)
    exact = amp * np.outer(np.cos(w[mode] * t), shape)
    return float(np.max(np.abs(s[:, :2] - exact)))


# %% [markdown]
# ## Step 4: a design problem
# Choose the largest time step h (cheapest run) so that the energy drift over 20 s, released from
# rest at 120 degrees, stays below a tolerance. RK4 is a fourth-order method: halving h should
# cut the error by about 2^4 = 16.

# %%
def largest_step(tol, state0, duration, candidates, **p):
    """Largest candidate step whose energy drift is below tol, and the table of drifts."""
    table = [(h, energy_drift(state0, duration, h, **p)) for h in candidates]
    ok = [h for h, d in table if d < tol]
    return (max(ok) if ok else None), table


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    s0 = release(120.0)
    w, vecs = normal_modes()
    print("normal modes (equal masses and rods): w =", np.round(w, 4), "rad/s; shapes th2/th1 =", np.round(vecs[1], 4))
    print("hand formula g(2 -/+ sqrt2):", np.round(np.sqrt(G * (2 - np.sqrt(2))), 4), np.round(np.sqrt(G * (2 + np.sqrt(2))), 4))
    for k in range(2):
        print(f"small-angle error, mode {k + 1}: {small_angle_error(k):.2e} rad (amplitude 1e-3 rad)")
    cands = [0.04, 0.02, 0.01, 0.005, 0.0025]
    best, table = largest_step(1e-5, s0, 20.0, cands)
    for h, d in table:
        print(f"h = {h:7.4f} s   energy drift {d:.2e}   steps {int(20 / h)}")
    print("largest step with drift below 1e-5:", best, "s;  below 1e-6:", largest_step(1e-6, s0, 20.0, cands)[0], "s")

    # Figure 1: energy error versus time for three steps
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for h in (0.02, 0.01, 0.005):
        t, s = simulate(s0, 20.0, h)
        e = np.array([energy(x) for x in s])
        ax.semilogy(t, np.maximum(np.abs(e - e[0]) / energy_scale(), 1e-16), label=f"h = {h} s")
    ax.axhline(1e-6, color="red", ls="--", label="tolerance 1e-6")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("relative energy error |E - E0| / E_ref")
    ax.set_title("RK4 energy error grows with time and with step size")
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "energy_error.png", dpi=120)

    # Figure 2: error versus step, with the order-4 slope
    hs = np.array([0.04, 0.02, 0.01, 0.005, 0.0025])
    ds = np.array([energy_drift(s0, 20.0, h) for h in hs])
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.loglog(hs, ds, "o-", label="measured drift")
    ax2.loglog(hs, ds[2] * (hs / hs[2]) ** 4, "k--", label="slope 4 (fourth order)")
    ax2.set_xlabel("time step h (s)")
    ax2.set_ylabel("relative energy drift over 20 s")
    ax2.set_title("Halving the step cuts the drift by about 16")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "drift_vs_step.png", dpi=120)

    # Figure 3: nonlinear versus linear for mode 1 at amplitude 0.05 rad (visible comparison)
    t, s = simulate(np.array([0.05 * vecs[0, 0], 0.05 * vecs[1, 0], 0.0, 0.0]), 4.0, 0.005)
    fig3, ax3 = plt.subplots(figsize=(6.5, 4))
    ax3.plot(t, s[:, 0], label="upper rod (full equations)")
    ax3.plot(t, s[:, 1], label="lower rod (full equations)")
    ax3.plot(t, 0.05 * np.cos(w[0] * t), "k:", label="linear mode 1, upper rod")
    ax3.set_xlabel("time (s)")
    ax3.set_ylabel("angle (rad)")
    ax3.set_title("Small swings follow the normal mode (w = 2.40 rad/s)")
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "normal_mode.png", dpi=120)

# %% [markdown]
# ## Where this stops
# RK4 has a small energy error that slowly builds up. For a chaotic motion that is fine for
# a few tens of seconds, but not for ever. Session 3 compares it with a symplectic method,
# measures how fast two nearby starts separate, and maps where the motion is regular or chaotic.
