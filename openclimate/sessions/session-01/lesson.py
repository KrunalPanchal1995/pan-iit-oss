"""Session 1 (Level 1): a bare planet balances sunlight in against heat radiated out.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: sunlight in, heat out
# **A. Real-world problem.** The Sun pours energy onto the Earth every second, yet the
# Earth does not keep heating up. Something must carry the same amount of energy away. What,
# and at what temperature does the planet settle? If we do the sum for an Earth with no
# atmosphere, do we get the 15 degrees C we live at?
#
# **Plan.** (1) sunlight absorbed per square metre, with the factor 4 and the albedo,
# (2) the Stefan-Boltzmann law for heat radiated, (3) balance the two to get the
# equilibrium temperature, (4) compare with the real Earth, Venus and Mars.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
SIGMA = 5.670374419e-8      # Stefan-Boltzmann constant, W/(m2 K4)
S_EARTH = 1361.0            # solar constant at Earth, W/m2
ALBEDO_EARTH = 0.30         # share of sunlight reflected straight back to space, no unit


# %% [markdown]
# ## Step 1: how much sunlight does the planet absorb?
# Sunlight arrives at S watts on every square metre facing the Sun. The planet catches it on
# a disc of area pi R^2 but spreads it, as it spins, over a sphere of area 4 pi R^2, so the
# average per square metre of surface is S / 4. A share called the **albedo** (alpha) is
# reflected by clouds, ice and deserts; the rest is absorbed:
#
#     absorbed = S (1 - alpha) / 4          (W/m2)

# %%
def absorbed_solar(s=S_EARTH, albedo=ALBEDO_EARTH):
    """Sunlight absorbed per square metre of planet surface, averaged over the sphere (W/m2)."""
    if s <= 0 or not 0.0 <= albedo <= 1.0:
        raise ValueError("need S > 0 and 0 <= albedo <= 1")
    return s * (1.0 - albedo) / 4.0


# %% [markdown]
# ## Step 2: how much heat does a warm surface radiate?
# Every object radiates heat as infrared light. The **Stefan-Boltzmann law** says a perfect
# radiator (emissivity 1) at absolute temperature T sends out sigma T^4 watts per square
# metre. T must be in **kelvin** (K = degrees C + 273.15); doubling T multiplies the
# radiation by 16.

# %%
def emitted(t, emissivity=1.0):
    """Infrared radiated per square metre by a surface at temperature t (K): eps sigma T^4."""
    t = np.asarray(t, float)
    if np.any(t < 0) or not 0.0 < emissivity <= 1.0:
        raise ValueError("need T >= 0 K and 0 < emissivity <= 1")
    return emissivity * SIGMA * t ** 4


def to_celsius(t_kelvin):
    """Kelvin to degrees Celsius."""
    return t_kelvin - 273.15


# %% [markdown]
# ## Step 3: the balance
# If the planet absorbs more than it radiates it warms up, radiates more, and so moves
# toward the temperature where the two are equal. This **equilibrium temperature** is
#
#     S (1 - alpha) / 4 = sigma T^4      so      T_e = [ S (1 - alpha) / (4 sigma) ]^(1/4)

# %%
def net_flux(t, s=S_EARTH, albedo=ALBEDO_EARTH):
    """Absorbed minus emitted (W/m2). Positive means the planet is warming up."""
    return absorbed_solar(s, albedo) - emitted(t)


def equilibrium_temperature(s=S_EARTH, albedo=ALBEDO_EARTH, emissivity=1.0):
    """Temperature (K) at which a bare planet radiates exactly what it absorbs."""
    return (absorbed_solar(s, albedo) / (emissivity * SIGMA)) ** 0.25


def greenhouse_warming(t_observed, s=S_EARTH, albedo=ALBEDO_EARTH):
    """How much warmer the real surface is than the bare-planet estimate (K)."""
    return t_observed - equilibrium_temperature(s, albedo)


# %% [markdown]
# ## Step 4: three planets
# Approximate values (NASA planetary fact sheets): solar constant S, Bond albedo and the
# mean surface temperature that is actually measured.

# %%
PLANETS = {
    "Venus": {"s": 2601.0, "albedo": 0.77, "t_obs": 737.0},
    "Earth": {"s": 1361.0, "albedo": 0.30, "t_obs": 288.0},
    "Mars": {"s": 586.0, "albedo": 0.25, "t_obs": 210.0},
}

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    asr = absorbed_solar()
    te = equilibrium_temperature()
    print(f"Earth absorbs {asr:.1f} W/m2; bare-planet temperature {te:.1f} K = {to_celsius(te):.1f} C")
    print(f"a surface at 288 K radiates {float(emitted(288.0)):.1f} W/m2; greenhouse warming {greenhouse_warming(288.0):.1f} K")

    # Figure 1: absorbed sunlight is flat, emitted heat grows as T^4; they cross at T_e
    t = np.linspace(180.0, 320.0, 300)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(t, emitted(t), color="#d9534f", lw=2.2, label="heat radiated  sigma T^4")
    ax.axhline(asr, color="#e9a23b", lw=2.2, label=f"sunlight absorbed  {asr:.0f} W/m2")
    ax.fill_between(t, emitted(t), asr, where=emitted(t) < asr, color="#e9a23b", alpha=0.15)
    ax.fill_between(t, emitted(t), asr, where=emitted(t) > asr, color="#1f6feb", alpha=0.12)
    ax.plot([te], [asr], "ko")
    ax.annotate(f"balance: T_e = {te:.1f} K", (te, asr), textcoords="offset points", xytext=(-160, 60),
                arrowprops=dict(arrowstyle="->"))
    ax.axvline(288.0, color="#2a9d8f", ls="--", lw=1.2)
    ax.text(289.5, 60, "real Earth\n288 K", color="#2a9d8f", fontsize=9)
    ax.text(205, 165, "warms up\n(in > out)", fontsize=9)
    ax.text(300, 180, "cools down\n(out > in)", fontsize=9, ha="center")
    ax.set_xlabel("surface temperature T (K)")
    ax.set_ylabel("energy flow (W/m2)")
    ax.set_title("A bare Earth settles where energy in = energy out")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "energy_balance.png", dpi=120)

    # Figure 2: bare-planet estimate against the measured surface temperature
    names = list(PLANETS)
    bare = [equilibrium_temperature(PLANETS[n]["s"], PLANETS[n]["albedo"]) for n in names]
    obs = [PLANETS[n]["t_obs"] for n in names]
    x = np.arange(len(names))
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.bar(x - 0.18, bare, 0.36, color="#e9a23b", label="bare planet T_e (model)")
    ax2.bar(x + 0.18, obs, 0.36, color="#d9534f", label="measured surface (approx.)")
    for xi, b, o in zip(x, bare, obs):
        ax2.text(xi - 0.18, b + 8, f"{b:.0f}", ha="center", fontsize=9)
        ax2.text(xi + 0.18, o + 8, f"{o:.0f}", ha="center", fontsize=9)
        print(f"{names[xi]}: bare {b:.0f} K, measured {o:.0f} K, difference {o - b:+.0f} K")
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{n}\n(+{o - b:.0f} K)" for n, b, o in zip(names, bare, obs)])
    ax2.set_ylabel("temperature (K)")
    ax2.set_ylim(0, 820)
    ax2.set_title("The gap between model and measurement is the greenhouse effect")
    ax2.legend(loc="upper right", fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "planets.png", dpi=120)

# %% [markdown]
# ## Where this stops
# A bare Earth would sit at about 255 K (-18 C), frozen solid. The real surface is 33 K
# warmer. Session 2 adds an atmosphere that lets sunlight through but absorbs infrared,
# and finds the missing 33 K.
