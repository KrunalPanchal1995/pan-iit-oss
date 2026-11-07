"""Session 3 (Level 3): simulate the whole lift and validate it.

Run:  python start.py 3
Educational model only. It is NOT an elevator design tool: real lifts follow safety standards
and are designed and certified by qualified engineers.
"""
# %% [markdown]
# # Session 3: a time-stepping simulation of a cable-counterweight lift
# **A. Real-world problem.** Session 2 gave a clean formula for the ride. A real motor has a torque
# limit, its force takes a moment to build up, and a heavy car does not follow the plan exactly.
# We now simulate the car step by step, with a controller that tries to follow a planned profile,
# and check the simulation against the Session 2 formulas.
#
# **Plan.** (1) plan the profile (trapezoid or S-curve), (2) simulate the car with a torque
# limit, (3) measure comfort, (4) validate with the travel-time formula and the energy balance,
# (5) see how load and counterweight change energy and comfort.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G = 9.81  # m/s^2

# one simplified lift used everywhere in this session (all numbers are assumptions)
LIFT = dict(m_car=1000.0, m_cw=1360.0, eta=0.85, tau=0.05, kp=100.0, kv=20.0)
# m_car: empty car (kg); m_cw: counterweight = car + 45 percent of 800 kg rated load;
# eta: motor and gear efficiency; tau: time the motor force needs to build up (s);
# kp, kv: gains of the controller that tracks the plan


# %% [markdown]
# ## Step 1: plan the motion (the profile)
# A profile is a planned acceleration a(t). The **trapezoid** profile switches acceleration on and
# off suddenly (infinite jerk on paper). The **S-curve** profile changes acceleration at a limited
# rate j (the jerk limit), in up to seven phases:
# jerk +j, a = amax, jerk -j, cruise, jerk -j, a = -amax, jerk +j.
# For a distance d the cruise speed is reduced if there is not enough room to reach vmax.

# %%
def accel_phase(v, amax, jmax):
    """Time to speed up from 0 to v: returns (total, jerk time tj, constant-accel time tl)."""
    if v >= amax ** 2 / jmax:
        tj = amax / jmax
        return v / amax + tj, tj, v / amax - tj
    tj = np.sqrt(v / jmax)
    return 2 * tj, tj, 0.0


def plan(d, vmax, amax, jmax=None):
    """Plan a ride of distance d (m). jmax=None gives the trapezoid profile.

    Returns a dict with phase times and the travel time T (s) from the exact formulas.
    """
    d = abs(d)
    if jmax is None:   # trapezoid: a switches instantly
        v = vmax if d >= vmax ** 2 / amax else np.sqrt(d * amax)
        ta = v / amax
        tc = (d - v * ta) / v if d > 0 else 0.0
        return dict(kind="trapezoid", v=v, tj=0.0, tl=ta, tc=tc, Ta=ta, T=2 * ta + tc, a=amax, j=None)

    # S-curve: distance covered by accelerating and braking is v * Ta(v)
    def reach(v):
        return v * accel_phase(v, amax, jmax)[0]

    if reach(vmax) <= d:
        v = vmax
    else:                       # find the cruise speed that just fits (bisection)
        lo, hi = 0.0, vmax
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if reach(mid) < d else (lo, mid)
        v = 0.5 * (lo + hi)
    Ta, tj, tl = accel_phase(v, amax, jmax) if v > 0 else (0.0, 0.0, 0.0)
    tc = (d - v * Ta) / v if v > 0 else 0.0
    return dict(kind="s-curve", v=v, tj=tj, tl=tl, tc=tc, Ta=Ta, T=2 * Ta + tc, a=tj * jmax, j=jmax)


def reference(pl, dt=0.001):
    """Planned time, acceleration, speed, position (arrays) for a plan, travelling up."""
    T = pl["T"]
    n = 10                                     # integrate on a 10 times finer grid, then keep every 10th point
    t = np.arange(0.0, T + dt / 2, dt / n)
    if pl["kind"] == "trapezoid":
        a = np.where(t < pl["Ta"], pl["a"], 0.0) - np.where(t >= T - pl["Ta"], pl["a"], 0.0)
    else:
        j, tj, tl, Ta = pl["j"], pl["tj"], pl["tl"], pl["Ta"]

        def half(s):          # acceleration while speeding up, s = time since the phase started
            return np.where(s < tj, j * s, np.where(s < tj + tl, j * tj, np.where(s < Ta, j * (Ta - s), 0.0)))

        s = t - (T - Ta)
        a = np.where(t < Ta, half(t), 0.0) - np.where(s >= 0, half(np.clip(s, 0, None)), 0.0)
    h = dt / n
    v = np.concatenate([[0.0], np.cumsum(0.5 * (a[1:] + a[:-1]) * h)])
    x = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * h)])
    return t[::n], a[::n], v[::n], x[::n]


# %% [markdown]
# ## Step 2: the physics of the cable-counterweight system
# The car (with its passengers) and the counterweight hang on one rope over the motor sheave. They
# move together, so the total mass M = m_car + m_load + m_cw is what accelerates. The motor force F
# on the rope has to carry the unbalanced weight and accelerate M:
# F = (m_car + m_load - m_cw) g + M a.   The mechanical power is F v.
# When F v is negative the motor is being driven (heavy car going down, or light car going up) and
# can feed energy back: **regeneration**, at efficiency eta.

# %%
def rope_force(m_load, a, lift=LIFT):
    """Motor force (N) on the rope for car acceleration a (m/s^2), upward positive."""
    unbalance = lift["m_car"] + m_load - lift["m_cw"]
    total = lift["m_car"] + m_load + lift["m_cw"]
    return unbalance * G + total * a


def electrical_power(F, v, eta):
    """Electrical power (W) drawn (positive) or fed back (negative) for rope force F and speed v."""
    p = F * v
    return p / eta if p >= 0 else p * eta


# %% [markdown]
# ## Step 3: simulate the ride with a torque limit
# The controller asks for the force that would follow the plan:
# a_cmd = a_plan + kv (v_plan - v) + kp (x_plan - x). The motor cannot give more than F_max (its
# torque limit divided by the sheave radius) and its force builds up with the time constant tau.
# We step the equations forward with dt = 1 ms.

# %%
def simulate(d, m_load, pl, F_max=40000.0, lift=LIFT, dt=0.001):
    """Simulate one ride of signed distance d (m, negative = down). Returns a results dict."""
    sign = 1.0 if d >= 0 else -1.0
    t_ref, a_ref, v_ref, x_ref = reference(pl, dt)
    unbalance = (lift["m_car"] + m_load - lift["m_cw"]) * G
    total = lift["m_car"] + m_load + lift["m_cw"]
    n_end = len(t_ref) + int(10.0 / dt)         # allow up to 10 s of catching up after the plan ends
    x = np.zeros(n_end)
    v = np.zeros(n_end)
    F = np.zeros(n_end)
    F[0] = float(np.clip(unbalance, -F_max, F_max))   # the brake/motor holds the unbalanced weight
    n = n_end
    for i in range(n_end - 1):
        if i < len(t_ref):
            ar, vr, xr = a_ref[i], v_ref[i], x_ref[i]
        else:                                   # plan finished: hold the target position
            ar, vr, xr = 0.0, 0.0, abs(d)
        a_cmd = sign * ar + lift["kv"] * (sign * vr - v[i]) + lift["kp"] * (sign * xr - x[i])
        F_cmd = max(-F_max, min(F_max, unbalance + total * a_cmd))
        F[i + 1] = max(-F_max, min(F_max, F[i] + (F_cmd - F[i]) * dt / lift["tau"]))
        a_i = (F[i] - unbalance) / total
        v[i + 1] = v[i] + a_i * dt
        x[i + 1] = x[i] + 0.5 * (v[i] + v[i + 1]) * dt
        if i > len(t_ref) and abs(x[i + 1] - d) < 0.002 and abs(v[i + 1]) < 0.02:
            n = i + 2
            break
    x, v, F = x[:n], v[:n], F[:n]
    t = np.arange(n) * dt
    a = (F - unbalance) / total
    jerk = np.gradient(a, dt)
    P_mech = F * v
    P_el = np.where(P_mech >= 0, P_mech / lift["eta"], P_mech * lift["eta"])
    return dict(t=t, x=x, v=v, a=a, jerk=jerk, F=F, P_mech=P_mech, P_el=P_el,
                time=float(t[-1]), peak_a=float(np.abs(a).max()), peak_jerk=float(np.abs(jerk).max()),
                saturated=bool(np.any(np.abs(F) >= F_max - 1e-6)), dt=dt, d=d, m_load=m_load)


# %% [markdown]
# ## Step 4: measure comfort and energy, and validate
# Comfort here = peak |acceleration| and peak |jerk| actually produced. Energy: the net work the motor
# does must equal the change in potential energy of the unbalanced mass, because the speed starts and
# ends at zero: integral of F v dt = (m_car + m_load - m_cw) g d.

# %%
def energies(res):
    """(drawn from the grid, fed back, net) in joules, and the net mechanical work (J)."""
    p, dt = res["P_el"], res["dt"]
    drawn = float(np.sum(p[p > 0]) * dt)
    back = float(-np.sum(p[p < 0]) * dt)
    work = float(np.sum(0.5 * (res["P_mech"][1:] + res["P_mech"][:-1])) * dt)
    return drawn, back, drawn - back, work


def comfort_score(peak_a, peak_jerk, a_lim=1.2, j_lim=2.5):
    """Larger of the two ratios to the comfort limits; <= 1 means comfortable (assumed limits)."""
    return max(peak_a / a_lim, peak_jerk / j_lim)


def sensitivity(loads, cw_values, d, pl, F_max=40000.0):
    """Net energy (kJ) for each (counterweight, load) pair. Rows: cw values, columns: loads."""
    table = np.zeros((len(cw_values), len(loads)))
    for r, cw in enumerate(cw_values):
        lift = dict(LIFT, m_cw=cw)
        for c, ml in enumerate(loads):
            table[r, c] = energies(simulate(d, ml, pl, F_max, lift))[2] / 1000.0
    return table


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    d, vmax, amax, jmax = 31.5, 2.5, 1.0, 1.5
    for pl in (plan(d, vmax, amax), plan(d, vmax, amax, jmax)):
        r = simulate(d, 400.0, pl)
        print(f"{pl['kind']:9s} formula T = {pl['T']:.3f} s, simulated {r['time']:.3f} s, "
              f"peak a {r['peak_a']:.2f} m/s^2, peak jerk {r['peak_jerk']:.2f} m/s^3")
    fig, ax = plt.subplots(3, 1, figsize=(6.4, 6.4), sharex=True)
    for pl, col in ((plan(d, vmax, amax), "tab:red"), (plan(d, vmax, amax, jmax), "tab:blue")):
        r = simulate(d, 400.0, pl)
        ax[0].plot(r["t"], r["v"], color=col, label=pl["kind"])
        ax[1].plot(r["t"], r["a"], color=col)
        ax[2].plot(r["t"], r["jerk"], color=col)
    ax[0].set_ylabel("speed (m/s)")
    ax[1].set_ylabel("acceleration (m/s^2)")
    ax[2].set_ylabel("jerk (m/s^3)")
    ax[2].set_xlabel("time (s)")
    ax[0].legend()
    ax[0].set_title("Simulated ride, 31.5 m, half load")
    for a_ in ax:
        a_.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "two_profiles.png", dpi=120)

    # energy against load, for two counterweights, going up and down
    loads = np.linspace(0, 800, 9)
    pl = plan(d, vmax, amax, jmax)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for cw in (1000.0, 1360.0):
        for sgn, ls in ((1, "-"), (-1, "--")):
            lift = dict(LIFT, m_cw=cw)
            e = [energies(simulate(sgn * d, m, pl, 40000.0, lift))[2] / 1000 for m in loads]
            ax2.plot(loads, e, ls, label=f"cw {cw:.0f} kg, {'up' if sgn > 0 else 'down'}")
    ax2.axhline(0, color="gray", lw=0.8)
    ax2.set_xlabel("passenger load (kg)")
    ax2.set_ylabel("net energy from the grid (kJ)")
    ax2.set_title("Heavy-down trips give energy back (negative)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "energy_vs_load.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
