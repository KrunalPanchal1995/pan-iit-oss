"""Session 2 (Level 2): the motion profile, travel time and motor power.

Run:  python start.py 2
Educational model only. It is NOT an elevator design tool: real lifts follow safety standards.
"""
# %% [markdown]
# # Session 2: plan the ride and size the motor
# **A. Real-world problem.** Two floors are 3.5 m apart. How quickly can a lift make the trip without
# making passengers feel sick? And how much power must the motor have, given a counterweight that
# balances most of the car?
#
# **Plan.** (1) the trapezoid and the S-curve profile as formulas, (2) travel time for a given
# distance, (3) the power with a counterweight, (4) the design problem.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G = 9.81   # m/s^2


# %% [markdown]
# ## Step 1: the trapezoid profile
# Speed up at a constant acceleration a until the cruise speed v, cruise, then slow down at -a.
# If the distance is short, the car never reaches v: the speed graph is a triangle with peak sqrt(a d).
#
#     d >= v^2 / a :  T = d / v + v / a        (accelerate, cruise, decelerate)
#     d <  v^2 / a :  T = 2 sqrt(d / a)        (triangle)

# %%
def trapezoid_time(d, v, a):
    """Travel time (s) of a trapezoid-speed ride of distance d (m), cruise speed v (m/s), accel a (m/s^2)."""
    if d >= v ** 2 / a:
        return d / v + v / a
    return 2 * np.sqrt(d / a)


# %% [markdown]
# ## Step 2: the S-curve (jerk-limited) profile
# The **jerk** j = da/dt is how fast the acceleration changes. A trapezoid changes a instantly, which you
# feel as a jolt. The S-curve ramps a up and down at the rate j. To reach speed v:
#
#     if v >= a^2 / j :  ramp time tj = a / j,  Ta = v / a + a / j       (a reaches its limit)
#     otherwise       :  tj = sqrt(v / j),      Ta = 2 sqrt(v / j)        (a never reaches its limit)
#
# Speeding up and slowing down cover the distance v Ta together, so if d >= v Ta the time is
# T = d / v + Ta. If the distance is shorter, the cruise speed is lowered until v Ta(v) = d.

# %%
def accel_phase(v, amax, jmax):
    """Time to speed up from 0 to v: returns (total Ta, ramp time tj, constant-accel time tl)."""
    if v >= amax ** 2 / jmax:
        tj = amax / jmax
        return v / amax + tj, tj, v / amax - tj
    tj = np.sqrt(v / jmax)
    return 2 * tj, tj, 0.0


def scurve_plan(d, vmax, amax, jmax):
    """S-curve plan for distance d: dict with cruise speed v, phase times and travel time T (s)."""
    def reach(v):
        return v * accel_phase(v, amax, jmax)[0]

    if reach(vmax) <= d:
        v = vmax
    else:                         # lower the cruise speed until it just fits (bisection)
        lo, hi = 0.0, vmax
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if reach(mid) < d else (lo, mid)
        v = 0.5 * (lo + hi)
    Ta, tj, tl = accel_phase(v, amax, jmax)
    tc = (d - v * Ta) / v
    return dict(v=v, Ta=Ta, tj=tj, tl=tl, tc=tc, T=2 * Ta + tc, a=tj * jmax, j=jmax)


def scurve_time(d, vmax, amax, jmax):
    return scurve_plan(d, vmax, amax, jmax)["T"]


# %% [markdown]
# ## Step 3: build the whole profile as arrays (a numerical check)
# Starting from the jerk (+j, 0, -j, 0, -j, 0, +j in time), add up the jerk to get a, add up a to get
# the speed v and add up v to get the position x. The last position must equal the distance d.

# %%
def jerk_series(pl, dt=0.001):
    """Time array and the planned jerk (m/s^3) for an S-curve plan."""
    t = np.arange(0.0, pl["T"] + dt / 2, dt)
    j, tj, tl, Ta, T = pl["j"], pl["tj"], pl["tl"], pl["Ta"], pl["T"]

    def half(s):     # jerk while speeding up (s = time since that phase began)
        return np.where(s < tj, j, np.where(s < tj + tl, 0.0, np.where(s < Ta, -j, 0.0)))

    s = t - (T - Ta)
    jerk = np.where(t < Ta, half(t), 0.0) - np.where(s >= 0, half(np.clip(s, 0, None)), 0.0)
    return t, jerk


def integrate_profile(pl, dt=0.001, fine=50):
    """Return t, jerk, a, v, x for an S-curve plan by numerical integration.

    The jerk switches between values at times that are not on the grid, so we integrate on a
    grid `fine` times finer and keep every `fine`-th point; this keeps the end position accurate.
    """
    h = dt / fine
    t, jerk = jerk_series(pl, h)
    a = np.concatenate([[0.0], np.cumsum(0.5 * (jerk[1:] + jerk[:-1]) * h)])
    v = np.concatenate([[0.0], np.cumsum(0.5 * (a[1:] + a[:-1]) * h)])
    x = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * h)])
    return t[::fine], jerk[::fine], a[::fine], v[::fine], x[::fine]


# %% [markdown]
# ## Step 4: the motor and the counterweight
# Car mass m_car, passengers m_load and counterweight m_cw hang on one rope. The motor only has to
# supply the **unbalanced** weight, (m_car + m_load - m_cw) g, plus the force that accelerates all
# the moving mass M = m_car + m_load + m_cw. At constant speed v:
#
#     P = (m_car + m_load - m_cw) g v / eta        (eta = efficiency, between 0 and 1)
#
# During acceleration a the force becomes (m_car + m_load - m_cw) g + M a.

# %%
def counterweight_mass(m_car, rated_load, fraction=0.45):
    """Common rule of thumb: counterweight = car + a fraction (about 40 to 50 percent) of the rated load."""
    return m_car + fraction * rated_load


def cruise_power(m_car, m_load, m_cw, v, eta):
    """Motor input power (W) at constant speed v (m/s) going up; negative means the motor is driven."""
    return (m_car + m_load - m_cw) * G * v / eta


def peak_force(m_car, m_load, m_cw, a):
    """Rope force (N) while accelerating upward at a (m/s^2)."""
    return (m_car + m_load - m_cw) * G + (m_car + m_load + m_cw) * a


# %% [markdown]
# ## Step 5: the design problem
# Fastest comfortable ride between two floors 3.5 m apart, then a 20-floor express (19 floors = 66.5 m).
# Assumed comfort limits (typical figures, not a standard): a <= 1.0 m/s^2, j <= 1.5 m/s^3.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    vmax, amax, jmax = 2.5, 1.0, 1.5
    m_car, rated, eta = 1000.0, 800.0, 0.85
    m_cw = counterweight_mass(m_car, rated)
    for label, d, vm in (("3.5 m (one floor)", 3.5, 2.5), ("66.5 m (20-floor express)", 66.5, 4.0)):
        pl = scurve_plan(d, vm, amax, jmax)
        print(f"{label}: trapezoid {trapezoid_time(d, vm, amax):.2f} s, S-curve {pl['T']:.2f} s "
              f"(cruise speed reached {pl['v']:.2f} m/s)")
    print(f"counterweight {m_cw:.0f} kg; cruise power full load up at 4 m/s: "
          f"{cruise_power(m_car, rated, m_cw, 4.0, eta) / 1000:.1f} kW")

    pl = scurve_plan(66.5, 4.0, amax, jmax)
    t, jerk, a, v, x = integrate_profile(pl)
    print(f"integrated distance {x[-1]:.3f} m, final speed {v[-1]:.4f} m/s")
    fig, ax = plt.subplots(4, 1, figsize=(6.4, 7.2), sharex=True)
    for axis, y, name in zip(ax, (x, v, a, jerk), ("position (m)", "speed (m/s)", "acceleration (m/s^2)", "jerk (m/s^3)")):
        axis.plot(t, y, color="tab:blue")
        axis.set_ylabel(name)
        axis.grid(alpha=0.3)
    ax[-1].set_xlabel("time (s)")
    ax[0].set_title("S-curve for a 20-floor express (66.5 m)")
    fig.tight_layout()
    fig.savefig(OUT / "scurve_profile.png", dpi=120)

    dist = np.linspace(1, 70, 140)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(dist, [trapezoid_time(d, 4.0, amax) for d in dist], label="trapezoid (a = 1.0)")
    ax2.plot(dist, [scurve_time(d, 4.0, amax, jmax) for d in dist], label="S-curve (a = 1.0, j = 1.5)")
    ax2.set_xlabel("distance (m)")
    ax2.set_ylabel("travel time (s)")
    ax2.set_title("Jerk limit costs time on short rides")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "time_vs_distance.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
