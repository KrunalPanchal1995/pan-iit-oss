"""Session 2 (Level 2): circular and elliptical orbits, vis-viva, Kepler's equation, two integrators.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the mathematics of an orbit
# **A. Real-world problem.** An operator needs an orbit that dips to 500 km above the ground
# and climbs to 35786 km. How long is one lap, how fast is the satellite at each end, and where
# is it one hour after perigee? You need four tools: circular speed, the vis-viva equation,
# Kepler's third law, and Kepler's equation. Then you check the physics by simulation, using two
# numerical methods and measuring how much energy each one wrongly gains or loses.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
MU = 3.986004418e14      # m^3/s^2
R_EARTH = 6.371e6        # m


# %% [markdown]
# ## Step 1: circular orbits and Kepler's third law
# v = sqrt(mu / r) and T = 2 pi sqrt(a^3 / mu), where a is the semi-major axis (half the long
# axis of the ellipse; for a circle a = r).

# %%
def circular_speed(r):
    return np.sqrt(MU / r)


def period(a):
    """Orbital period (s) from the semi-major axis a (m): Kepler's third law."""
    return 2 * np.pi * np.sqrt(a**3 / MU)


# %% [markdown]
# ## Step 2: the ellipse and the vis-viva equation
# Closest point = perigee radius rp; farthest = apogee radius ra (both measured from the centre
# of the Earth, so altitude + 6371 km). Then a = (rp + ra) / 2 and e = (ra - rp) / (ra + rp).
# The speed anywhere is given by vis-viva: v^2 = mu (2/r - 1/a).

# %%
def ellipse_from_peri_apo(rp, ra):
    """Return semi-major axis a (m) and eccentricity e from perigee and apogee radii (m)."""
    return (rp + ra) / 2, (ra - rp) / (ra + rp)


def vis_viva(r, a):
    """Speed (m/s) at distance r (m) on an orbit of semi-major axis a (m)."""
    return np.sqrt(MU * (2 / r - 1 / a))


def specific_energy(r, v):
    """Energy per kilogram (J/kg): kinetic minus gravitational. Equals -mu / (2 a) for a Kepler orbit."""
    return 0.5 * v**2 - MU / r


def angular_momentum(rvec, vvec):
    """Specific angular momentum (m^2/s): x*vy - y*vx. Conserved because gravity points at the centre."""
    return rvec[0] * vvec[1] - rvec[1] * vvec[0]


def semi_major_axis_for_period(T):
    """Semi-major axis (m) for a period T (s): Kepler's third law solved for a."""
    return (MU * (T / (2 * np.pi)) ** 2) ** (1 / 3)


def apogee_altitude_for_period(T, alt_perigee_km):
    """Apogee altitude (km) of the orbit with period T (s) and the given perigee altitude (km)."""
    return (2 * semi_major_axis_for_period(T) - (R_EARTH + alt_perigee_km * 1e3) - R_EARTH) / 1e3


def design_orbit(alt_perigee_km, alt_apogee_km):
    """Everything about an orbit with given perigee and apogee altitudes."""
    rp, ra = R_EARTH + alt_perigee_km * 1e3, R_EARTH + alt_apogee_km * 1e3
    a, e = ellipse_from_peri_apo(rp, ra)
    return {"a": a, "e": e, "T": period(a), "vp": vis_viva(rp, a), "va": vis_viva(ra, a), "rp": rp, "ra": ra}


# %% [markdown]
# ## Step 3: Kepler's equation, where is the satellite at time t?
# Mean anomaly M = 2 pi t / T grows steadily. The eccentric anomaly E is the geometric angle
# we need; they are linked by M = E - e sin(E). There is no formula for E, so we solve it by
# Newton's method: E <- E - (E - e sin E - M) / (1 - e cos E).

# %%
def solve_kepler(M, e, tol=1e-12, max_iter=50):
    """Solve M = E - e sin E for E (radians). Returns (E, iterations, residual)."""
    E = M if e < 0.8 else np.pi
    for k in range(1, max_iter + 1):
        f = E - e * np.sin(E) - M
        E = E - f / (1 - e * np.cos(E))
        if abs(E - e * np.sin(E) - M) < tol:
            return E, k, abs(E - e * np.sin(E) - M)
    return E, max_iter, abs(E - e * np.sin(E) - M)


def radius_from_E(E, a, e):
    return a * (1 - e * np.cos(E))


# %% [markdown]
# ## Step 4: integrate the two-body equations and measure the drift
# Acceleration is -mu r / |r|^3. RK4 is a general-purpose method (accurate each step, but its
# energy slowly drifts). Leapfrog (velocity Verlet) is *symplectic*: its energy wobbles but does
# not drift. We measure both over many laps.

# %%
def accel(r):
    return -MU * r / np.linalg.norm(r) ** 3


def rk4_step(r, v, dt):
    k1r, k1v = v, accel(r)
    k2r, k2v = v + 0.5 * dt * k1v, accel(r + 0.5 * dt * k1r)
    k3r, k3v = v + 0.5 * dt * k2v, accel(r + 0.5 * dt * k2r)
    k4r, k4v = v + dt * k3v, accel(r + dt * k3r)
    return r + dt / 6 * (k1r + 2 * k2r + 2 * k3r + k4r), v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)


def leapfrog_step(r, v, dt):
    v_half = v + 0.5 * dt * accel(r)
    r_new = r + dt * v_half
    return r_new, v_half + 0.5 * dt * accel(r_new)


def propagate(step, r0, v0, dt, n):
    """Run n steps. Returns arrays of positions (n+1, 2), energy (n+1) and angular momentum (n+1)."""
    r, v = np.array(r0, float), np.array(v0, float)
    pos, en, hh = [r.copy()], [specific_energy(np.linalg.norm(r), np.linalg.norm(v))], [angular_momentum(r, v)]
    for _ in range(n):
        r, v = step(r, v, dt)
        pos.append(r.copy())
        en.append(specific_energy(np.linalg.norm(r), np.linalg.norm(v)))
        hh.append(angular_momentum(r, v))
    return np.array(pos), np.array(en), np.array(hh)


def perigee_start(rp, ra):
    """Start state (position, velocity) at perigee on the x axis, counter-clockwise."""
    a, _ = ellipse_from_peri_apo(rp, ra)
    return np.array([rp, 0.0]), np.array([0.0, vis_viva(rp, a)])


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    o = design_orbit(500, 35786)
    print(f"design orbit 500 x 35786 km: a = {o['a'] / 1e3:.0f} km, e = {o['e']:.4f}, T = {o['T'] / 3600:.3f} h")
    print(f"  perigee speed {o['vp'] / 1e3:.3f} km/s, apogee speed {o['va'] / 1e3:.3f} km/s, ratio {o['vp'] / o['va']:.3f} = ra/rp {o['ra'] / o['rp']:.3f}")
    print(f"  energy -mu/2a = {-MU / (2 * o['a']):.1f} J/kg")
    print(f"12 hour orbit with perigee 500 km: a = {semi_major_axis_for_period(43200.0) / 1e3:.0f} km, apogee altitude {apogee_altitude_for_period(43200.0, 500):.0f} km")
    E, k, res = solve_kepler(2 * np.pi * 3600 / o["T"], o["e"])
    print(f"  one hour after perigee: M = {2 * np.pi * 3600 / o['T']:.4f} rad, E = {E:.5f} rad, {k} iterations, residual {res:.1e}, r = {radius_from_E(E, o['a'], o['e']) / 1e3:.0f} km")
    for e in (0.0, 0.3, 0.7, 0.95):
        its = max(solve_kepler(M, e)[1] for M in np.linspace(0.01, 6.27, 200))
        print(f"  e = {e}: at most {its} Newton iterations")

    rp, ra = 7.0e6, 2.1e7
    r0, v0 = perigee_start(rp, ra)
    T = period((rp + ra) / 2)
    dt, laps = 60.0, 50
    n = int(round(T * laps / dt))
    res = {}
    for name, step in (("RK4", rk4_step), ("leapfrog", leapfrog_step)):
        pos, en, hh = propagate(step, r0, v0, dt, n)
        res[name] = (pos, en, hh)
        print(f"{name:9s} dt={dt:.0f}s {laps} laps: energy change {(en[-1] - en[0]) / abs(en[0]):.2e}, worst {np.max(np.abs(en - en[0])) / abs(en[0]):.2e}, h change {(hh[-1] - hh[0]) / hh[0]:.2e}")

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    th = np.linspace(0, 2 * np.pi, 300)
    axs[0].fill(R_EARTH / 1e3 * np.cos(th), R_EARTH / 1e3 * np.sin(th), color="#9ecae1")
    pos = res["RK4"][0][: int(T / dt) + 1] / 1e3
    axs[0].plot(pos[:, 0], pos[:, 1], "k-", lw=1)
    axs[0].plot([rp / 1e3], [0], "ro"); axs[0].text(rp / 1e3 + 500, 800, "perigee")
    axs[0].plot([-ra / 1e3], [0], "go"); axs[0].text(-ra / 1e3, 1500, "apogee")
    axs[0].set_aspect("equal"); axs[0].set_xlabel("x (km)"); axs[0].set_ylabel("y (km)")
    axs[0].set_title("One lap of a 7000 x 21000 km ellipse"); axs[0].grid(alpha=0.3)
    t_h = np.arange(n + 1) * dt / 3600
    for name, col in (("RK4", "#d62728"), ("leapfrog", "#1f77b4")):
        axs[1].plot(t_h, (res[name][1] - res[name][1][0]) / abs(res[name][1][0]), color=col, label=name)
    axs[1].set_xlabel("time (hours)"); axs[1].set_ylabel("relative energy change (no unit)")
    axs[1].set_title("RK4 drifts steadily, leapfrog stays bounded"); axs[1].legend(); axs[1].grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(OUT / "orbit_and_drift.png", dpi=120)

    M = np.linspace(0, 2 * np.pi, 200)
    fig2, ax2 = plt.subplots(figsize=(5.5, 4))
    for e in (0.0, 0.3, 0.7, 0.9):
        ax2.plot(M, [solve_kepler(m, e)[0] for m in M], label=f"e = {e}")
    ax2.set_xlabel("mean anomaly M (radians)"); ax2.set_ylabel("eccentric anomaly E (radians)")
    ax2.set_title("Solving Kepler's equation"); ax2.legend(); ax2.grid(alpha=0.3)
    fig2.tight_layout(); fig2.savefig(OUT / "kepler_equation.png", dpi=120)
