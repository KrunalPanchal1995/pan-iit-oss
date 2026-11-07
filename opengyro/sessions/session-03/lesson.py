"""Session 3 (Level 3): simulate the heavy symmetric top with Euler angles and validate it.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulating a spinning top
# **A. Real-world problem.** A toy top spun fast at a tilt does not fall: it circles slowly
# (precession) and shivers a little (nutation). Spun slowly it topples. Spun upright and
# fast enough it "sleeps" (stands still). Today you simulate the top from the Lagrangian
# equations, check that energy and two angular momenta stay constant, and compare the result
# with the Session 2 formula.
#
# **Setup.** A rigid body (a disc on a short axle) turns about a fixed point O, the tip. The
# axis makes angle `theta` with the upward vertical, turns around the vertical by `phi`, and
# the disc spins about its own axis by `psi` (the three Euler angles).

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G = 9.81          # m/s^2
M = 0.5           # kg, mass of the disc
RAD = 0.05        # m, disc radius
LEN = 0.04        # m, distance from the fixed point to the centre of mass (r)
I3 = M * RAD ** 2 / 2                      # about the symmetry axis, kg m^2
I1 = M * RAD ** 2 / 4 + M * LEN ** 2       # about a perpendicular axis through the fixed point
MGR = M * G * LEN                          # N m, the largest gravity torque


# %% [markdown]
# ## Step 1: the equations
# With `w3 = psi' + phi' cos(theta)` (the spin component along the axis) the Lagrangian is
#
#     L = I1/2 (theta'^2 + phi'^2 sin^2 theta) + I3/2 w3^2 - m g r cos(theta)
#
# `phi` and `psi` do not appear in L, so two momenta are conserved:
#
#     p_psi = I3 w3                                   (constant, so w3 is constant)
#     p_phi = I1 phi' sin^2 theta + I3 w3 cos(theta)  (constant)
#
# The Lagrange equation for `theta` and the derivative of `p_phi` give the three accelerations:
#
#     theta'' = phi'^2 sin cos - (I3/I1) w3 phi' sin + (m g r / I1) sin
#     phi''   = (I3 w3 / I1 - 2 phi' cos) theta' / sin
#     psi''   = -(phi'' cos - phi' sin theta')
#
# We integrate all three with RK4 and then *check* that p_phi, p_psi and the energy stay put.

# %%
def deriv(y, i1=I1, i3=I3, mgr=MGR):
    """y = [theta, phi, psi, theta', phi', psi'] -> its time derivative."""
    th, _, _, thd, phd, psd = y
    s, c = np.sin(th), np.cos(th)
    w3 = psd + phd * c
    thdd = phd * phd * s * c - (i3 / i1) * w3 * phd * s + (mgr / i1) * s
    phdd = (i3 * w3 / i1 - 2.0 * phd * c) * thd / s
    psdd = -(phdd * c - phd * s * thd)
    return np.array([thd, phd, psd, thdd, phdd, psdd])


def rk4_step(y, dt, **kw):
    k1 = deriv(y, **kw)
    k2 = deriv(y + 0.5 * dt * k1, **kw)
    k3 = deriv(y + 0.5 * dt * k2, **kw)
    k4 = deriv(y + dt * k3, **kw)
    return y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate(w3, theta0, t_end=3.0, dt=2e-4, phid0=0.0, **kw):
    """Release the top at angle theta0 (radians) with spin component w3 (rad/s) along the axis.

    Returns times t and the states y (rows: [theta, phi, psi, theta', phi', psi']).
    """
    y = np.array([theta0, 0.0, 0.0, 0.0, phid0, w3 - phid0 * np.cos(theta0)])
    n = int(round(t_end / dt))
    t = np.arange(n + 1) * dt
    out = np.empty((n + 1, 6))
    out[0] = y
    for k in range(n):
        y = rk4_step(y, dt, **kw)
        out[k + 1] = y
    return t, out


# %% [markdown]
# ## Step 2: the quantities that must be constant
# These are the validation tools. A correct simulation of a frictionless top keeps all three
# constant; the size of their drift is the numerical error.

# %%
def invariants(y, i1=I1, i3=I3, mgr=MGR):
    th, thd, phd, psd = y[:, 0], y[:, 3], y[:, 4], y[:, 5]
    w3 = psd + phd * np.cos(th)
    p_psi = i3 * w3
    p_phi = i1 * phd * np.sin(th) ** 2 + i3 * w3 * np.cos(th)
    energy = 0.5 * i1 * (thd ** 2 + (phd * np.sin(th)) ** 2) + 0.5 * i3 * w3 ** 2 + mgr * np.cos(th)
    return p_psi, p_phi, energy


def relative_drift(x):
    """Largest change of x divided by the largest size of x."""
    return float(np.max(np.abs(x - x[0])) / max(np.max(np.abs(x)), 1e-30))


# %% [markdown]
# ## Step 3: precession rate and nutation frequency
# For a fast spin the theory of Session 2 says `Omega_p = m g r / (I3 w3)`. The top also
# nods in theta at about `w_n = I3 w3 / I1` (nutation). We measure both from the simulation.
# The mean precession rate is taken between the first and last minimum of theta, so a whole
# number of nutation cycles is included.

# %%
def measured_rates(t, y):
    """Return (mean phi' over whole nutation cycles, nutation angular frequency) or (nan, nan)."""
    th = y[:, 0]
    idx = np.where((th[1:-1] < th[:-2]) & (th[1:-1] <= th[2:]))[0] + 1   # local minima of theta
    if len(idx) < 3:
        return float("nan"), float("nan")
    tm = []
    for k in idx:      # refine each minimum with a parabola through three points
        a, b, c = th[k - 1], th[k], th[k + 1]
        shift = 0.5 * (a - c) / (a - 2 * b + c)
        tm.append(t[k] + shift * (t[1] - t[0]))
    tm = np.array(tm)
    nut = 2 * np.pi / np.mean(np.diff(tm))
    i0, i1_ = idx[0], idx[-1]
    rate = (y[i1_, 1] - y[i0, 1]) / (t[i1_] - t[i0])
    return float(rate), float(nut)


def omega_p(w3, i3=I3, mgr=MGR):
    """Fast-spin precession rate m g r / (I3 w3), rad/s."""
    return mgr / (i3 * w3)


def sleeping_limit(i1=I1, i3=I3, mgr=MGR):
    """Classical bound: a vertical top is stable if w3^2 > 4 m g r I1 / I3^2. Returns w3_min in rad/s."""
    return float(np.sqrt(4.0 * mgr * i1) / i3)


def sleeping_run(w3, theta0=0.05, t_end=4.0, dt=2e-4):
    """Release the top almost vertical (theta0 rad, a small push). Returns the largest tilt reached (rad)."""
    t, y = simulate(w3, theta0, t_end, dt)
    return float(y[:, 0].max())


def falls(w3, theta0=np.radians(45), t_end=3.0, dt=1e-3):
    """True if the axis reaches the horizontal (theta >= 90 degrees) within t_end."""
    t, y = simulate(w3, theta0, t_end, dt)
    return bool(y[:, 0].max() >= np.pi / 2)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    th0 = np.radians(60)
    w3 = 300.0
    t, y = simulate(w3, th0, 3.0)
    p_psi, p_phi, en = invariants(y)
    print(f"I3 = {I3:.4e} kg m^2, I1 = {I1:.4e} kg m^2, m g r = {MGR:.4f} N m")
    print(f"drift of p_psi {relative_drift(p_psi):.1e}, p_phi {relative_drift(p_phi):.1e}, energy {relative_drift(en):.1e}")
    rate, nut = measured_rates(t, y)
    print(f"w3 = {w3:.0f} rad/s: simulated precession {rate:.4f} rad/s, formula {omega_p(w3):.4f} rad/s, "
          f"difference {100 * (rate / omega_p(w3) - 1):.1f} %")
    print(f"nutation: simulated {nut:.1f} rad/s, formula I3 w3 / I1 = {I3 * w3 / I1:.1f} rad/s")

    # figure 1: the path of the axis tip seen from above, and theta(t)
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.3))
    ax[0].plot(np.sin(y[:, 0]) * np.cos(y[:, 1]), np.sin(y[:, 0]) * np.sin(y[:, 1]), lw=0.8)
    ax[0].set_aspect("equal")
    ax[0].set_xlabel("x of axis tip (unit length)")
    ax[0].set_ylabel("y of axis tip (unit length)")
    ax[0].set_title("Axis tip seen from above")
    ax[0].grid(alpha=0.3)
    ax[1].plot(t, np.degrees(y[:, 0]))
    ax[1].set_xlabel("time (s)")
    ax[1].set_ylabel("tilt theta (degrees)")
    ax[1].set_title("Tilt versus time: nutation")
    ax[1].set_xlim(0, 0.5)
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "top_path.png", dpi=120)

    # figure 2: validation
    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    for name, q in (("energy", en), ("p_phi", p_phi), ("p_psi", p_psi)):
        ax2.semilogy(t[1:], np.abs(q[1:] - q[0]) / np.max(np.abs(q)) + 1e-18, label=name)
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("relative change since t = 0 (no unit)")
    ax2.set_title("Conserved quantities stay constant (RK4)")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "conservation.png", dpi=120)

    # figure 3: precession rate versus spin
    ws = np.array([80, 120, 160, 200, 300, 400, 600])
    sim = [measured_rates(*simulate(w, th0, 3.0, 2e-4))[0] for w in ws]
    for w, s in zip(ws, sim):
        print(f"w3 = {w:4d}: simulated {s:.4f}  formula {omega_p(w):.4f}  ratio {s / omega_p(w):.3f}")
    fig3, ax3 = plt.subplots(figsize=(6.5, 4))
    wl = np.linspace(60, 620, 200)
    ax3.plot(wl, omega_p(wl), label="formula m g r / (I3 w3)")
    ax3.plot(ws, sim, "o", label="simulation")
    ax3.set_xlabel("spin w3 (rad/s)")
    ax3.set_ylabel("precession rate (rad/s)")
    ax3.set_title("Faster spin, slower precession")
    ax3.legend()
    ax3.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "precession_vs_spin.png", dpi=120)

    # sleeping top and failure
    wc = sleeping_limit()
    print(f"classical sleeping limit w3 > {wc:.1f} rad/s")
    for f in (0.8, 0.9, 1.1, 1.3):
        print(f"  w3 = {f:.1f} x limit = {f * wc:6.1f} rad/s: largest tilt {np.degrees(sleeping_run(f * wc)):.1f} degrees")
    for w in (10.0, 30.0, 300.0):
        print(f"  start 45 degrees, spin {w:5.0f} rad/s: falls over = {falls(w)}")

# %% [markdown]
# ## Where this stops
# This is an ideal top: no friction at the tip, no air drag, a perfect point contact. Real tops
# slow down, and the friction makes a tilted top rise towards the vertical. That is the road to
# the Target: see `promo/roadmap.md`.
