"""Session 3 (Level 3): simulate a plate cooled by boiling, find the burnout, and grow a bubble.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a heated plate, a boiling curve and a burnout you can reproduce
# **A. Real-world problem.** A heater plate sits in water. Turn the power up slowly and the
# plate stays just above 100 C, the water boils vigorously and all is well. Turn it up a little
# too far and, within seconds, the surface is red hot or melted. That is *burnout* (the critical
# heat flux, CHF). Can a simple model show why, and show why a thermostat that holds the wall
# temperature instead of the power never burns out?
#
# **Plan.** (1) a piecewise boiling curve q(dT) with four regimes, (2) a lumped plate whose
# temperature is stepped forward in time, (3) a check against an exact solution and against
# energy conservation, (4) the burnout run and the hysteresis loop, (5) bubble growth by
# a diffusion solver, with a log-log fit of its exponent.
#
# **Safety and scope.** Simplified teaching model, not a design tool for real heaters. The
# boiling-curve coefficients below are ILLUSTRATIVE numbers chosen to give the right shape and
# a peak near 1.1 MW per square metre; they are not a correlation fitted to a data set. Real
# surfaces differ by large factors. Never design or test real heating equipment from this model.
#
# **Assumptions.** One uniform plate temperature (lumped: thin, high conductivity); heat leaves
# through one face into saturated water at 100 C and 1 atm; the other face is insulated; the
# boiling curve is single valued in the wall superheat dT = T_wall - T_sat.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

T_SAT = 100.0          # degrees C, water at 1 atm
H_NC = 1000.0          # W/(m^2 K) illustrative natural-convection coefficient
Q_CHF = 1.1e6          # W/m^2 illustrative critical heat flux (about the well-known water value)
DT_CHF = 30.0          # K, wall superheat at the CHF for surface = 1 (illustrative)
Q_MIN = 2.5e4          # W/m^2 illustrative minimum film-boiling flux (Leidenfrost point)
DT_MIN = 120.0         # K, superheat at that minimum (illustrative)
C_PLATE = 17250.0      # J/(m^2 K) for a 5 mm copper plate: 3.45e6 J/(m^3 K) * 0.005 m
DT_LIMIT = 600.0       # K, superheat at which the plate is considered destroyed (illustrative)


# %% [markdown]
# ## Step 1: the boiling curve in four pieces
# * natural convection: `q = H_NC * dT` (no bubbles yet),
# * nucleate boiling: `q = C * dT**3`, where `C = Q_CHF / DT_CHF**3 * surface`, up to the CHF,
# * transition boiling: flux falls from the CHF to the minimum, straight on a log scale,
# * film boiling: a vapour blanket, `q = Q_MIN * dT / DT_MIN`, rising slowly.
#
# `surface` scales the nucleate coefficient (1 = reference, 0.6 = a fouled, less active surface,
# 1.5 = a rougher, more active one). A smaller `surface` pushes the peak to a higher superheat.

# %%
def nucleate_coeff(surface=1.0):
    """C in q = C dT^3, in W/(m^2 K^3)."""
    return Q_CHF / DT_CHF ** 3 * surface


def dt_at_chf(surface=1.0):
    """Wall superheat (K) at which the nucleate branch reaches the CHF."""
    return (Q_CHF / nucleate_coeff(surface)) ** (1.0 / 3.0)


def boiling_flux(dt, surface=1.0):
    """Illustrative boiling curve: heat flux (W/m^2) for wall superheat dt (K). Pure Python floats."""
    c = nucleate_coeff(surface)
    d1 = dt_at_chf(surface)
    if dt <= d1:
        return max(H_NC * dt, c * dt ** 3) if dt > 0 else H_NC * dt
    if dt <= DT_MIN:
        f = (dt - d1) / (DT_MIN - d1)
        return math.exp(math.log(Q_CHF) + f * (math.log(Q_MIN) - math.log(Q_CHF)))
    return Q_MIN * dt / DT_MIN


def regime(dt, surface=1.0):
    d1 = dt_at_chf(surface)
    if dt < math.sqrt(H_NC / nucleate_coeff(surface)):
        return "natural convection"
    if dt <= d1:
        return "nucleate boiling"
    if dt <= DT_MIN:
        return "transition boiling"
    return "film boiling"


# %% [markdown]
# ## Step 2: the lumped plate, stepped forward in time
# Energy balance per square metre of plate: `C_PLATE * d(dT)/dt = q_in(t) - q(dT)`.
# Explicit Euler with a small step `dt_s` (the fastest time constant is about 0.16 s, so
# `dt_s = 0.005 s` is safe). Heat supplied minus heat carried off by boiling is stored.

# %%
def simulate_power(q_in, t_end=120.0, dt_s=0.005, surface=1.0, c_plate=C_PLATE, dt0=0.0,
                   stop_at_limit=True):
    """Power-controlled heating. q_in is a function of time t (s) giving W/m^2.

    Returns a dict with arrays t, dT, q_in, q_out and the burnout time (None if it never happens).
    """
    n = int(round(t_end / dt_s))
    t = np.arange(n + 1) * dt_s
    dT = np.zeros(n + 1)
    qi = np.zeros(n + 1)
    qo = np.zeros(n + 1)
    dT[0] = dt0
    burn = None
    last = n
    for k in range(n + 1):
        qi[k] = q_in(t[k])
        qo[k] = boiling_flux(dT[k], surface)
        if stop_at_limit and burn is None and dT[k] >= DT_LIMIT:
            burn = t[k]
            last = k
            break
        if k < n:
            dT[k + 1] = dT[k] + dt_s * (qi[k] - qo[k]) / c_plate
    return {"t": t[:last + 1], "dT": dT[:last + 1], "q_in": qi[:last + 1], "q_out": qo[:last + 1],
            "burnout_time": burn, "dt_s": dt_s, "c_plate": c_plate, "surface": surface}


def step_power(q_target, ramp=10.0):
    """Heat flux that rises linearly to q_target over `ramp` seconds and then stays."""
    return lambda t: q_target * min(1.0, t / ramp)


def _trapezoid(y, x):
    return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(x)))


def energy_balance(run):
    """Energy in, energy carried off by boiling, energy stored (J/m^2) and the residual.

    Uses the trapezoid rule on the recorded arrays, so it is an independent check of the
    time stepping.
    """
    t = run["t"]
    e_in = _trapezoid(run["q_in"], t)
    e_out = _trapezoid(run["q_out"], t)
    stored = run["c_plate"] * (run["dT"][-1] - run["dT"][0])
    return {"in": e_in, "out": e_out, "stored": stored, "residual": e_in - e_out - stored}


# %% [markdown]
# ## Step 3: check the stepper against an exact solution
# While the plate is in natural convection and the flux is constant, the equation is linear:
# `dT(t) = (q_in / H_NC) * (1 - exp(-H_NC t / C_PLATE))`. A time constant `C_PLATE / H_NC`
# of 17.25 s means the plate reaches 63 percent of its final superheat after 17 s.

# %%
def exact_natural(q_const, t):
    return q_const / H_NC * (1.0 - np.exp(-H_NC * np.asarray(t) / C_PLATE))


# %% [markdown]
# ## Step 4: burnout, safe margin and the hysteresis loop
# `burnout_time(q)` applies a power step and reports when the plate reaches `DT_LIMIT`.
# `hysteresis_loop` raises the heat flux slowly past the CHF, then lowers it again, with
# no limit stop, so you see the path the operating point takes.

# %%
def burnout_time(q_target, surface=1.0, c_plate=C_PLATE, t_end=300.0, ramp=10.0, dt_s=0.005):
    run = simulate_power(step_power(q_target, ramp), t_end=t_end, dt_s=dt_s, surface=surface, c_plate=c_plate)
    return run["burnout_time"]


def steady_superheat(q, surface=1.0):
    """Nucleate-branch superheat (K) at which boiling_flux = q, or None above the CHF."""
    if q > Q_CHF:
        return None
    lo, hi = 0.0, dt_at_chf(surface)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if boiling_flux(mid, surface) < q:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def hysteresis_loop(q_peak=1.15e6, t_up=240.0, t_top=600.0, t_down=8000.0, t_tail=400.0, dt_s=0.05, surface=1.0):
    """Power ramps 0 -> q_peak, holds, then ramps slowly back to 0. No plate limit is applied,
    so the loop shows where the model would go (a real plate has failed long before)."""
    def q_in(t):
        if t < t_up:
            return q_peak * t / t_up
        if t < t_up + t_top:
            return q_peak
        return max(0.0, q_peak * (1.0 - (t - t_up - t_top) / t_down))
    run = simulate_power(q_in, t_end=t_up + t_top + t_down + t_tail, dt_s=dt_s, surface=surface, stop_at_limit=False)
    run["t_peak_end"] = t_up + t_top
    return run


def hysteresis_flux(run, surface=1.0):
    """Heat flux (W/m^2) at which the plate jumped up to film boiling on the way up, and at which it
    fell back to nucleate boiling on the way down."""
    d1 = dt_at_chf(surface)
    up = np.where(run["dT"] > 2.0 * d1)[0][0]
    after = np.where(run["t"] > run["t_peak_end"])[0][0]
    down = after + np.where(run["dT"][after:] < DT_MIN)[0][0]
    return float(run["q_in"][up]), float(run["q_in"][down])


def temperature_controlled(dt_max=200.0, n=401, surface=1.0):
    """Wall temperature imposed: sweep dT up to dt_max and back. Returns dT and q (single valued)."""
    up = np.linspace(0.0, dt_max, n)
    sweep = np.concatenate([up, up[::-1]])
    return sweep, np.array([boiling_flux(d, surface) for d in sweep])


# %% [markdown]
# ## Step 5: bubble growth by diffusion
# A bubble grows because liquid at the wall is superheated: heat conducts into the bubble wall and
# evaporates liquid. In a thin thermal layer, `rho_v h_fg dR/dt = q_interface`. We get
# `q_interface` from a numerical solution of the 1-D heat equation in the liquid after the wall of the
# bubble is held at saturation temperature, then integrate to get R(t). The planar
# (flat-interface) result is `R = 2 Ja sqrt(alpha t / pi)`; the classic spherical Plesset-Zwick
# result `R = 2 sqrt(3/pi) Ja sqrt(alpha t)` is sqrt(3) times larger. Both grow as the
# square root of time, so the exponent of a log-log fit must be 0.5.

# %%
RHO_L, RHO_V, CP_L, K_L, H_FG = 958.4, 0.596, 4216.0, 0.679, 2.257e6   # water at 100 C, approximate
ALPHA = K_L / (RHO_L * CP_L)                                             # m^2/s, about 1.7e-7


def jakob(dt_sup):
    """Jakob number Ja = rho_l cp dT / (rho_v h_fg), dimensionless."""
    return RHO_L * CP_L * dt_sup / (RHO_V * H_FG)


def radius_planar(t, dt_sup):
    return 2.0 * jakob(dt_sup) * np.sqrt(ALPHA * np.asarray(t) / math.pi)


def radius_pz(t, dt_sup):
    """Plesset-Zwick scaling R = 2 sqrt(3/pi) Ja sqrt(alpha t)."""
    return 2.0 * math.sqrt(3.0 / math.pi) * jakob(dt_sup) * np.sqrt(ALPHA * np.asarray(t))


def growth_numeric(dt_sup, t_end=5e-3, n_space=600, n_time=500):
    """Solve the 1-D heat equation in the liquid (interface held at T_sat, far field superheated
    by dt_sup) with backward Euler on a geometric time grid; integrate the interface flux to R(t).

    Returns (t, R) arrays.
    """
    depth = 12.0 * math.sqrt(ALPHA * t_end)
    dx = depth / n_space
    theta = np.ones(n_space + 1) * dt_sup       # superheat above T_sat in the liquid
    theta[0] = 0.0
    times = np.geomspace(1e-7, t_end, n_time)
    t_prev = 0.0
    radius, rr, tt = 0.0, [0.0], [0.0]
    flux_prev = None
    for t_now in times:
        h = t_now - t_prev
        r = ALPHA * h / dx ** 2
        # tridiagonal system (1 + 2r) th_i - r th_{i-1} - r th_{i+1} = th_i_old, ends fixed
        d = theta[1:-1].copy()
        d[-1] += r * dt_sup
        b = np.empty(n_space - 1)
        b[0] = 1.0 + 2.0 * r
        for i in range(1, n_space - 1):          # Thomas algorithm, forward sweep
            b[i] = 1.0 + 2.0 * r - r * r / b[i - 1]
            d[i] += r * d[i - 1] / b[i - 1]
        x = np.zeros(n_space - 1)
        x[-1] = d[-1] / b[-1]
        for i in range(n_space - 3, -1, -1):     # back substitution
            x[i] = (d[i] + r * x[i + 1]) / b[i]
        theta[1:-1] = x
        flux = K_L * (-3.0 * theta[0] + 4.0 * theta[1] - theta[2]) / (2.0 * dx)
        if flux_prev is None:
            flux_prev = flux
        radius += 0.5 * (flux + flux_prev) * h / (RHO_V * H_FG)
        flux_prev = flux
        t_prev = t_now
        tt.append(t_now)
        rr.append(radius)
    return np.array(tt), np.array(rr)


def loglog_slope(t, r, t_min=1e-4):
    """Slope of log R against log t for t >= t_min: the growth exponent."""
    m = (t >= t_min) & (r > 0)
    return float(np.polyfit(np.log(t[m]), np.log(r[m]), 1)[0])


# %% [markdown]
# ## Step 6: choosing a safe power (the mini-project tool)
# A design is accepted when, for every surface condition listed (new = 1.0, fouled = 0.6):
# (a) the heat flux is at most `max_chf_fraction` of the CHF, (b) the steady wall superheat is at
# most `dt_max` kelvin, and (c) a power overshoot of 20 percent does not burn the plate out in
# a transient simulation.

# %%
def design_check(power_w, area_m2, surfaces=(1.0, 0.6), dt_max=25.0, max_chf_fraction=0.6, overshoot=1.2):
    """Returns a dict: ok, flux, worst superheat, and which condition failed (if any)."""
    q = power_w / area_m2
    out = {"flux": q, "ok": True, "failed": []}
    if q > max_chf_fraction * Q_CHF:
        out["ok"] = False
        out["failed"].append("flux above the allowed fraction of the CHF")
    worst = 0.0
    for s in surfaces:
        d = steady_superheat(q, s)
        worst = max(worst, d if d is not None else float("inf"))
        if d is None or d > dt_max:
            out["ok"] = False
            out["failed"].append(f"superheat above {dt_max} K on surface {s}")
        if burnout_time(q * overshoot, s, t_end=60.0, dt_s=0.02) is not None:
            out["ok"] = False
            out["failed"].append(f"burnout after a {overshoot} times overshoot on surface {s}")
    out["worst_superheat"] = worst
    return out


def max_safe_power(area_m2, step_w=1000.0, p_max_w=60000.0, **kw):
    """Largest power on the grid that passes design_check (None if none does)."""
    best = None
    p = step_w
    while p <= p_max_w + 1e-9:
        if design_check(p, area_m2, **kw)["ok"]:
            best = p
        p += step_w
    return best


# %% [markdown]
# ## Step 7: a thick plate, heat flowing through the metal
# The lumped plate gives one temperature to the whole plate. A thick or poorly conducting
# plate cannot: heat entering at the back face must be *conducted* to the boiling face, which
# takes a temperature difference. In steady state that difference is exactly `q L / k`
# (heat flux times thickness over conductivity). The ratio of the temperature drop inside the
# plate to the one across the boiling film is the *Biot number* `Bi = h L / k`, where
# `h = q / dT` is how well the surface hands heat to the water. Lumping is fair for Bi below
# about 0.1.
#
# `simulate_plate` divides the thickness into slices (finite volumes) and steps the heat
# equation `rho cp dT/dt = k d2T/dx2`: heat `q_in(t)` enters at x = 0, the boiling curve takes
# `boiling_flux(T at x = L)` out at the surface. Conduction is treated implicitly, so the step
# is not limited by the slice thickness; the boiling flux is taken at the start of the step,
# so keep `dt_s` small (checked by halving it).

# %%
K_PLATE = 400.0         # W/(m K), copper
RHO_CP = 3.45e6         # J/(m^3 K), copper; C_PLATE is RHO_CP times 5 mm


def biot_chf(thickness, k=K_PLATE, surface=1.0):
    """Biot number h L / k with h = Q_CHF / dT at the critical heat flux (where it matters most)."""
    return Q_CHF / dt_at_chf(surface) * thickness / k


def simulate_plate(q_in, thickness, n=None, t_end=300.0, dt_s=0.002, surface=1.0, k=K_PLATE,
                   rho_cp=RHO_CP, stop_at_limit=True):
    """1-D conduction in a plate of the given thickness (m) heated at x = 0 (flux q_in(t), W/m^2),
    cooled by boiling at x = L, insulated otherwise. Superheats are in K relative to the water.

    Returns dict: t, T_back, T_surface, T_mean, q_in, q_out (arrays), burnout_time (the heated
    face reaches DT_LIMIT, or None), final profile T (nodes from back to surface), x, and the
    stored energy (J/m^2) for the energy balance."""
    if n is None:
        n = max(10, int(round(thickness / 0.5e-3)))
    dx = thickness / n
    c = np.full(n + 1, rho_cp * dx)
    c[0] *= 0.5
    c[-1] *= 0.5
    g = k / dx
    cond = np.zeros((n + 1, n + 1))
    for i in range(n):
        cond[i, i] += g
        cond[i + 1, i + 1] += g
        cond[i, i + 1] -= g
        cond[i + 1, i] -= g
    a_inv = np.linalg.inv(np.diag(c) + dt_s * cond)
    steps = int(round(t_end / dt_s))
    T = np.zeros(n + 1)
    b = np.zeros(n + 1)
    tt, tb, ts, tm, qi_l, qo_l = [], [], [], [], [], []
    burn = None
    w = np.full(n + 1, dx)
    w[0] *= 0.5
    w[-1] *= 0.5
    for s in range(steps + 1):
        t = s * dt_s
        qi, qo = q_in(t), boiling_flux(T[-1], surface)
        tt.append(t); tb.append(T[0]); ts.append(T[-1]); tm.append(float(w @ T) / thickness)
        qi_l.append(qi); qo_l.append(qo)
        if stop_at_limit and T[0] >= DT_LIMIT:
            burn = t
            break
        b[0], b[-1] = qi, -qo
        T = a_inv @ (c * T + dt_s * b)
    return {"t": np.array(tt), "T_back": np.array(tb), "T_surface": np.array(ts), "T_mean": np.array(tm),
            "q_in": np.array(qi_l), "q_out": np.array(qo_l), "burnout_time": burn,
            "x": np.linspace(0.0, thickness, n + 1), "T": T, "thickness": thickness,
            "stored": float(np.sum(c * T)), "rho_cp": rho_cp}


def plate_energy_balance(run):
    """Energy in, carried off by boiling and stored in the plate (J/m^2), and the residual.
    The stored energy is recomputed from the final profile, independently of the time stepping."""
    e_in = _trapezoid(run["q_in"], run["t"])
    e_out = _trapezoid(run["q_out"], run["t"])
    return {"in": e_in, "out": e_out, "stored": run["stored"], "residual": e_in - e_out - run["stored"]}


def plate_burnout_time(q_target, thickness, ramp=10.0, **kw):
    """Burnout time (s) of the 1-D plate for a power step, to compare with `burnout_time` with
    c_plate = RHO_CP * thickness."""
    return simulate_plate(step_power(q_target, ramp), thickness, **kw)["burnout_time"]


# %% [markdown]
# ## Step 6: run it and plot
# Four figures: the boiling curve, the burnout run, the hysteresis loop, and bubble growth.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    dts = np.linspace(0.0, 250.0, 1000)
    q = np.array([boiling_flux(d) for d in dts])
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.semilogy(dts[1:], q[1:] / 1e3)
    for xx, yy, lab in ((2.5, 3, "natural\nconvection"), (14, 80, "nucleate"), (60, 100, "transition"), (190, 9, "film")):
        ax.annotate(lab, (xx, yy), fontsize=8, ha="center")
    ax.plot([DT_CHF], [Q_CHF / 1e3], "ro")
    ax.annotate("CHF 1100 kW/m2", (DT_CHF, Q_CHF / 1e3), (42, 1300), fontsize=8, color="r")
    ax.plot([DT_MIN], [Q_MIN / 1e3], "ks")
    ax.annotate("minimum film flux", (DT_MIN, Q_MIN / 1e3), (100, 8), fontsize=8)
    ax.set_xlabel("wall superheat T_wall - T_sat (K)")
    ax.set_ylabel("heat flux q (kW/m2, log scale)")
    ax.set_title("Illustrative boiling curve (not a fitted correlation)")
    ax.set_ylim(1, 3000)
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "boiling_curve.png", dpi=120)

    fig2, axs = plt.subplots(1, 2, figsize=(9, 3.8))
    for qt, col in ((900e3, "tab:green"), (1050e3, "tab:blue"), (1150e3, "tab:red")):
        run = simulate_power(step_power(qt), t_end=60.0)
        axs[0].plot(run["t"], T_SAT + run["dT"], color=col, label=f"{qt / 1e3:.0f} kW/m2")
        steady = steady_superheat(qt)
        print(f"q_in {qt / 1e3:6.0f} kW/m2: steady superheat {steady}, burnout time {run['burnout_time']}")
    axs[0].axhline(T_SAT + DT_LIMIT, color="k", ls="--", lw=1)
    axs[0].annotate("plate limit", (1, T_SAT + DT_LIMIT + 8), fontsize=8)
    axs[0].set_xlabel("time (s)")
    axs[0].set_ylabel("plate temperature (degrees C)")
    axs[0].set_title("Power-controlled: below and above the CHF")
    axs[0].legend(title="heat flux in")
    axs[0].grid(alpha=0.3)
    h = hysteresis_loop()
    dl = np.logspace(0, 3.9, 800)
    axs[1].loglog(dl, [boiling_flux(d) / 1e3 for d in dl], color="0.6", lw=3, alpha=0.6, label="boiling curve")
    kk = np.arange(int(30.0 / h["dt_s"]), len(h["t"]), 20)
    pk = int(np.searchsorted(h["t"], h["t_peak_end"]))
    axs[1].loglog(np.maximum(h["dT"][kk[kk < pk]], 1e-1), np.maximum(h["q_in"][kk[kk < pk]], 1.0) / 1e3, "r-", lw=1.2, label="power raised")
    ok = kk[(kk >= pk) & (h["dT"][kk] > 3.0)]
    axs[1].loglog(h["dT"][ok], h["q_in"][ok] / 1e3, "b-", lw=1.2, label="power lowered")
    sw, qq = temperature_controlled()
    axs[1].loglog(sw[1:], qq[1:] / 1e3, "g--", lw=1.2, label="temperature controlled")
    axs[1].set_xlim(1, 8000)
    axs[1].set_ylim(1, 3000)
    axs[1].set_xlabel("wall superheat (K, log scale)")
    axs[1].set_ylabel("heat flux (kW/m2, log scale)")
    axs[1].set_title("Hysteresis of a power-controlled plate")
    axs[1].legend(fontsize=7)
    axs[1].grid(alpha=0.3, which="both")
    fig2.tight_layout()
    fig2.savefig(OUT / "burnout_and_hysteresis.png", dpi=120)

    print("hysteresis: jump up at / fall back at (kW/m2):", [round(v / 1e3, 1) for v in hysteresis_flux(h)])
    t, r = growth_numeric(5.0)
    print("growth exponent (numeric, 5 K):", round(loglog_slope(t, r), 3))
    print("numeric R at 5 ms / planar analytic:", round(float(r[-1] / radius_planar(t[-1], 5.0)), 3))
    fig3, ax3 = plt.subplots(figsize=(5.6, 4))
    ax3.loglog(t[1:], r[1:] * 1e3, label="numerical diffusion solver")
    ax3.loglog(t[1:], radius_planar(t[1:], 5.0) * 1e3, "--", label="planar: 2 Ja sqrt(alpha t / pi)")
    ax3.loglog(t[1:], radius_pz(t[1:], 5.0) * 1e3, ":", label="Plesset-Zwick (spherical)")
    ax3.set_xlabel("time (s)")
    ax3.set_ylabel("bubble radius (mm)")
    ax3.set_title("Bubble growth, 5 K superheat: slope 1/2 on log-log")
    ax3.legend(fontsize=7)
    ax3.grid(alpha=0.3, which="both")
    fig3.tight_layout()
    fig3.savefig(OUT / "bubble_growth.png", dpi=120)
    print("burnout times (s) after a step to q:")
    for qt in (1.1e6, 1.15e6, 1.3e6, 1.5e6):
        print(f"  {qt / 1e3:6.0f} kW/m2 -> {burnout_time(qt)}")
    print("mini-project: max safe power for 0.04 m2 (W):", max_safe_power(0.04))

    # figure 4: thick plate, temperature profile and burnout time against thickness
    fig4, ax4 = plt.subplots(1, 2, figsize=(10.5, 4.2))
    q_ss = 5e5
    for th, col in ((0.005, "#003f7f"), (0.02, "#c86a00"), (0.05, "#d81b60")):
        rr = simulate_plate(lambda t: q_ss, th, t_end=150.0, stop_at_limit=False)
        ax4[0].plot(1e3 * rr["x"], rr["T"], color=col, lw=2,
                    label=f"{1e3 * th:g} mm: drop {rr['T'][0] - rr['T'][-1]:.2f} K = q L / k")
    ax4[0].set_xlabel("depth x from the heated back face (mm)")
    ax4[0].set_ylabel("temperature above the water (K)")
    ax4[0].set_title(f"Steady profiles at q = {q_ss / 1e3:.0f} kW/m2", fontsize=10)
    ax4[0].grid(alpha=0.3)
    ax4[0].legend(fontsize=8)
    ths = np.array([1, 2, 5, 10, 20, 50]) * 1e-3
    lum = [burnout_time(1.3e6, c_plate=RHO_CP * th, t_end=400.0) for th in ths]
    one = [plate_burnout_time(1.3e6, th, t_end=400.0) for th in ths]
    ax4[1].plot(1e3 * ths, lum, "o--", color="#c86a00", label="lumped plate")
    ax4[1].plot(1e3 * ths, one, "s-", color="#003f7f", label="1-D conduction (heated face)")
    ax4[1].set_xscale("log")
    ax4[1].set_xlabel("plate thickness (mm)")
    ax4[1].set_ylabel("burnout time after a step to 1.3 MW/m2 (s)")
    ax4[1].set_title("Lumped burnout time is a few percent late", fontsize=10)
    ax4[1].grid(alpha=0.3, which="both")
    ax4[1].legend(fontsize=8)
    fig4.tight_layout()
    fig4.savefig(OUT / "thick_plate.png", dpi=120)
    print("thickness mm, Bi at CHF, lumped burnout, 1-D burnout, difference %:")
    for th, a, b_ in zip(ths, lum, one):
        print(f"  {1e3 * th:4.0f}  Bi {biot_chf(th):.3f}  {a:7.2f}  {b_:7.2f}  {100 * (a - b_) / a:5.1f}")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
