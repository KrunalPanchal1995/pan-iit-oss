"""Session 3 (Level 3): a lumped crumple-zone model, solved in time and checked against theory.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a crumple zone you can simulate
# **A. Real-world problem.** Real crumple zones do not push back with one constant force.
# The front first resists more and more, then collapses at a roughly steady force (the
# *plateau*), and if it is used up the stiff passenger cell is next, with a sudden jump in force.
# Today you model the car as one lump of mass pushing into a crumple "spring" with a
# force-displacement curve, step it through time, and check the answer against two exact
# results: the constant-force formula from Session 2 and the energy balance.
# Then you crash two cars into each other and make the crumple zone fail on purpose.
#
# **Plan.** (1) the force curve, (2) a time stepper (RK4), (3) validate against theory,
# (4) energy balance, (5) two cars, (6) sensitivity and the "bottoming out" failure.
#
# *Simplified educational model: one lump, one dimension, no rebound, no occupant, no injury
# prediction. It is not a crashworthiness design tool.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81            # m/s^2
XR = 0.05           # m, length of the rising part of the force curve
K_CELL = 3.0e7      # N/m, stiffness of the passenger cell once the crumple zone is used up


def kmh_to_ms(v_kmh):
    return v_kmh / 3.6


# %% [markdown]
# ## Step 1: the force-displacement curve
# `x` is how far the front has been crushed (m). The crumple zone resists with force F(x):
#
# * 0 <= x < XR: a straight ramp from 0 up to the plateau force Fp,
# * XR <= x <= Lc: the constant plateau Fp (the crumple zone collapsing),
# * x > Lc: the crumple length is used up, the stiff cell acts like a very hard spring:
#   F = Fp + K_CELL * (x - Lc).
#
# The area under this curve up to x is the work done, the energy absorbed.

# %%
def crumple_force(x, Fp, Lc, xr=XR, k_cell=K_CELL):
    """Resisting force (N) at crush distance x (m)."""
    x = np.asarray(x, dtype=float)
    ramp = Fp * np.clip(x / xr, 0.0, 1.0)
    over = np.maximum(x - Lc, 0.0)
    return np.where(x <= 0.0, 0.0, ramp + k_cell * over)


def work_to(x, Fp, Lc, xr=XR, k_cell=K_CELL):
    """Exact area under the force curve from 0 to x (J), worked out by hand-integration."""
    x = float(x)
    if x <= 0.0:
        return 0.0
    if x <= xr:
        return 0.5 * Fp * x * x / xr
    w = 0.5 * Fp * xr + Fp * (min(x, Lc) - xr)
    if x > Lc:
        w += Fp * (x - Lc) + 0.5 * k_cell * (x - Lc) ** 2
    return w


# %% [markdown]
# ## Step 2: step through time (RK4)
# Newton's law: m dv/dt = -(F(x) + c v), dx/dt = v, where c is an optional damping
# coefficient (N s/m, default 0). We also integrate the work done by the spring, the energy
# lost in the damper and the impulse, so we can audit the energy afterwards.
# RK4 (fourth-order Runge-Kutta) takes four slope samples per step. When the speed would cross
# zero inside a step, the step is shortened so the car stops exactly at v = 0.

# %%
def _force_scalar(x, Fp, Lc, xr, k_cell):
    """Same curve as crumple_force, for one number (fast path inside the time loop)."""
    if x <= 0.0:
        return 0.0
    f = Fp * min(x / xr, 1.0)
    return f + k_cell * (x - Lc) if x > Lc else f


def _rhs(y, m, Fp, Lc, xr, k_cell, c):
    x, v = y[0], y[1]
    f = _force_scalar(x, Fp, Lc, xr, k_cell)
    r = f + c * v
    return np.array([v, -r / m, f * v, c * v * v, r])


def _rk4(y, h, args):
    k1 = _rhs(y, *args)
    k2 = _rhs(y + 0.5 * h * k1, *args)
    k3 = _rhs(y + 0.5 * h * k2, *args)
    k4 = _rhs(y + h * k3, *args)
    return y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0


def simulate_crash(m, v0, Fp, Lc, xr=XR, k_cell=K_CELL, c=0.0, dt=1e-4):
    """Crash a mass m (kg) at speed v0 (m/s) into a rigid barrier through a crumple zone.

    Returns a dict with arrays t, x, v, a_g (deceleration in g) and the summary numbers
    peak_g, stop_distance, stop_time, KE0, W_spring, W_damper, KE_end, impulse.
    """
    args = (m, Fp, Lc, xr, k_cell, c)
    y = np.array([0.0, v0, 0.0, 0.0, 0.0])
    t = 0.0
    T, Y = [t], [y.copy()]
    while y[1] > 0.0 and t < 2.0:
        new = _rk4(y, dt, args)
        if new[1] <= 0.0:                      # the car stops inside this step: shorten it
            h = dt * y[1] / (y[1] - new[1])
            new = _rk4(y, h, args)
            new[1] = 0.0
            dt_used = h
        else:
            dt_used = dt
        y, t = new, t + dt_used
        T.append(t)
        Y.append(y.copy())
    Y = np.array(Y)
    T = np.array(T)
    force = crumple_force(Y[:, 0], Fp, Lc, xr, k_cell) + c * Y[:, 1]
    a_g = force / m / G
    return {
        "t": T, "x": Y[:, 0], "v": Y[:, 1], "a_g": a_g, "force": force,
        "peak_g": float(a_g.max()), "stop_distance": float(Y[-1, 0]), "stop_time": float(T[-1]),
        "KE0": 0.5 * m * v0 * v0, "W_spring": float(Y[-1, 2]), "W_damper": float(Y[-1, 3]),
        "KE_end": 0.5 * m * float(Y[-1, 1]) ** 2, "impulse": float(Y[-1, 4]),
    }


# %% [markdown]
# ## Step 3: validate against the exact constant-force answer
# If the crash stops on the plateau, the energy balance is exactly
#
#     KE0 = (1/2) Fp XR + Fp (d - XR)   =>   d = KE0 / Fp + XR / 2,   peak decel = Fp / m.
#
# The simulation must reproduce these numbers.

# %%
def analytic_plateau(m, v0, Fp, xr=XR):
    """Exact (stop distance m, peak deceleration in g, stop time s) when the crash ends on the plateau."""
    ke = 0.5 * m * v0 * v0
    d = ke / Fp + 0.5 * xr
    w = np.sqrt(Fp / (m * xr))                     # on the ramp the motion is x = (v0 / w) sin(w t)
    t1 = np.arcsin(w * xr / v0) / w                # time to reach the end of the ramp
    v1 = v0 * np.cos(w * t1)                       # speed there
    t_stop = t1 + m * v1 / Fp                      # then constant force Fp: t = m v / Fp
    return d, Fp / m / G, float(t_stop)


# %%
# %% [markdown]
# ## Step 4: the energy balance (the audit)
# Every joule must be accounted for:  KE0 = crumple work + damper loss + residual KE.
# Here "crumple work" is the work done by the force curve up to the crush distance.

# %%
def energy_balance(res):
    """Return (KE0, W_spring + W_damper + KE_end, relative error)."""
    total = res["W_spring"] + res["W_damper"] + res["KE_end"]
    return res["KE0"], total, abs(total - res["KE0"]) / res["KE0"]


def split_work(res, Fp, Lc, xr=XR, k_cell=K_CELL):
    """Work done in the crumple zone (x <= Lc) and in the stiff cell (x > Lc), in joules."""
    x_end = res["stop_distance"]
    w_crumple = work_to(min(x_end, Lc), Fp, Lc, xr, k_cell)
    return w_crumple, work_to(x_end, Fp, Lc, xr, k_cell) - w_crumple


# %% [markdown]
# ## Step 5: two cars (momentum and relative speed)
# Two cars meet head on. Momentum is conserved (Newton's third law: equal and opposite
# forces for the same time). If they lock together (perfectly inelastic), the common final
# velocity is  vf = (m1 v1 + m2 v2) / (m1 + m2)  and the energy that must be crushed is
# (1/2) mu v_rel^2, with mu = m1 m2 / (m1 + m2) and v_rel the relative speed.
# We simulate it as ONE crash of the reduced mass mu at the relative speed, through the two
# crumple zones in series (same force in both, lengths add). Car 1 moves in +x, car 2 in -x.

# %%
def two_car_collision(m1, v1, m2, v2, Fp, Lc1, Lc2):
    """Head-on crash of car 1 (speed v1 > 0) and car 2 (speed v2 < 0 if oncoming; v2 > 0 if it is
    driving the same way, slower). Returns a dict with final velocities, energy and peak g of each car."""
    mu = m1 * m2 / (m1 + m2)
    v_rel = v1 - v2
    res = simulate_crash(mu, v_rel, Fp, Lc1 + Lc2)
    j = res["impulse"]                       # impulse of the contact force (N s)
    v1f = v1 - j / m1
    v2f = v2 + j / m2
    return {
        "v_rel": v_rel, "mu": mu, "impulse": j, "v1_final": v1f, "v2_final": v2f,
        "p_before": m1 * v1 + m2 * v2, "p_after": m1 * v1f + m2 * v2f,
        "KE_lost": 0.5 * mu * v_rel ** 2, "peak_g1": res["peak_g"] * mu / m1, "peak_g2": res["peak_g"] * mu / m2,
        "stop_distance": res["stop_distance"], "result": res,
    }


# %% [markdown]
# ## Step 6: sensitivity and the failure case
# Peak deceleration is Fp / m, so it scales with the plateau force and falls with mass.
# If Lc is too short the plateau is used up before the car stops, the stiff cell takes over
# and a second, much larger spike appears: the crumple zone has "bottomed out".

# %%
def sweep_plateau(m, v0, Lc, forces):
    """Peak deceleration (g) and stop distance (m) for a list of plateau forces (N)."""
    rows = []
    for f in forces:
        r = simulate_crash(m, v0, f, Lc)
        rows.append((f, r["peak_g"], r["stop_distance"]))
    return rows


def bottomed_out(res, Lc):
    return res["stop_distance"] > Lc + 1e-9


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m, v0 = 1000.0, kmh_to_ms(56.0)
    Fp, Lc = 200e3, 0.8
    res = simulate_crash(m, v0, Fp, Lc)
    d_ref, g_ref, t_ref = analytic_plateau(m, v0, Fp)
    print(f"56 km/h = {v0:.3f} m/s, KE0 = {res['KE0'] / 1000:.2f} kJ")
    print(f"simulated: stop {res['stop_distance']:.4f} m in {res['stop_time'] * 1000:.1f} ms, peak {res['peak_g']:.3f} g")
    print(f"analytic : stop {d_ref:.4f} m in {t_ref * 1000:.1f} ms, peak {g_ref:.3f} g")
    ke0, tot, err = energy_balance(res)
    print(f"energy: KE0 {ke0:.1f} J = spring {res['W_spring']:.1f} + damper {res['W_damper']:.1f} + KE_end {res['KE_end']:.3f}; error {err:.2e}")
    print(f"momentum: impulse {res['impulse']:.1f} N s vs m v0 {m * v0:.1f} N s")

    # time step check (convergence)
    for dt in (1e-3, 1e-4, 1e-5):
        r = simulate_crash(m, v0, Fp, Lc, dt=dt)
        print(f"dt {dt:g}: stop distance error {abs(r['stop_distance'] - d_ref):.2e} m")

    # two cars
    for label, args in (("equal, head-on 56 km/h each", (1000, v0, 1000, -v0)),
                        ("1500 kg vs 750 kg, head-on 56 km/h each", (1500, v0, 750, -v0))):
        out = two_car_collision(*args, Fp, 0.7, 0.7)
        print(f"{label}: v_final {out['v1_final']:.3f} / {out['v2_final']:.3f} m/s, KE lost {out['KE_lost'] / 1000:.1f} kJ, "
              f"peak g {out['peak_g1']:.1f} / {out['peak_g2']:.1f}, momentum {out['p_before']:.1f} -> {out['p_after']:.1f}")

    # sensitivity to plateau force
    rows = sweep_plateau(m, v0, 0.9, [150e3, 200e3, 250e3, 300e3])
    for f, pg, d in rows:
        print(f"Fp {f / 1000:.0f} kN: peak {pg:.1f} g, stop {d:.3f} m")

    # failure case
    bad = simulate_crash(m, v0, 250e3, 0.35)
    print(f"short zone Lc 0.35 m, Fp 250 kN: stop {bad['stop_distance']:.3f} m, peak {bad['peak_g']:.1f} g, bottomed out {bottomed_out(bad, 0.35)}")

    # Figure 1: force-displacement curve and the deceleration trace
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.9))
    xs = np.linspace(0, 0.9, 400)
    a1.plot(xs, crumple_force(xs, Fp, Lc) / 1000)
    a1.fill_between(xs[xs <= res["stop_distance"]], crumple_force(xs[xs <= res["stop_distance"]], Fp, Lc) / 1000, alpha=0.25,
                    label=f"area = energy absorbed = {res['W_spring'] / 1000:.0f} kJ")
    a1.set_xlabel("crush distance x (m)")
    a1.set_ylabel("resisting force F (kN)")
    a1.set_title("Force-displacement curve of the front")
    a1.legend(fontsize=8)
    a1.grid(alpha=0.3)
    a2.plot(res["t"] * 1000, res["a_g"], label="good design (stops on plateau)")
    a2.plot(bad["t"] * 1000, bad["a_g"], color="C3", label="Lc too short: bottoms out")
    a2.set_xlabel("time (ms)")
    a2.set_ylabel("deceleration (g)")
    a2.set_title("Deceleration trace")
    a2.legend(fontsize=8)
    a2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "force_and_trace.png", dpi=120)

    # Figure 2: simulation versus analytic, and energy split
    fig2, (b1, b2) = plt.subplots(1, 2, figsize=(10, 3.9))
    fs = np.linspace(120e3, 400e3, 29)
    sim_d = [simulate_crash(m, v0, f, 1.2)["stop_distance"] for f in fs]
    b1.plot(fs / 1000, [analytic_plateau(m, v0, f)[0] for f in fs], "-", label="analytic KE0/Fp + XR/2")
    b1.plot(fs / 1000, sim_d, "o", ms=4, label="RK4 simulation")
    b1.set_xlabel("plateau force Fp (kN)")
    b1.set_ylabel("stopping distance (m)")
    b1.set_title("Simulation matches the exact answer")
    b1.legend(fontsize=8)
    b1.grid(alpha=0.3)
    wc, wcell = split_work(res, Fp, Lc)
    wc2, wcell2 = split_work(bad, 250e3, 0.35)
    b2.bar([0, 1], [wc / 1000, wc2 / 1000], label="crumple zone work", color="C1")
    b2.bar([0, 1], [wcell / 1000, wcell2 / 1000], bottom=[wc / 1000, wc2 / 1000], label="passenger cell work", color="C3")
    b2.set_xticks([0, 1])
    b2.set_xticklabels(["good design", "Lc too short"])
    b2.set_ylabel("energy absorbed (kJ)")
    b2.set_title("Where the kinetic energy went")
    b2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "validation_energy.png", dpi=120)

# %% [markdown]
# ## Mini-project: choose the crumple zone for a small car at 56 km/h
# Use `simulate_crash` for a 1000 kg car at 56 km/h into a rigid barrier. Choose the plateau
# force Fp (steps of 10 kN) and crumple length Lc (steps of 0.05 m) so that the peak
# deceleration is at most 25 g (a teaching target), Lc is at most 0.70 m (space under the
# bonnet) and the crumple zone does not bottom out. See the README for the full task.
