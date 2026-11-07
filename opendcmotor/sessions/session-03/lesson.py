"""Session 3 (Level 3): simulate a DC motor in time, validate it, control it with PWM, and size a robot drive.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a motor in time
# **A. Real-world problem.** A real motor does not jump to its steady speed. Switch it on and the
# current spikes first (the rotor is still, so there is no back voltage), then the speed climbs,
# and the current falls. A robot also controls speed by switching the voltage on and off
# quickly (PWM). Can we simulate all of this, trust the simulation, and use it to size a motor
# and gearbox for a robot that must climb a slope?
#
# **Plan.** (1) write the two coupled equations, (2) solve them with RK4, (3) check against the
# Session 2 line and against energy conservation, (4) add PWM, a current limit and a stall case,
# (5) size a robot drive.
#
# *Low-voltage educational model only: a simplified lumped model, not a design tool. Never
# connect a real motor, battery or driver based on this lesson alone.*

# %%
import math
import pathlib

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# example motor (same as Session 2) plus inductance and load inertia
P = {"V": 12.0, "R": 2.0, "L": 5e-3, "k": 0.05, "b": 5e-5, "J": 2e-4}


# %% [markdown]
# ## Step 1: the two coupled equations
# Electrical: `L di/dt = V - R i - k w`. Mechanical: `J dw/dt = k i - b w - T_load`.
# L (henry) is the winding inductance, J (kg m^2) the rotor plus load inertia, b (N m s/rad)
# viscous friction, T_load (N m) the load torque. To check energy we also integrate four
# powers along with the state: electrical input `V i`, resistor heat `R i^2`, friction heat
# `b w^2` and load work `T_load w`.

# %%
def tau_e(R=P["R"], L=P["L"]):
    """Electrical time constant L / R (s)."""
    return L / R


def tau_m(R=P["R"], k=P["k"], b=P["b"], J=P["J"]):
    """Mechanical time constant approximation J R / (k^2 + b R) (s); valid when tau_e << tau_m."""
    return J * R / (k * k + b * R)


def steady_state(V=P["V"], T_load=0.0, R=P["R"], k=P["k"], b=P["b"]):
    """(speed rad/s, current A) where both derivatives are zero."""
    w = (k * V / R - T_load) / (k * k / R + b)
    return w, (T_load + b * w) / k


def derivs(y, V, T_load, par):
    """Right-hand side of the coupled equations plus the four power integrals."""
    i, w = y[0], y[1]
    if par.get("I_lim") is not None:               # ideal current limiter: never push more than I_lim
        V = min(V, par["k"] * w + par["R"] * par["I_lim"])
    di = (V - par["R"] * i - par["k"] * w) / par["L"]
    dw = (par["k"] * i - par["b"] * w - T_load) / par["J"]
    return (di, dw, V * i, par["R"] * i * i, par["b"] * w * w, T_load * w)


# %% [markdown]
# ## Step 2: RK4
# Runge-Kutta 4 takes four slope samples per step and combines them; the error shrinks with
# the fourth power of the step. The voltage is held constant during each step (so PWM edges
# must fall on step boundaries).

# %%
def rk4_step(y, V, T_load, dt, par):
    k1 = derivs(y, V, T_load, par)
    k2 = derivs([a + 0.5 * dt * d for a, d in zip(y, k1)], V, T_load, par)
    k3 = derivs([a + 0.5 * dt * d for a, d in zip(y, k2)], V, T_load, par)
    k4 = derivs([a + dt * d for a, d in zip(y, k3)], V, T_load, par)
    return [a + dt / 6.0 * (d1 + 2 * d2 + 2 * d3 + d4) for a, d1, d2, d3, d4 in zip(y, k1, k2, k3, k4)]


def simulate(t_end, dt, V=None, T_load=0.0, par=None, y0=None, record_every=1):
    """Simulate the motor. V is a number or a list of voltages, one per step; T_load a number
    or a function of time. Returns dict with t, i, w and the energy integrals."""
    par = dict(P, **(par or {}))
    n = int(round(t_end / dt))
    volts = [par["V"]] * n if V is None else ([V] * n if isinstance(V, (int, float)) else list(V))
    y = list(y0) if y0 is not None else [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    out = {key: [] for key in ("t", "i", "w", "E_in", "E_R", "E_b", "E_load")}
    for s in range(n + 1):
        if s % record_every == 0 or s == n:
            for key, val in zip(out, (s * dt, y[0], y[1], y[2], y[3], y[4], y[5])):
                out[key].append(val)
        if s == n:
            break
        tl = T_load(s * dt) if callable(T_load) else T_load
        y = rk4_step(y, volts[s], tl, dt, par)
    return out


def energy_residual(sim, par=None):
    """Electrical in minus (heat + friction + load work + kinetic + magnetic), in joules, at the end."""
    par = dict(P, **(par or {}))
    stored = 0.5 * par["J"] * sim["w"][-1] ** 2 + 0.5 * par["L"] * sim["i"][-1] ** 2
    return sim["E_in"][-1] - (sim["E_R"][-1] + sim["E_b"][-1] + sim["E_load"][-1] + stored)


def time_to_fraction(sim, frac, w_final=None):
    """First time the speed reaches frac of w_final (default: the last speed), by linear interpolation."""
    target = frac * (sim["w"][-1] if w_final is None else w_final)
    for j in range(1, len(sim["t"])):
        if sim["w"][j] >= target:
            f = (target - sim["w"][j - 1]) / (sim["w"][j] - sim["w"][j - 1])
            return sim["t"][j - 1] + f * (sim["t"][j] - sim["t"][j - 1])
    return float("nan")


# %% [markdown]
# ## Step 3: PWM, current limit, stall
# PWM switches the supply fully on for a fraction D (the duty cycle) of each period and off for
# the rest. The motor averages it: mean voltage `D V`. The ripple is small when the period is
# short against both time constants. Stalling is the worst case: speed 0, current V/R, and
# heat `R i^2` with nowhere to go.

# %%
def pwm_sequence(D, f_pwm, dt, t_end, V=P["V"]):
    """Per-step voltage list for a PWM wave (duty D, frequency f_pwm in Hz); edges on step boundaries."""
    steps_per_period = int(round(1.0 / (f_pwm * dt)))
    on_steps = int(round(D * steps_per_period))
    n = int(round(t_end / dt))
    return [V if (s % steps_per_period) < on_steps else 0.0 for s in range(n)]


def pwm_run(D, f_pwm=1000.0, T_load=0.0, dt=2e-5, t_settle=0.6, t_measure=0.05):
    """Run PWM to near periodic steady state, then measure mean speed and ripple over t_measure."""
    mean_v = D * P["V"]
    w0, i0 = steady_state(mean_v, T_load)
    seq = pwm_sequence(D, f_pwm, dt, t_settle + t_measure)
    sim = simulate(t_settle + t_measure, dt, V=seq, T_load=T_load, y0=[i0, w0, 0, 0, 0, 0])
    m0 = int(round(t_settle / dt))
    w, i = sim["w"][m0:], sim["i"][m0:]
    return {"w_mean": sum(w) / len(w), "w_ripple": max(w) - min(w), "i_mean": sum(i) / len(i), "i_ripple": max(i) - min(i)}


def locked_rotor_current(t, V=P["V"], R=P["R"], L=P["L"]):
    """Current (A) of a locked rotor (w = 0) t seconds after switch-on: (V / R)(1 - exp(-t R / L))."""
    return V / R * (1.0 - math.exp(-t * R / L))


def stall_heat(V=P["V"], R=P["R"]):
    """Heat in the winding at stall (W): I^2 R with I = V / R."""
    return (V / R) ** 2 * R


def time_to_heat(delta_T, power, C_th=15.0):
    """Seconds to warm by delta_T kelvin with no cooling; C_th (J/K) is an assumed heat capacity."""
    return C_th * delta_T / power


# %% [markdown]
# ## Step 4: size a robot wheel drive
# A robot of mass m climbs a slope of angle theta on two driven wheels of radius r. The force
# along the slope is `m g (sin theta + c cos theta)`, c being the rolling-resistance coefficient. Each wheel
# needs torque `F r / n`; the gearbox (ratio N, efficiency eta) turns it into a motor torque,
# and Session 2's steady-state line gives speed and current. `window` lists every ratio that
# meets the speed, current and starting-margin limits.

# %%
ROBOT = {"m": 8.0, "r": 0.05, "c": 0.03, "n": 2, "eta": 0.9}


def wheel_drive(N, slope_deg, V=P["V"], robot=None):
    """Steady climb with gear ratio N: dict(v m/s, current A, start margin, efficiency, ok)."""
    rb = dict(ROBOT, **(robot or {}))
    g = 9.81
    th = math.radians(slope_deg)
    F = rb["m"] * g * (math.sin(th) + rb["c"] * math.cos(th))
    T_wheel = F * rb["r"] / rb["n"]
    T_m = T_wheel / (N * rb["eta"])
    k, R, b = P["k"], P["R"], P["b"]
    a = k * k / R + b
    w_m = (k * V / R - T_m) / a
    if w_m <= 0:
        return {"v": 0.0, "current": V / R, "start": N * rb["eta"] * k * V / R / T_wheel, "eff": 0.0, "T_m": T_m, "w_m": 0.0, "F": F}
    I = (T_m + b * w_m) / k
    return {"v": w_m / N * rb["r"], "current": I, "start": N * rb["eta"] * k * V / R / T_wheel,
            "eff": T_wheel * (w_m / N) / (V * I), "T_m": T_m, "w_m": w_m, "F": F}


def window(slope_deg, v_min=0.5, I_max=1.5, start_min=1.5, ratios=range(2, 101), V=P["V"], robot=None):
    """Ratios that climb at >= v_min m/s, draw <= I_max A and start with margin >= start_min; best by efficiency."""
    good = []
    for N in ratios:
        d = wheel_drive(N, slope_deg, V, robot)
        if d["v"] >= v_min and d["current"] <= I_max and d["start"] >= start_min:
            good.append((N, d))
    if not good:
        return [], None
    return [g[0] for g in good], max(good, key=lambda g: g[1]["eff"])[0]


def climb_sim(N, slope_deg, V=P["V"], robot=None, t_end=0.6, dt=1e-4):
    """Time-domain climb from rest: returns (final speed m/s, time to 90 percent of it in s).
    The robot's mass is reflected to each motor shaft as extra inertia m r^2 / (n N^2)."""
    rb = dict(ROBOT, **(robot or {}))
    d = wheel_drive(N, slope_deg, V, robot)
    J_eq = 2e-5 + rb["m"] * rb["r"] ** 2 / (rb["n"] * N * N)
    sim = simulate(t_end, dt, V=V, T_load=d["T_m"], par={"V": V, "J": J_eq})
    v_end = sim["w"][-1] / N * rb["r"]
    return v_end, time_to_fraction(sim, 0.9)


def steepest_slope(v_min=0.5, I_max=1.5, V=P["V"], robot=None):
    """Largest whole-degree slope for which some ratio meets all limits."""
    best = 0
    for deg in range(0, 60):
        if window(deg, v_min, I_max, V=V, robot=robot)[0]:
            best = deg
    return best


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"tau_e = {tau_e()*1000:.2f} ms, tau_m approx = {tau_m()*1000:.1f} ms")
    # (a) step response, no load
    sim = simulate(1.0, 1e-4, V=12.0)
    w_ss, i_ss = steady_state(12.0)
    print(f"step: final speed {sim['w'][-1]:.2f} rad/s (steady formula {w_ss:.2f}), final current {sim['i'][-1]:.3f} A ({i_ss:.3f}), peak current {max(sim['i']):.2f} A")
    t63 = time_to_fraction(sim, 1 - math.exp(-1), w_final=w_ss)
    print(f"time to 63.2 percent of final speed: {t63*1000:.1f} ms (tau_m approx {tau_m()*1000:.1f} ms)")
    print(f"energy residual at the end: {energy_residual(sim):.2e} J (input {sim['E_in'][-1]:.2f} J)")
    # (b) convergence
    ref = simulate(0.3, 5e-5, V=12.0)["w"][-1]
    errs = [abs(simulate(0.3, d, V=12.0)["w"][-1] - ref) for d in (2e-3, 1e-3, 5e-4)]
    print("RK4 errors at dt = 2, 1, 0.5 ms:", [f"{e:.2e}" for e in errs], "ratio", f"{errs[0]/errs[1]:.1f}", f"{errs[1]/errs[2]:.1f}")
    # (c) load: simulated steady state vs Session 2 line
    for tl in (0.0, 0.1, 0.2, 0.3):
        s = simulate(1.5, 2e-4, V=12.0, T_load=tl)
        print(f"load {tl:.2f} N m: sim {s['w'][-1]:7.2f} rad/s, line {steady_state(12.0, tl)[0]:7.2f} rad/s")
    # (d) current limit
    lim = simulate(0.6, 1e-4, V=12.0, par={"I_lim": 3.0})
    print(f"inrush: unlimited peak {max(sim['i']):.2f} A, V/R = {12.0/2.0:.1f} A; limited to 3 A peak {max(lim['i']):.2f} A; "
          f"time to 90 percent speed {time_to_fraction(lim, 0.9, w_ss)*1000:.0f} ms against {time_to_fraction(sim, 0.9, w_ss)*1000:.0f} ms")
    # (e) PWM
    for D in (0.2, 0.5, 0.8, 1.0):
        r = pwm_run(D)
        print(f"PWM D={D:.2f} (hand ripple D(1-D)V/(L f) = {D*(1-D)*12.0/(5e-3*1000.0):.3f} A): mean speed {r['w_mean']:6.2f} rad/s (D V line {steady_state(D*12.0)[0]:6.2f}), speed ripple {r['w_ripple']:.3f} rad/s, current ripple {r['i_ripple']:.3f} A")
    # (f) stall
    print(f"stall: {stall_heat():.0f} W in the winding; +100 K in {time_to_heat(100.0, stall_heat()):.1f} s (assumed C_th 15 J/K, no cooling); at 6 V {stall_heat(6.0):.0f} W")
    # (g) robot
    for deg in (0, 10, 20, 30, 35):
        ws, best = window(deg)
        print(f"slope {deg:2d} deg: ratios {ws[0] if ws else '-'} to {ws[-1] if ws else '-'}, best {best}")
    for dg in (20, 30):
        vv, t90 = climb_sim(16 if dg == 20 else 18, dg)
        print(f"climb simulation at {dg} deg: final speed {vv:.3f} m/s (steady formula {wheel_drive(16 if dg == 20 else 18, dg)['v']:.3f}), 90 percent after {t90*1000:.0f} ms")
    lk = simulate(0.03, 1e-5, par={"J": 1e6})
    print(f"locked rotor: simulated current {lk['i'][-1]:.3f} A, formula {locked_rotor_current(0.03):.3f} A, heat power {stall_heat():.0f} W")
    print("steepest slope with a feasible ratio:", steepest_slope(), "degrees")
    d = wheel_drive(16, 20)
    print(f"N=16 at 20 deg: v {d['v']:.3f} m/s, current {d['current']:.3f} A, start margin {d['start']:.2f}, efficiency {d['eff']:.3f}")

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot([x * 1000 for x in sim["t"]], sim["w"], color="tab:blue", label="speed (rad/s)")
    ax[0].axhline(w_ss, color="gray", ls=":", label="steady state")
    ax[0].set_xlim(0, 800)
    ax[0].set_xlabel("time (ms)")
    ax[0].set_ylabel("speed (rad/s)")
    ax[0].set_title("Step response of the motor")
    ax[0].grid(alpha=0.3)
    ax[0].legend(loc="center right", fontsize=8)
    ax1 = ax[0].twinx()
    ax1.plot([x * 1000 for x in sim["t"]], sim["i"], color="tab:red")
    ax1.set_ylabel("current (A), red")
    s2 = simulate(0.05, 2e-5, V=pwm_sequence(0.5, 1000.0, 2e-5, 0.05), record_every=5)
    ax[1].plot([x * 1000 for x in s2["t"]], s2["i"], color="tab:red", lw=0.8, label="current (A)")
    ax[1].set_xlabel("time (ms)")
    ax[1].set_ylabel("current (A)")
    ax[1].set_title("PWM at D = 0.5, 1 kHz: current ripples")
    ax[1].grid(alpha=0.3)
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "step_and_pwm.png", dpi=120)

    degs = list(range(0, 41, 2))
    ratios = list(range(4, 41))
    grid = [[1.0 if (wheel_drive(N, dg)["v"] >= 0.5 and wheel_drive(N, dg)["current"] <= 1.5) else 0.0 for N in ratios] for dg in degs]
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.imshow(grid, origin="lower", aspect="auto", extent=[ratios[0] - 0.5, ratios[-1] + 0.5, degs[0] - 1, degs[-1] + 1], cmap="Greens", vmin=0, vmax=1.5)
    ax2.set_xlabel("gear ratio N")
    ax2.set_ylabel("slope (degrees)")
    ax2.set_title("Green: speed >= 0.5 m/s and current <= 1.5 A")
    fig2.tight_layout()
    fig2.savefig(OUT / "sizing_sweep.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
