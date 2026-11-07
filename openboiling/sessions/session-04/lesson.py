"""Session 4 (Level 3): a boiling curve built from fluid properties, at any pressure.

Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: the boiling curve from correlations, and what pressure does to it
# **A. Real-world problem.** Sessions 2 and 3 used a boiling curve with hand-picked numbers: a
# critical heat flux (CHF) of 1.1 MW per square metre, at any pressure. But a pressure cooker boils
# water at 120 C, a boiler at 180 C, and a power-station tube at 300 C, and engineers know that
# the CHF changes with pressure. How much does it change, and why? This session builds the boiling
# curve from water properties instead: Rohsenow for nucleate boiling, Zuber for the CHF, Berenson
# for the minimum film flux and for film boiling, and it asks what happens when the pressure goes
# from 0.5 to 20 bar.
#
# **Plan.** (1) water properties along the saturation line, (2) nucleate boiling, (3) the CHF,
# (4) the minimum flux and film boiling, (5) the whole curve at any pressure, (6) what the
# heater designer gets from it: allowed flux and a burnout test at several pressures.
#
# **Safety and scope.** Simplified teaching model of pool boiling of saturated water on a large
# flat horizontal surface. The correlations carry large uncertainties (the nucleate flux can be
# off by a factor of two, the CHF by 20 to 30 percent, and both depend on the surface). The
# transition and film-boiling parts were developed mostly from data near atmospheric pressure, so
# treat them as a shape, especially at high pressure. Radiation, subcooling, flow and a real
# surface are left out. Never design or test real heating or boiler equipment from this model.
#
# **Assumptions.** Saturated water; properties along the saturation line interpolated from a
# steam table (IAPWS-IF97, 0.5 to 20 bar absolute); vapour properties in the film are taken at
# saturation; one uniform plate temperature in the burnout test (lumped, as in Session 3).

# %%
import functools
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G = 9.81               # m/s^2
ATM = 1.01325          # bar, standard atmosphere
P_MIN, P_MAX = 0.5, 20.0   # bar absolute: the range of the steam table below
CSF = 0.013            # Rohsenow surface-fluid constant, clean water on metal (varies with the surface)
H_NC = 1000.0          # W/(m^2 K), natural convection before bubbles start (as in Session 3)
Q_CHF_SHIPPED = 1.1e6  # W/m^2, the critical heat flux that Session 3's hand-picked curve uses at any pressure
C_PLATE = 17250.0      # J/(m^2 K): the 5 mm copper plate of Session 3
DT_LIMIT = 600.0       # K, superheat at which the plate counts as destroyed (as in Session 3)


# %% [markdown]
# ## Step 1: water along the saturation line
# Everything below needs the properties of saturated liquid and vapour at the pressure we choose:
# saturation temperature, densities, latent heat, surface tension, viscosities, specific heats,
# Prandtl number and vapour conductivity. The table is from the IAPWS-IF97 steam-table formulation
# (computed with the Python package `iapws` and rounded to 5 figures), at 12 pressures from 0.5
# to 20 bar absolute. Between rows we interpolate the logarithm of each property against the
# logarithm of the pressure (the saturation temperature linearly against ln p). Outside the table
# we refuse to answer instead of extrapolating.

# %%
_COLS = ("P", "T", "rho_l", "rho_v", "h_fg", "sigma", "mu_l", "cp_l", "Pr_l", "mu_v", "k_v", "cp_v")
STEAM_TABLE = (
    # P bar, T_sat C, rho_l, rho_v kg/m3, h_fg J/kg, sigma N/m, mu_l Pa s, cp_l J/kg/K, Pr_l, mu_v Pa s, k_v W/m/K, cp_v J/kg/K
    (0.5, 81.317, 970.95, 0.30863, 2304700.0, 0.062431, 0.0003483, 4196.8, 2.1888, 1.1584e-05, 0.022833, 2015.5),
    (0.75, 91.758, 964.12, 0.45104, 2278000.0, 0.060485, 0.00030797, 4207.0, 1.9233, 1.1946e-05, 0.023782, 2047.4),
    (1.01325, 99.974, 958.37, 0.59762, 2256500.0, 0.058917, 0.00028166, 4216.6, 1.7538, 1.2231e-05, 0.024568, 2077.4),
    (1.5, 111.35, 949.92, 0.86255, 2226000.0, 0.056695, 0.00025133, 4232.4, 1.5628, 1.2626e-05, 0.02572, 2127.8),
    (2.0, 120.21, 942.94, 1.129, 2201600.0, 0.054926, 0.0002316, 4246.7, 1.4416, 1.2934e-05, 0.026675, 2175.2),
    (3.0, 133.53, 931.81, 1.6507, 2163400.0, 0.052205, 0.00020691, 4272.0, 1.2943, 1.3394e-05, 0.028216, 2261.8),
    (4.0, 143.61, 922.88, 2.1627, 2133300.0, 0.050096, 0.00019134, 4294.4, 1.2046, 1.3742e-05, 0.029477, 2340.3),
    (5.0, 151.84, 915.28, 2.6681, 2107900.0, 0.048349, 0.00018025, 4315.1, 1.1427, 1.4024e-05, 0.030571, 2412.7),
    (7.0, 164.95, 902.56, 3.6662, 2065600.0, 0.045513, 0.00016498, 4353.0, 1.0604, 1.4473e-05, 0.03245, 2543.3),
    (10.0, 179.89, 887.13, 5.1454, 2014400.0, 0.042216, 0.00015048, 4405.1, 0.98744, 1.4981e-05, 0.034812, 2715.0),
    (15.0, 198.3, 866.65, 7.5929, 1946300.0, 0.038063, 0.0001358, 4485.5, 0.92137, 1.5608e-05, 0.038098, 2964.5),
    (20.0, 212.38, 849.8, 10.042, 1889800.0, 0.03483, 0.00012636, 4562.3, 0.88517, 1.6091e-05, 0.040936, 3190.4),
)
_LNP = np.log([row[0] for row in STEAM_TABLE])


def props(p_bar):
    """Saturated water properties at pressure p_bar (bar absolute, 0.5 to 20) as a dict."""
    if not (P_MIN <= p_bar <= P_MAX):
        raise ValueError(f"pressure {p_bar} bar is outside the table ({P_MIN} to {P_MAX} bar absolute)")
    out = {"P": float(p_bar)}
    x = math.log(p_bar)
    for j, name in enumerate(_COLS):
        if name == "P":
            continue
        y = np.array([row[j] for row in STEAM_TABLE])
        out[name] = float(np.interp(x, _LNP, y)) if name == "T" else float(np.exp(np.interp(x, _LNP, np.log(y))))
    return out


# %% [markdown]
# ## Step 2: nucleate boiling (Rohsenow)
# Rohsenow's correlation for nucleate pool boiling:
# `q = mu_l h_fg sqrt(g (rho_l - rho_v) / sigma) * (cp_l dT / (Csf h_fg Pr_l))^3`, with the
# wall superheat `dT = T_wall - T_sat`. It scales with `dT^3`, as in Session 2, but now the
# coefficient comes from the fluid properties, so it changes with pressure. `Csf` stands for the
# surface and liquid together (0.013 is a typical value for clean water on a metal); the flux goes
# as `1 / Csf^3`, so a 50 percent change in `Csf` changes the flux by a factor of eight. It can be
# inverted: the superheat needed to carry a flux is `dT = (q / coefficient)^(1/3)`.

# %%
@functools.lru_cache(maxsize=None)
def rohsenow_coeff(p_bar, csf=CSF):
    """C in q = C dT^3, in W/(m^2 K^3), for water at pressure p_bar."""
    p = props(p_bar)
    lead = p["mu_l"] * p["h_fg"] * math.sqrt(G * (p["rho_l"] - p["rho_v"]) / p["sigma"])
    return lead * (p["cp_l"] / (csf * p["h_fg"] * p["Pr_l"])) ** 3


def rohsenow_flux(dt, p_bar, csf=CSF):
    return rohsenow_coeff(p_bar, csf) * dt ** 3


def rohsenow_superheat(q, p_bar, csf=CSF):
    """Wall superheat (K) that carries the flux q (W/m^2) in nucleate boiling."""
    return (q / rohsenow_coeff(p_bar, csf)) ** (1.0 / 3.0)


# %% [markdown]
# ## Step 3: the critical heat flux (Zuber)
# Zuber's hydrodynamic estimate, with the usual constant 0.131 for a large flat plate:
# `q_chf = 0.131 h_fg sqrt(rho_v) (sigma g (rho_l - rho_v))^(1/4)`. The vapour leaves in columns
# and jets, and the CHF is where the escaping vapour starts to choke the liquid coming back. Three
# properties change with pressure, and they pull in different directions: the vapour gets much
# denser (`sqrt(rho_v)` rises a lot), while the latent heat and the surface tension fall a little.
# The CHF is independent of the surface constant `Csf`: it depends on the fluid, not on the plate.

# %%
@functools.lru_cache(maxsize=None)
def chf_zuber(p_bar):
    p = props(p_bar)
    return 0.131 * p["h_fg"] * math.sqrt(p["rho_v"]) * (p["sigma"] * G * (p["rho_l"] - p["rho_v"])) ** 0.25


def chf_factors(p_bar, p_ref=ATM):
    """How each factor of Zuber's formula at p_bar compares with p_ref, and their product (the CHF ratio)."""
    a, b = props(p_bar), props(p_ref)
    f_rho = math.sqrt(a["rho_v"] / b["rho_v"])
    f_hfg = a["h_fg"] / b["h_fg"]
    f_cap = ((a["sigma"] * (a["rho_l"] - a["rho_v"])) / (b["sigma"] * (b["rho_l"] - b["rho_v"]))) ** 0.25
    return {"sqrt_rho_v": f_rho, "h_fg": f_hfg, "capillary": f_cap, "ratio": f_rho * f_hfg * f_cap}


# %% [markdown]
# ## Step 4: the minimum flux and film boiling (Berenson)
# Beyond the CHF the surface is partly blanketed by vapour (transition boiling) and then fully
# blanketed (film boiling). Two Berenson-type results fix the other end of the transition:
# * the minimum heat flux (the Leidenfrost point), in Zuber's form with Berenson's constant 0.09:
#   `q_min = 0.09 rho_v h_fg (g sigma (rho_l - rho_v) / (rho_l + rho_v)^2)^(1/4)`;
# * film boiling on a horizontal plate, from a vapour film that is unstable at the Taylor
#   wavelength `lambda = 2 pi sqrt(3 sigma / (g (rho_l - rho_v)))`:
#   `h = 0.425 (k_v^3 rho_v (rho_l - rho_v) g h'_fg / (mu_v dT lambda))^(1/4)`,
#   with `h'_fg = h_fg + 0.4 cp_v dT` (the vapour must also be heated), and `q = h dT`.
#
# These are independent correlations and they do not meet exactly. We define the superheat at the
# minimum, `dt_min`, as the point where the film-boiling flux falls to `q_min`, which makes the
# curve continuous. No radiation is included.

# %%
@functools.lru_cache(maxsize=None)
def q_min(p_bar):
    p = props(p_bar)
    return 0.09 * p["rho_v"] * p["h_fg"] * (G * p["sigma"] * (p["rho_l"] - p["rho_v"]) / (p["rho_l"] + p["rho_v"]) ** 2) ** 0.25


def film_flux(dt, p_bar):
    """Film-boiling flux (W/m^2) at superheat dt (K), vapour properties at saturation."""
    p = props(p_bar)
    drho = p["rho_l"] - p["rho_v"]
    lam = 2.0 * math.pi * math.sqrt(3.0 * p["sigma"] / (G * drho))
    hfg_eff = p["h_fg"] + 0.4 * p["cp_v"] * dt
    h = 0.425 * (p["k_v"] ** 3 * p["rho_v"] * drho * G * hfg_eff / (p["mu_v"] * dt * lam)) ** 0.25
    return h * dt


@functools.lru_cache(maxsize=None)
def dt_min(p_bar):
    """Superheat (K) at which the film-boiling flux equals q_min (bisection)."""
    target = q_min(p_bar)
    lo, hi = 1.0, 3000.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if film_flux(mid, p_bar) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# %% [markdown]
# ## Step 5: the whole curve at any pressure
# Four pieces, as in Session 3, but every number now comes from the properties:
# * natural convection `q = H_NC dT` until bubbles start,
# * nucleate boiling, Rohsenow, up to the superheat where it reaches the Zuber CHF,
# * transition boiling: the flux falls from the CHF to `q_min`, straight on a log scale,
# * film boiling, Berenson, from `dt_min` upwards.

# %%
def dt_chf(p_bar, csf=CSF):
    """Superheat (K) at which nucleate boiling reaches the CHF."""
    return rohsenow_superheat(chf_zuber(p_bar), p_bar, csf)


def boiling_flux(dt, p_bar, csf=CSF):
    """Heat flux (W/m^2) for wall superheat dt (K) at pressure p_bar. Pure Python floats."""
    if dt <= 0:
        return H_NC * dt
    d1, d2 = dt_chf(p_bar, csf), dt_min(p_bar)
    if dt <= d1:
        return max(H_NC * dt, rohsenow_flux(dt, p_bar, csf))
    if dt <= d2:
        f = (dt - d1) / (d2 - d1)
        return math.exp(math.log(chf_zuber(p_bar)) + f * (math.log(q_min(p_bar)) - math.log(chf_zuber(p_bar))))
    return film_flux(dt, p_bar)


def regime(dt, p_bar, csf=CSF):
    if dt < math.sqrt(H_NC / rohsenow_coeff(p_bar, csf)):
        return "natural convection"
    if dt <= dt_chf(p_bar, csf):
        return "nucleate boiling"
    if dt <= dt_min(p_bar):
        return "transition boiling"
    return "film boiling"


def steady_superheat(q, p_bar, csf=CSF):
    """Wall superheat (K) in steady nucleate boiling at flux q, or None if q is above the CHF."""
    if q > chf_zuber(p_bar):
        return None
    return rohsenow_superheat(q, p_bar, csf)


def pressure_row(p_bar, csf=CSF):
    """One row of the pressure study: saturation temperature and the key points of the curve."""
    p = props(p_bar)
    c = chf_zuber(p_bar)
    return {"p_bar": p_bar, "t_sat": p["T"], "chf": c, "chf_ratio": c / chf_zuber(ATM), "dt_chf": dt_chf(p_bar, csf),
            "q_min": q_min(p_bar), "dt_min": dt_min(p_bar), "q_10K": rohsenow_flux(10.0, p_bar, csf)}


# %% [markdown]
# ## Step 6: what the designer gets
# A heater is kept at a fraction of the CHF (the safety margin of Session 3 was 60 percent). So the
# CHF at the working pressure sets the allowed flux and, through Rohsenow, the wall temperature.
# The burnout test is Session 3's: a lumped 5 mm copper plate, power raised over 10 s, explicit
# Euler steps; the plate counts as burnt out when its superheat reaches `DT_LIMIT`. The same heater
# at the same power can burn out at one atmosphere and be safe at a few bar.

# %%
def design_flux(p_bar, fraction=0.6):
    """Allowed heat flux (W/m^2): a fraction of the CHF at that pressure."""
    return fraction * chf_zuber(p_bar)


def design_row(p_bar, fraction=0.6, csf=CSF):
    q = design_flux(p_bar, fraction)
    dt = steady_superheat(q, p_bar, csf)
    return {"p_bar": p_bar, "t_sat": props(p_bar)["T"], "flux": q, "superheat": dt, "wall_c": props(p_bar)["T"] + dt}


def simulate_power(q_target, p_bar, t_end=60.0, dt_s=0.005, ramp=10.0, csf=CSF, c_plate=C_PLATE):
    """Lumped plate heated by a flux rising linearly to q_target over `ramp` s. Returns dict with t, dT, burnout_time."""
    n = int(round(t_end / dt_s))
    t = np.arange(n + 1) * dt_s
    dT = np.zeros(n + 1)
    burn = None
    last = n
    for k in range(n + 1):
        if dT[k] >= DT_LIMIT:
            burn, last = t[k], k
            break
        if k < n:
            q_in = q_target * min(1.0, t[k] / ramp)
            dT[k + 1] = dT[k] + dt_s * (q_in - boiling_flux(dT[k], p_bar, csf)) / c_plate
    return {"t": t[:last + 1], "dT": dT[:last + 1], "burnout_time": burn}


def burnout_time(q_target, p_bar, **kw):
    return simulate_power(q_target, p_bar, **kw)["burnout_time"]


# %% [markdown]
# ## Step 7: see it
# Left: the boiling curve at 1 atm and at 5 bar, log-log, with the CHF and the minimum flux of each
# marked. Right: the CHF against pressure, with the constant 1.1 MW/m2 that the hand-picked curve
# gave, and the wall superheat needed to carry 500 kW/m2 in nucleate boiling.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    dts = np.logspace(0, math.log10(1500.0), 500)
    for p_bar, col, ls in ((ATM, "#c0561b", "-"), (5.0, "#0072b2", "--")):
        ax.loglog(dts, [boiling_flux(d, p_bar) / 1e3 for d in dts], color=col, ls=ls, lw=2,
                  label=f"{p_bar:g} bar (T_sat {props(p_bar)['T']:.0f} C)")
        ax.plot([dt_chf(p_bar)], [chf_zuber(p_bar) / 1e3], "o", color=col)
        ax.plot([dt_min(p_bar)], [q_min(p_bar) / 1e3], "s", color=col)
    ax.set_xlabel("wall superheat T_wall - T_sat (K, log scale)")
    ax.set_ylabel("heat flux (kW/m2, log scale)")
    ax.set_title("Boiling curve from correlations (circle: CHF, square: minimum)", fontsize=10)
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "boiling_curves.png", dpi=120)

    ps = np.geomspace(P_MIN, P_MAX, 80)
    fig2, axs = plt.subplots(1, 2, figsize=(9.6, 3.8))
    axs[0].plot(ps, [chf_zuber(p) / 1e6 for p in ps], color="#0072b2", lw=2, label="Zuber CHF from properties")
    axs[0].axhline(Q_CHF_SHIPPED / 1e6, color="#8a1a5b", ls=":", lw=2, label="hand-picked curve: 1.1 at any pressure")
    axs[0].plot([ATM, 5.0], [chf_zuber(ATM) / 1e6, chf_zuber(5.0) / 1e6], "ko")
    axs[0].set_xlabel("pressure (bar absolute)")
    axs[0].set_ylabel("critical heat flux (MW/m2)")
    axs[0].set_title("CHF rises with pressure", fontsize=10)
    axs[0].legend(fontsize=8)
    axs[0].grid(alpha=0.3)
    for csf, col, ls in ((0.008, "#c0561b", "--"), (CSF, "#0072b2", "-"), (0.02, "#8a1a5b", ":")):
        axs[1].plot(ps, [rohsenow_superheat(5e5, p, csf) for p in ps], color=col, ls=ls, lw=2, label=f"Csf = {csf}")
    axs[1].set_xlabel("pressure (bar absolute)")
    axs[1].set_ylabel("wall superheat for 500 kW/m2 (K)")
    axs[1].set_title("Boiling gets easier at higher pressure", fontsize=10)
    axs[1].legend(fontsize=8)
    axs[1].grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "chf_pressure.png", dpi=120)

    print("pressure study (CHF in MW/m2, minimum flux in kW/m2, superheats in K):")
    for p_bar in (0.5, ATM, 2.0, 5.0, 10.0, 20.0):
        r = pressure_row(p_bar)
        print(f"  {p_bar:6.2f} bar: T_sat {r['t_sat']:6.1f} C  CHF {r['chf'] / 1e6:5.3f} ({r['chf_ratio']:4.2f}x)  dT at CHF {r['dt_chf']:5.1f}  q_min {r['q_min'] / 1e3:6.1f}  dt_min {r['dt_min']:6.0f}  q at 10 K {r['q_10K'] / 1e3:6.0f}")
    f = chf_factors(5.0)
    print("5 bar against 1 atm: sqrt(rho_v)", round(f["sqrt_rho_v"], 3), " h_fg", round(f["h_fg"], 3), " capillary", round(f["capillary"], 3), " ratio", round(f["ratio"], 3))
    print("burnout time after a step to 1.3 MW/m2 (s): 1 atm", burnout_time(1.3e6, ATM), " 5 bar", burnout_time(1.3e6, 5.0))
    print("design flux at 60 percent of the CHF:")
    for p_bar in (0.5, ATM, 2.0, 5.0, 10.0):
        r = design_row(p_bar)
        print(f"  {p_bar:6.2f} bar: {r['flux'] / 1e3:6.0f} kW/m2, superheat {r['superheat']:5.1f} K, wall {r['wall_c']:6.1f} C")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
