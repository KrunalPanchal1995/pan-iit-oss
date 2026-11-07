"""Session 3 (Level 3): step the energy balance forward in time and validate it.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a warming planet, one year at a time
# **A. Real-world problem.** Session 2 says that more infrared-absorbing gas means a warmer
# surface in equilibrium. But the ocean holds a huge amount of heat, so the Earth cannot jump
# to its new temperature at once. If CO2 rises, how fast does the surface warm, how much
# warming is still "in the pipeline", and what CO2 level keeps the long-term warming below
# 2 K? We step the energy balance forward in time and check the simulation against exact
# results before we trust it.
#
# **Plan.** (1) the time-dependent one-layer model with an ocean heat capacity,
# (2) validation: equilibrium, relaxation time and energy conservation, (3) CO2 forcing and the
# feedback parameter, (4) a step change and a 1 percent per year rise, (5) the mini-project:
# a CO2 ceiling for a 2 K limit.
#
# **Model.** Global and annual averages per square metre; time in years; heat capacity in
# W yr/(m2 K) so that C dT/dt is in W/m2. A simplified teaching model, not a climate projection.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
SIGMA = 5.670374419e-8                  # W/(m2 K4)
S_EARTH, ALBEDO_EARTH = 1361.0, 0.30
SECONDS_PER_YEAR = 3.156e7
RHO_W, CP_W = 1025.0, 3990.0            # sea water: kg/m3, J/(kg K)
CO2_PRE = 280.0                         # pre-industrial CO2, ppm
F2X = 5.35 * np.log(2.0)                # forcing for doubled CO2, about 3.71 W/m2


def heat_capacity(depth_m=70.0):
    """Heat capacity of a well-mixed ocean layer of this depth, in W yr/(m2 K)."""
    if depth_m <= 0:
        raise ValueError("depth must be positive")
    return RHO_W * CP_W * depth_m / SECONDS_PER_YEAR


# %% [markdown]
# ## Step 1: the one-layer model, now with time
# The surface layer of the ocean (a "slab" about 70 m deep) stores heat. Any imbalance
# between sunlight absorbed and infrared escaping warms or cools it:
#
#     C dTs/dt = S (1 - alpha) / 4  -  (1 - eps / 2) sigma Ts^4
#
# The second term is Session 2's outgoing infrared (OLR). We step it forward with the
# simplest method, **forward Euler**: T_new = T + dt (in - out) / C.

# %%
def olr(ts, eps):
    """Outgoing longwave radiation of the one-layer model (W/m2)."""
    return (1.0 - eps / 2.0) * SIGMA * np.asarray(ts, float) ** 4


def equilibrium_ts(eps, s=S_EARTH, albedo=ALBEDO_EARTH):
    """Session 2 result: Ts where OLR equals absorbed sunlight (K)."""
    return (s * (1.0 - albedo) / 4.0 / ((1.0 - eps / 2.0) * SIGMA)) ** 0.25


def run_layer_model(t0, eps, years, dt=0.05, depth_m=70.0, s=S_EARTH, albedo=ALBEDO_EARTH):
    """Step the nonlinear one-layer model. Returns arrays (time in yr, Ts in K)."""
    if dt <= 0 or years <= 0:
        raise ValueError("need dt > 0 and years > 0")
    c = heat_capacity(depth_m)
    asr = s * (1.0 - albedo) / 4.0
    n = int(round(years / dt))
    t = np.arange(n + 1) * dt
    ts = np.empty(n + 1)
    ts[0] = t0
    for i in range(n):
        ts[i + 1] = ts[i] + dt * (asr - olr(ts[i], eps)) / c
    return t, ts


def planck_lambda(eps, s=S_EARTH, albedo=ALBEDO_EARTH):
    """d(OLR)/dTs at equilibrium: 4 OLR / Ts (W/(m2 K)). How strongly a warmer planet sheds heat."""
    ts = equilibrium_ts(eps, s, albedo)
    return 4.0 * float(olr(ts, eps)) / ts


# %% [markdown]
# ## Step 2: forcing and feedback
# Near equilibrium we can straighten the curve: write T for the warming above the starting
# state. Extra CO2 creates a **radiative forcing** F (W/m2); a warmer planet sheds lambda T
# more. The **feedback parameter** lambda includes the Planck response from Step 1 (about
# 3.3 W/(m2 K)) minus the extra warming from water vapour, melting ice and clouds:
#
#     C dT/dt = F(t) - lambda T          F = 5.35 ln(CO2 / 280)   (Myhre et al. 1998)
#
# In equilibrium T = F / lambda; for doubled CO2 this is the **equilibrium climate
# sensitivity** ECS = F2x / lambda. For a step forcing the exact solution is
# T = (F / lambda)(1 - exp(-t / tau)) with **time constant** tau = C / lambda.

# %%
def co2_forcing(co2_ppm, co2_ref=CO2_PRE):
    """Radiative forcing of CO2 relative to co2_ref (W/m2)."""
    co2_ppm = np.asarray(co2_ppm, float)
    if np.any(co2_ppm <= 0) or co2_ref <= 0:
        raise ValueError("CO2 must be positive")
    return 5.35 * np.log(co2_ppm / co2_ref)


def lambda_for_ecs(ecs):
    """Feedback parameter (W/(m2 K)) that gives this equilibrium climate sensitivity (K)."""
    if ecs <= 0:
        raise ValueError("ECS must be positive")
    return F2X / ecs


def step_response(forcing, lam, t, depth_m=70.0):
    """Exact warming (K) after a sudden constant forcing, at times t (yr)."""
    tau = heat_capacity(depth_m) / lam
    return forcing / lam * (1.0 - np.exp(-np.asarray(t, float) / tau))


def run_linear_model(forcing_fn, lam, years, dt=0.1, depth_m=70.0):
    """Forward-Euler run of C dT/dt = F(t) - lam T from T = 0.

    Returns a dict with time, warming T, forcing F, imbalance N = F - lam T (W/m2) and the
    heat stored C T (W yr/m2) next to the time-integral of N (they must agree)."""
    if lam <= 0 or dt <= 0 or years <= 0:
        raise ValueError("need lam > 0, dt > 0 and years > 0")
    c = heat_capacity(depth_m)
    n = int(round(years / dt))
    t = np.arange(n + 1) * dt
    f = np.array([forcing_fn(x) for x in t], float)
    temp = np.zeros(n + 1)
    for i in range(n):
        temp[i + 1] = temp[i] + dt * (f[i] - lam * temp[i]) / c
    imbalance = f - lam * temp
    absorbed = float(np.sum(imbalance[:-1]) * dt)      # the same sum Euler used
    return {"t": t, "T": temp, "F": f, "N": imbalance, "stored": c * temp[-1], "absorbed": absorbed}


# %% [markdown]
# ## Step 3: scenarios
# * **Step:** CO2 doubled overnight, then held (F = F2x).
# * **Ramp:** CO2 grows 1 percent per year (a standard test case) up to a ceiling, then held.
#   It doubles after ln 2 / ln 1.01 = 69.7 years.

# %%
def co2_path(rate_pct, ceiling_ppm, start_ppm=CO2_PRE):
    """CO2 (ppm) as a function of time (yr): rate_pct per year growth up to ceiling_ppm."""
    def co2(t):
        return min(start_ppm * (1.0 + rate_pct / 100.0) ** t, ceiling_ppm)
    return co2


def max_co2_for_limit(t_limit, lam, co2_ref=CO2_PRE):
    """Highest CO2 (ppm) whose equilibrium warming F / lam stays at or below t_limit (K)."""
    if t_limit <= 0 or lam <= 0:
        raise ValueError("need a positive limit and lambda")
    return co2_ref * np.exp(t_limit * lam / 5.35)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    c = heat_capacity()
    eps0 = 2.0 * (1.0 - (S_EARTH * 0.7 / 4 / SIGMA) / 288.0 ** 4)      # Session 2: eps for 288 K
    lam_p = planck_lambda(eps0)
    print(f"heat capacity of a 70 m ocean layer: {c:.2f} W yr/(m2 K); eps today {eps0:.3f}; Planck lambda {lam_p:.2f} W/(m2 K)")

    # validation 1: the nonlinear model relaxes to the Session 2 equilibrium with tau = C / lambda
    t, ts = run_layer_model(270.0, eps0, 40.0)
    print(f"start 270 K -> {ts[-1]:.3f} K after 40 yr (analytic equilibrium {equilibrium_ts(eps0):.3f} K)")
    print(f"predicted relaxation time C / lambda = {c / lam_p:.2f} yr")

    # validation 2: step forcing, Euler against the exact solution
    lam = lambda_for_ecs(3.0)
    run = run_linear_model(lambda _: F2X, lam, 50.0)
    exact = step_response(F2X, lam, run["t"])
    print(f"F2x = {F2X:.3f} W/m2, lambda = {lam:.3f}, tau = {c / lam:.2f} yr")
    print(f"T after 10 yr: Euler {np.interp(10, run['t'], run['T']):.3f} K, exact {step_response(F2X, lam, 10.0):.3f} K; max error {np.max(np.abs(run['T'] - exact)):.4f} K")
    print(f"energy check: heat stored {run['stored']:.3f}, imbalance integrated {run['absorbed']:.3f} W yr/m2")

    # Figure 1: validation
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.2))
    for t0 in (240.0, 270.0, 300.0, 320.0):
        tt, tsx = run_layer_model(t0, eps0, 40.0)
        a1.plot(tt, tsx, lw=2, label=f"start {t0:.0f} K")
    a1.axhline(equilibrium_ts(eps0), color="k", ls="--", lw=1)
    a1.text(39, equilibrium_ts(eps0) + 1.5, f"Session 2 answer {equilibrium_ts(eps0):.0f} K", ha="right", fontsize=8)
    a1.set_xlabel("time (years)")
    a1.set_ylabel("surface temperature Ts (K)")
    a1.set_title("Every start settles at the same temperature")
    a1.legend(fontsize=8)
    a1.grid(alpha=0.3)
    a2.plot(run["t"], exact, color="k", lw=4, alpha=0.25, label="exact (F / lambda)(1 - exp(-t / tau))")
    a2.plot(run["t"], run["T"], color="#d9534f", lw=1.6, label="forward Euler, dt = 0.1 yr")
    a2.axhline(F2X / lam, color="#264653", ls="--", lw=1)
    a2.axvline(c / lam, color="#999999", ls=":", lw=1)
    a2.text(c / lam + 0.7, 0.3, f"tau = {c / lam:.1f} yr", fontsize=8)
    a2.text(49, F2X / lam - 0.22, "ECS = 3.0 K", ha="right", fontsize=8)
    a2.set_xlabel("time after CO2 doubles (years)")
    a2.set_ylabel("warming T (K)")
    a2.set_title("Step forcing: simulation matches the exact curve")
    a2.legend(fontsize=8, loc="lower right")
    a2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "validation.png", dpi=120)

    # Figure 2: 1 percent per year to doubling, then held; three feedback strengths
    path = co2_path(1.0, 2 * CO2_PRE)
    cases = [("Planck only", lam_p, "#2a9d8f"), ("ECS 3 K", lambda_for_ecs(3.0), "#e9a23b"), ("ECS 4.5 K", lambda_for_ecs(4.5), "#d9534f")]
    fig2, (b1, b2) = plt.subplots(1, 2, figsize=(10, 4.2))
    t_double = np.log(2.0) / np.log(1.01)
    for name, lm, colour in cases:
        r = run_linear_model(lambda x: float(co2_forcing(path(x))), lm, 200.0)
        at_double = np.interp(t_double, r["t"], r["T"])
        print(f"{name:12s} lambda {lm:.2f}: warming at doubling (year {t_double:.0f}) {at_double:.2f} K, year 200 {r['T'][-1]:.2f} K, equilibrium {F2X / lm:.2f} K")
        b1.plot(r["t"], r["T"], color=colour, lw=2.2, label=f"{name} (lambda {lm:.2f})")
        b1.axhline(F2X / lm, color=colour, ls="--", lw=1)
        b2.plot(r["t"], r["N"], color=colour, lw=2.0)
    b1.axvline(t_double, color="#999999", ls=":", lw=1)
    b1.text(t_double + 2, 0.2, "CO2 doubled", fontsize=8)
    b1.set_xlabel("time (years)")
    b1.set_ylabel("warming T (K)")
    b1.set_title("CO2 +1 %/yr to 560 ppm, then held")
    b1.legend(fontsize=8, loc="lower right")
    b1.grid(alpha=0.3)
    b2.plot(r["t"], r["F"], color="k", lw=1.2, ls="--", label="forcing F")
    b2.set_xlabel("time (years)")
    b2.set_ylabel("energy imbalance N = F - lambda T (W/m2)")
    b2.set_title("The imbalance is heat still flowing into the ocean")
    b2.legend(fontsize=8)
    b2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "scenarios.png", dpi=120)

    # Figure 3: mini-project, the CO2 ceiling for a 2 K equilibrium limit
    ecs = np.linspace(1.5, 4.5, 61)
    ceiling = [max_co2_for_limit(2.0, lambda_for_ecs(e)) for e in ecs]
    fig3, ax3 = plt.subplots(figsize=(6.4, 4.2))
    ax3.plot(ecs, ceiling, color="#264653", lw=2.2, label="CO2 ceiling for 2 K (CO2 only)")
    ax3.axhline(420.0, color="#d9534f", ls="--", lw=1.2, label="about 420 ppm (mid-2020s)")
    for e in (2.5, 3.0, 4.0):
        cm = max_co2_for_limit(2.0, lambda_for_ecs(e))
        ax3.plot([e], [cm], "o", color="#264653")
        ax3.annotate(f"{cm:.0f} ppm", (e, cm), textcoords="offset points", xytext=(6, 6), fontsize=8)
        print(f"ECS {e} K: CO2 ceiling for 2 K = {cm:.0f} ppm")
    ax3.set_xlabel("equilibrium climate sensitivity ECS (K)")
    ax3.set_ylabel("highest CO2 for 2 K in equilibrium (ppm)")
    ax3.set_title("The more sensitive the climate, the lower the ceiling")
    ax3.legend(fontsize=8)
    ax3.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "co2_ceiling.png", dpi=120)

    # sensitivity
    print("time step convergence (T at 10 yr, step forcing):",
          [round(float(np.interp(10, *(lambda r: (r["t"], r["T"]))(run_linear_model(lambda _: F2X, lam, 12.0, dt=d)))), 4) for d in (1.0, 0.5, 0.1, 0.01)],
          "exact", round(float(step_response(F2X, lam, 10.0)), 4))
    print("tau against ocean depth (ECS 3 K):", [round(float(heat_capacity(h) / lam), 1) for h in (25, 50, 70, 100, 200)], "yr")

# %% [markdown]
# ## Where this stops
# One ocean slab warms up in a few years, but the real deep ocean keeps absorbing heat for
# centuries, so the real transient warming is lower than this model gives. Water vapour,
# ice and clouds are lumped into one number lambda. A two-layer ocean, separate feedbacks
# and the historical forcing record are the road to the Target: see `promo/roadmap.md`.
