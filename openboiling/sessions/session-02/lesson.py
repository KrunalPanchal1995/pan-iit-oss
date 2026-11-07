"""Session 2 (Level 2): the energy and heat-flux numbers behind boiling.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: energy to boil, heat flux, and the limits of a heater
# **A. Real-world problem.** An electric kettle must bring 1.7 kg of water to the boil in four
# minutes. How many watts is that? And once we know the power, how hot does the metal element get,
# how close is it to the critical heat flux (the point where boiling stops working and the
# surface overheats), and how big must the element be to stay safely away from it?
#
# **Safety and scope.** Simplified teaching model with approximate handbook water properties at
# 1 atm. Not a design tool for real appliances: real elements, water level protection and
# certification are far more demanding. Never bypass a kettle's boil-dry protection.
#
# **Assumptions.** Water at 100 C and 1 atm; constant properties; the heat flux is the same over the
# whole element (uniform); empirical scalings are used as typical shapes, with an uncertain
# coefficient.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G = 9.81            # m/s^2
CP = 4186.0         # J/(kg K), liquid water (average 20 to 100 C)
H_FG = 2.257e6      # J/kg latent heat at 100 C
RHO_L = 958.4       # kg/m^3 liquid at 100 C
RHO_V = 0.596       # kg/m^3 vapour at 100 C, 1 atm
SIGMA = 0.0589      # N/m surface tension at 100 C
MU_L = 2.82e-4      # Pa s liquid viscosity at 100 C
CP_L = 4216.0       # J/(kg K) liquid cp at 100 C
PR_L = 1.75         # Prandtl number of liquid water at 100 C
EFF = 0.85          # fraction of electrical power reaching the water
C_NB = 1.1e6 / 30.0 ** 3   # W/(m^2 K^3) illustrative nucleate coefficient: 1.1 MW/m2 at 30 K


# %% [markdown]
# ## Step 1: energy to boil
# Warming `m` kg by `dT` takes `m cp dT`. Turning `m_s` kg of boiling water into steam takes
# `m_s L`. With an efficiency `eta`, the heating time at power `P` is `t = Q / (eta P)`.

# %%
def energy_to_heat(mass, t_from, t_to=100.0):
    """Sensible heat, joules."""
    return mass * CP * (t_to - t_from)


def energy_to_vaporise(mass):
    """Latent heat, joules."""
    return mass * H_FG


def heating_time(power_w, mass, t_from=20.0, eff=EFF):
    """Seconds to bring `mass` kg from t_from to 100 C."""
    return energy_to_heat(mass, t_from) / (eff * power_w)


def power_for_time(mass, t_target_s, t_from=20.0, eff=EFF):
    """Electrical power (W) needed to reach 100 C in t_target_s seconds."""
    return energy_to_heat(mass, t_from) / (eff * t_target_s)


# %% [markdown]
# ## Step 2: heat flux and wall superheat
# The heater has an area `A`. The heat flux is `q = eta P / A` (W/m^2). Newton's law of cooling
# defines a heat transfer coefficient `h = q / (T_wall - T_sat)`. In nucleate boiling `h` is not
# constant: it grows with the flux, because more bubbles stir the water more. The classic
# Rohsenow-type result is an EMPIRICAL SCALING `q proportional to dT_sat^3`, where `dT_sat =
# T_wall - T_sat`. In published data the exponent is typically between about 2.5 and 4 (3 is the
# usual textbook value) and the coefficient changes by a factor of several with the surface
# material, roughness and cleanliness.

# %%
def heat_flux(power_w, area, eff=EFF):
    return eff * power_w / area


def superheat_from_flux(q, c=C_NB):
    """Invert q = c dT^3 for the nucleate-boiling wall superheat (K)."""
    return (q / c) ** (1.0 / 3.0)


def nucleate_flux(dt, c=C_NB):
    return c * dt ** 3


def heat_transfer_coeff(q, c=C_NB):
    """h = q / dT in W/(m^2 K); for q = c dT^3 it is c dT^2."""
    return q / superheat_from_flux(q, c)


def rohsenow_flux(dt, csf=0.013, n=1.0):
    """Rohsenow-type nucleate boiling flux (W/m^2) for water at 1 atm.

    q = mu h_fg sqrt(g (rho_l - rho_v) / sigma) * (cp dT / (Csf h_fg Pr^n))^3
    csf is a surface-fluid constant (about 0.013 for clean water-metal pairs; it varies with the
    surface), n = 1 for water.
    """
    lead = MU_L * H_FG * math.sqrt(G * (RHO_L - RHO_V) / SIGMA)
    return lead * (CP_L * dt / (csf * H_FG * PR_L ** n)) ** 3


# %% [markdown]
# ## Step 3: the critical heat flux and the bubble size
# Zuber's hydrodynamic estimate for the critical heat flux of a large flat heater:
# `q_chf = 0.131 h_fg sqrt(rho_v) (sigma g (rho_l - rho_v))^(1/4)`. For water at 1 atm it gives
# about 1.1 MW/m^2 (the commonly quoted figure is roughly 1 MW/m^2, an approximate value that
# varies with the surface and conditions).
#
# A bubble leaves the surface when buoyancy beats surface tension. Fritz's classic estimate of the
# departure diameter is `D = 0.0208 theta sqrt(sigma / (g (rho_l - rho_v)))` with the contact angle
# `theta` in degrees. It is an empirical scaling: the size scales with the capillary length
# `sqrt(sigma / (g d_rho))` (about 2.5 mm for water at 100 C).

# %%
def chf_zuber(sigma=SIGMA, rho_l=RHO_L, rho_v=RHO_V, h_fg=H_FG):
    return 0.131 * h_fg * math.sqrt(rho_v) * (sigma * G * (rho_l - rho_v)) ** 0.25


def capillary_length(sigma=SIGMA, rho_l=RHO_L, rho_v=RHO_V):
    return math.sqrt(sigma / (G * (rho_l - rho_v)))


def departure_diameter(theta_deg):
    """Fritz departure diameter in metres."""
    return 0.0208 * theta_deg * capillary_length()


# %% [markdown]
# ## Step 4: design the heater
# Given a target heating time and an element area, `design_heater` returns the power, the flux,
# the wall superheat and the safety factor on the critical heat flux. `min_area_for_margin`
# finds the smallest area that keeps the safety factor above a chosen value.

# %%
def design_heater(mass, t_target_s, area, t_from=20.0, eff=EFF, c=C_NB, chf=1.1e6):
    p = power_for_time(mass, t_target_s, t_from, eff)
    q = heat_flux(p, area, eff)
    dt = superheat_from_flux(q, c)
    return {"power_w": p, "flux": q, "superheat_k": dt, "wall_c": 100.0 + dt, "chf_margin": chf / q}


def min_area_for_margin(power_w, margin, chf=1.1e6, eff=EFF):
    """Smallest area (m^2) so that q_chf / q >= margin."""
    return margin * eff * power_w / chf


# %% [markdown]
# ## Step 5: see it
# Left: the heat flux against wall superheat; the cubic law rises to the critical heat flux.
# Right: the heating time against power for 1.7 kg of water.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    d = design_heater(1.7, 240.0, 0.01)
    print("kettle:", {k: round(v, 3) for k, v in d.items()})
    print("Zuber CHF (kW/m2):", round(chf_zuber() / 1e3, 1), " capillary length (mm):", round(capillary_length() * 1e3, 3))
    print("Fritz departure diameter at 45 deg (mm):", round(departure_diameter(45) * 1e3, 2))
    print("Rohsenow at 10 K (kW/m2):", round(rohsenow_flux(10.0) / 1e3, 1))
    dts = np.linspace(0.5, 32, 200)
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.8))
    axs[0].plot(dts, nucleate_flux(dts) / 1e3, label="illustrative: q = 40.7 dT^3")
    axs[0].plot(dts, [rohsenow_flux(x) / 1e3 for x in dts], "--", label="Rohsenow-type, Csf = 0.013")
    axs[0].axhline(chf_zuber() / 1e3, color="r", ls=":", label="Zuber CHF, about 1100")
    axs[0].set_ylim(0, 1500)
    axs[0].set_xlabel("wall superheat T_wall - 100 C (K)")
    axs[0].set_ylabel("heat flux (kW/m2)")
    axs[0].set_title("Nucleate boiling: q grows as dT^3")
    axs[0].legend(fontsize=7)
    axs[0].grid(alpha=0.3)
    ps = np.linspace(500, 5000, 100)
    axs[1].plot(ps, [heating_time(p, 1.7) for p in ps])
    axs[1].plot([d["power_w"]], [240], "ro")
    axs[1].set_xlabel("heater power (W)")
    axs[1].set_ylabel("time to 100 C (s)")
    axs[1].set_title("1.7 kg from 20 C: time falls as 1/P")
    axs[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "flux_and_time.png", dpi=120)

    th = np.linspace(5, 90, 50)
    fig2, ax2 = plt.subplots(figsize=(5.6, 4))
    ax2.plot(th, [departure_diameter(x) * 1e3 for x in th])
    ax2.set_xlabel("contact angle (degrees)")
    ax2.set_ylabel("bubble departure diameter (mm)")
    ax2.set_title("Fritz scaling: bigger contact angle, bigger bubble")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "departure_diameter.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
