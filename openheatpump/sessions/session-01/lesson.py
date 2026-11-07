"""Session 1 (Level 1): a heat pump moves heat, a heater makes it.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a heat pump moves heat, a heater makes it
# **A. Real-world problem.** A room needs 10 kWh of heat on a cold day. An electric
# resistance heater turns 1 kWh of electricity into 1 kWh of heat, so it needs 10 kWh. A heat
# pump needs far less electricity, because most of the heat is *carried in* from the cold
# outdoor air. How can that be possible, and what controls how many kWh of heat you get for
# each kWh of electricity?
#
# **Plan.** (1) write the heater, (2) write the heat pump with its COP, (3) draw the energy
# flows, (4) see how the COP changes with the outdoor temperature.
#
# Educational model only, not an installation design.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
ETA = 0.45          # fraction of the ideal (Carnot) COP that a real machine reaches: typical, not exact


# %% [markdown]
# ## Step 1: the resistance heater
# All the electricity becomes heat: heat out = electricity in. Its "COP" is exactly 1.

# %%
def heater_electricity(heat_kwh):
    """Electricity (kWh) a resistance heater needs to deliver `heat_kwh` of heat."""
    return float(heat_kwh)


# %% [markdown]
# ## Step 2: the heat pump and its COP
# The **COP** (coefficient of performance) is heat delivered divided by electricity used:
#
#     COP = Q_hot / W        so        W = Q_hot / COP
#
# Energy is conserved, so the rest of the heat comes from outdoors: Q_outdoor = Q_hot - W.
#
# A heat pump works harder when it must lift the heat across a bigger temperature gap. The
# best possible COP (the Carnot limit, derived in Session 2) uses *kelvin* (K = C + 273.15):
#
#     COP_best = T_hot / (T_hot - T_cold)
#
# A real machine reaches roughly 40 to 50 percent of that. We use 0.45 as a typical value.

# %%
def kelvin(t_celsius):
    return t_celsius + 273.15


def heat_pump_cop(t_out_c, t_supply_c, eta=ETA):
    """Real COP = eta x Carnot COP, for heat delivered at t_supply_c from air at t_out_c."""
    lift = t_supply_c - t_out_c
    if lift <= 0:
        raise ValueError("the supply temperature must be above the outdoor temperature")
    return eta * kelvin(t_supply_c) / lift


def heat_pump_flows(heat_kwh, cop):
    """Return (electricity, heat taken from outdoors) in kWh for a delivered heat `heat_kwh`."""
    work = heat_kwh / cop
    return work, heat_kwh - work


# %% [markdown]
# ## Step 3: compare for 10 kWh of heat
# Outdoor air at 0 C, heat delivered to a floor-heating loop at 35 C.

# %%
cop0 = heat_pump_cop(0.0, 35.0)
work, outdoor = heat_pump_flows(10.0, cop0)
if __name__ == "__main__":
    print(f"COP at 0 C outdoors, 35 C supply: {cop0:.2f}")
    print(f"resistance heater: {heater_electricity(10.0):.2f} kWh electricity for 10 kWh heat")
    print(f"heat pump        : {work:.2f} kWh electricity + {outdoor:.2f} kWh from outdoors")


# %% [markdown]
# ## Step 4: draw the flows, then the COP against the outdoor temperature
# The first picture has the arrows for each machine: electric in, outdoor heat in, indoor heat
# out. The second shows the COP falling as the outdoor air gets colder.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 4.2))
    for ax, name in zip(axs, ("Resistance heater", "Heat pump")):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")
        ax.set_title(name)
        ax.add_patch(plt.Rectangle((3.5, 3), 3.5, 4, fc="#fde8d8", ec="black"))
        ax.text(5.25, 5, "house\n10 kWh\nof heat", ha="center", va="center")
        ax.annotate("", xy=(9.8, 5), xytext=(7, 5), arrowprops=dict(arrowstyle="simple", fc="#d9534f", mutation_scale=40))
        ax.text(7.2, 5.9, "heat 10 kWh", fontsize=8)
    axs[0].annotate("", xy=(3.5, 5), xytext=(0.2, 5), arrowprops=dict(arrowstyle="simple", fc="#e9c46a", mutation_scale=40))
    axs[0].text(0.2, 6.2, "electric\n10.00 kWh", color="#8a6d00")
    axs[1].annotate("", xy=(3.5, 3.8), xytext=(0.2, 3.8), arrowprops=dict(arrowstyle="simple", fc="#e9c46a", mutation_scale=14 + 26 * work / 10))
    axs[1].text(0.2, 2.2, f"electric\n{work:.2f} kWh", color="#8a6d00")
    axs[1].annotate("", xy=(3.5, 6.2), xytext=(0.2, 6.2), arrowprops=dict(arrowstyle="simple", fc="#2a9d8f", mutation_scale=14 + 26 * outdoor / 10))
    axs[1].text(0.2, 7.3, f"outdoor air\n{outdoor:.2f} kWh", color="#1b6f66")
    axs[1].text(6.2, 1.5, f"COP = {cop0:.2f}", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "energy_flows.png", dpi=120)

    to = np.linspace(-15, 15, 61)
    fig2, ax2 = plt.subplots(figsize=(6.2, 4))
    ax2.plot(to, [heat_pump_cop(t, 35.0) for t in to], label="supply 35 C (floor heating)")
    ax2.plot(to, [heat_pump_cop(t, 55.0) for t in to], label="supply 55 C (radiators)")
    ax2.axhline(1.0, color="gray", ls=":", label="resistance heater, COP = 1")
    ax2.set_xlabel("outdoor temperature (C)")
    ax2.set_ylabel("COP (heat out / electricity in, no unit)")
    ax2.set_title("The colder it is outside, the lower the COP")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "cop_vs_outdoor.png", dpi=120)
    for t in (-10, 0, 7, 15):
        print(f"outdoor {t:>3d} C: COP {heat_pump_cop(t, 35.0):.2f} (35 C supply), {heat_pump_cop(t, 55.0):.2f} (55 C supply)")

# %% [markdown]
# ## Where this stops
# Here the COP uses a made-up fraction 0.45 and ignores the house. Session 2 explains where the
# Carnot limit comes from and sizes a heat pump for a real heat loss.
