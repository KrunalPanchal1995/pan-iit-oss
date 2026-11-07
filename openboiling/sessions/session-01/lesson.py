"""Session 1 (Level 1): heating water until it boils, and the four stages of boiling.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: why a pot of water gets stuck at 100 C
# **A. Real-world problem.** You put a pot on the stove. For a few minutes the water just gets
# warmer. Then bubbles appear at the bottom, and from that moment the temperature stops rising,
# even though the heater keeps pouring in energy. Where does the energy go? And why do bubbles
# appear on the hot surface and not in the middle of the water?
#
# **Plan.** (1) heat water with a constant power and watch the temperature, (2) find where the
# energy goes once it boils, (3) meet the *boiling curve*: how the heat leaving a hot surface
# changes as the surface gets hotter than the boiling point.
#
# **Assumptions.** Water at normal air pressure (boils at 100 C); all the heater power goes into
# the water, reduced by an efficiency of 0.85; one uniform water temperature; no evaporation below
# the boiling point. This is a simplified teaching model.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

CP = 4186.0        # J/(kg K): energy to warm 1 kg of water by 1 K (specific heat)
LATENT = 2.257e6   # J/kg: energy to turn 1 kg of boiling water into steam (latent heat)
T_BOIL = 100.0     # degrees C at normal air pressure
EFF = 0.85         # fraction of heater power that reaches the water


# %% [markdown]
# ## Step 1: warm, then boil
# While `T < 100`, all the useful power warms the water: `m * CP * dT/dt = EFF * P`.
# Once `T = 100`, the energy makes steam instead: `m_dot = EFF * P / LATENT` kilograms of water
# leave every second, and the temperature stays at 100 C.

# %%
def time_to_boil(power_w, mass_kg, t_start=20.0):
    """Seconds until the water reaches 100 C."""
    return mass_kg * CP * (T_BOIL - t_start) / (EFF * power_w)


def heating_state(t, power_w, mass_kg, t_start=20.0):
    """Water temperature (C) and mass boiled away (kg) after t seconds of heating."""
    tb = time_to_boil(power_w, mass_kg, t_start)
    temp = min(T_BOIL, t_start + EFF * power_w * t / (mass_kg * CP))
    boiled = 0.0 if t <= tb else EFF * power_w * (t - tb) / LATENT
    return temp, boiled


# %% [markdown]
# ## Step 2: the boiling curve (the idea in one picture)
# Hold a metal surface at a temperature `dT` degrees above the boiling point and measure the heat
# flux `q` leaving it, in watts per square metre. Four stages appear:
#
# 1. **natural convection** (dT below about 5 K): no bubbles, warm water rises quietly;
# 2. **nucleate boiling** (about 5 to 30 K): bubbles form on tiny pits, stir the water, and `q`
#    rises very steeply;
# 3. **critical heat flux, then transition boiling** (about 30 to 120 K): so much vapour that
#    liquid cannot reach the surface, and `q` falls;
# 4. **film boiling** (above about 120 K): a vapour blanket insulates the surface, `q` is small.
#
# The numbers below are ILLUSTRATIVE (a drawing aid), chosen to give the right shape and a peak
# near 1.1 MW per square metre for water; real values depend on the surface.

# %%
_DT_PTS = np.array([0.0, 5.0, 10.0, 20.0, 30.0, 120.0, 300.0])
_Q_PTS = np.array([0.0, 5.0e3, 4.07e4, 3.26e5, 1.1e6, 2.5e4, 6.25e4])     # W/m^2 at those superheats


def flux_curve(dt):
    """Illustrative heat flux (W/m^2) leaving a surface dt kelvin above the boiling point."""
    dt = np.asarray(dt, dtype=float)
    logq = np.interp(dt, _DT_PTS[1:], np.log(_Q_PTS[1:]))
    return np.where(dt < _DT_PTS[1], _Q_PTS[1] * dt / _DT_PTS[1], np.exp(logq))


def stage_name(dt):
    """Name of the boiling stage for wall superheat dt (kelvin)."""
    if dt < 5.0:
        return "natural convection"
    if dt <= 30.0:
        return "nucleate boiling"
    if dt <= 120.0:
        return "transition boiling"
    return "film boiling"


# %% [markdown]
# ## Step 3: see it
# Left: the temperature stops at 100 C and the boiled-off mass starts to climb. Right: the labelled
# boiling curve (log scale on the flux, because it spans a factor of 40).

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    P, M = 2000.0, 1.0
    ts = np.linspace(0, 420, 421)
    st = np.array([heating_state(t, P, M) for t in ts])
    tb = time_to_boil(P, M)
    print(f"{M} kg at {P:.0f} W: boils after {tb:.0f} s; boiled away after 420 s: {st[-1, 1] * 1000:.0f} g")
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(ts, st[:, 0], label="water temperature")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("water temperature (degrees C)", color="tab:blue")
    ax.axvline(tb, color="gray", ls=":")
    ax.annotate("bubbles start", (tb + 5, 40), fontsize=8)
    ax2 = ax.twinx()
    ax2.plot(ts, st[:, 1] * 1000, color="tab:red")
    ax2.set_ylabel("water boiled away (g)", color="tab:red")
    ax.set_title("1 kg of water on a 2 kW heater: it stops at 100 C")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "heating_curve.png", dpi=120)

    dts = np.linspace(0.3, 250, 800)
    fig2, ax3 = plt.subplots(figsize=(6.4, 4.2))
    ax3.semilogy(dts, flux_curve(dts) / 1e3)
    for xx, yy, lab in ((16, 3, "1 natural\nconvection"), (8, 200, "2 nucleate"), (80, 300, "3 transition"), (190, 80, "4 film")):
        ax3.annotate(lab, (xx, yy), fontsize=8, ha="center")
    ax3.plot([30], [1100], "ro")
    ax3.annotate("critical heat flux", (30, 1100), (45, 1300), fontsize=8, color="r")
    ax3.set_ylim(1, 3000)
    ax3.set_xlabel("wall superheat T_wall - 100 C (K)")
    ax3.set_ylabel("heat flux q (kW/m2, log scale)")
    ax3.set_title("The boiling curve (illustrative)")
    ax3.grid(alpha=0.3, which="both")
    fig2.tight_layout()
    fig2.savefig(OUT / "boiling_curve_levels.png", dpi=120)
    for d in (2, 10, 30, 60, 200):
        print(f"superheat {d:3d} K: {stage_name(d):20s} q = {float(flux_curve(d)) / 1e3:8.1f} kW/m2")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
