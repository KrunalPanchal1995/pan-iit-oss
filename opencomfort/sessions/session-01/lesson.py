"""Session 1 (Level 1): where the heat in a hot room comes from, and the two passive levers.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: where the heat comes from
# **A. Real-world problem.** On an April afternoon in Chennai a closed room with a sunny
# west window can feel hotter than the street outside. Where does that heat come from? And
# why do two cheap, old ideas, a sunshade over the window (a "chajja") and open windows,
# make such a big difference without using any electricity?
#
# **Plan.** (1) heat flow through walls and roof, Q = U A dT, (2) sunshine through glass,
# Q = SHGC A I, (3) heat from people and lamps, (4) heat carried by air flowing through the
# room, (5) the steady-state indoor temperature where heat in = heat out.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
RHO_CP = 1200.0   # J/(m3 K): air density 1.2 kg/m3 times specific heat about 1000 J/(kg K)


# %% [markdown]
# ## Step 1: heat through walls, roof and glass (conduction)
# Heat flows from hot to cold. Through a wall of area A (m2) with a temperature difference
# dT (K) between outside and inside air, the heat flow in watts is
#
#     Q = U A dT
#
# U (W/(m2 K)) is the U-value: how many watts get through 1 m2 for each kelvin of
# difference. A 230 mm brick wall has U about 2, a bare concrete roof 2.5 to 3.5, a
# single glass pane about 5 to 6. Lower U means better insulation.

# %%
def conduction_gain(u, area, t_out, t_in):
    """Heat flow into the room through one surface (W). Positive when outside is hotter."""
    if u < 0 or area < 0:
        raise ValueError("U-value and area must not be negative")
    return u * area * (t_out - t_in)


def ua_total(surfaces):
    """Sum of U x A over a list of (U, A) pairs: the room's conductance in W/K."""
    return float(sum(u * a for u, a in surfaces))


# %% [markdown]
# ## Step 2: sunshine through the window (solar gain)
# Sunlight falling on a window brings I watts per m2 (the irradiance). Clear glass lets
# most of it in. The solar heat gain coefficient SHGC (no unit, 0 to 1) is the share that
# ends up as heat in the room: about 0.8 for clear single glass. A shade outside the window
# stops part of the sun **before** it reaches the glass. If the shade blocks a fraction s
# of the sunshine:
#
#     Q_sun = (1 - s) x SHGC x A_window x I

# %%
def solar_gain(area, shgc, irradiance, shaded=0.0):
    """Solar heat gain through a window (W). `shaded` is the fraction of sun blocked (0 to 1)."""
    if not (0.0 <= shaded <= 1.0) or not (0.0 <= shgc <= 1.0):
        raise ValueError("shaded fraction and SHGC must be between 0 and 1")
    if area < 0 or irradiance < 0:
        raise ValueError("area and irradiance must not be negative")
    return (1.0 - shaded) * shgc * area * irradiance


# %% [markdown]
# ## Step 3: heat from people, lamps and fans (internal gains)
# A resting adult gives off about 75 W of sensible heat (the part that warms the air).
# Lamps, a laptop and a ceiling fan add their electrical power as heat.

# %%
def internal_gain(people, equipment_w, w_per_person=75.0):
    """Heat from people and equipment (W)."""
    if people < 0 or equipment_w < 0:
        raise ValueError("people and equipment must not be negative")
    return people * w_per_person + equipment_w


# %% [markdown]
# ## Step 4: heat carried by air (ventilation)
# When outdoor air replaces indoor air, it carries heat. The air change rate ACH (per hour)
# says how many times the room's air volume is replaced in one hour. The flow is
# V_dot = ACH x Vol / 3600 (m3/s), and the heat it brings in is
#
#     Q_vent = rho cp V_dot (T_out - T_in)        rho cp = 1200 J/(m3 K)
#
# If outside is hotter, air flow heats the room; if outside is cooler, it cools the room.

# %%
def flow_rate(ach, volume):
    """Air flow in m3/s from air changes per hour and room volume (m3)."""
    if ach < 0 or volume <= 0:
        raise ValueError("need ACH >= 0 and volume > 0")
    return ach * volume / 3600.0


def ventilation_conductance(ach, volume):
    """rho cp V_dot in W/K: the ventilation 'U x A'."""
    return RHO_CP * flow_rate(ach, volume)


def ventilation_gain(ach, volume, t_out, t_in):
    """Heat brought in by ventilation (W). Positive when outside air is hotter."""
    return ventilation_conductance(ach, volume) * (t_out - t_in)


# %% [markdown]
# ## Step 5: the steady-state indoor temperature
# If nothing changes for a long time, the room settles where heat in = heat out:
#
#     (UA + H_v)(T_in - T_out) = Q_sun + Q_int       H_v = rho cp V_dot
#
#     T_in = T_out + (Q_sun + Q_int) / (UA + H_v)
#
# The sun and the people push the room **above** outdoor temperature; the walls and the
# air flow pull it back down. Shading shrinks the top of the fraction; ventilation grows
# the bottom. That is the whole idea of passive cooling in one line.

# %%
def steady_indoor_temperature(t_out, ua, h_vent, q_sun, q_int):
    """Indoor air temperature (degrees C) where all heat flows balance."""
    if ua + h_vent <= 0:
        raise ValueError("the room must lose heat somehow: UA + H_v must be positive")
    return t_out + (q_sun + q_int) / (ua + h_vent)


def heat_balance(t_out, t_in, ua, h_vent, q_sun, q_int):
    """Net heat flow into the room (W); zero at steady state."""
    return ua * (t_out - t_in) + h_vent * (t_out - t_in) + q_sun + q_int


# The example room used throughout: 4 m x 4 m x 3 m on the top floor, one west wall outside.
ROOM = {
    "volume": 48.0,                                # m3
    "surfaces": [(2.0, 10.0),                      # brick wall 10 m2 (12 m2 minus window), U = 2
                 (5.0, 2.0),                       # single-glazed window 2 m2, U = 5
                 (2.5, 16.0)],                     # concrete roof 16 m2, U = 2.5
    "window_area": 2.0, "shgc": 0.8,
}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t_out, sun = 34.0, 500.0                       # afternoon air (C) and sun on the west window (W/m2)
    ua = ua_total(ROOM["surfaces"])
    q_int = internal_gain(2, 100.0)
    print(f"UA = {ua:.0f} W/K, internal gains = {q_int:.0f} W")

    # Figure 1: steady indoor temperature for four designs
    designs = [("closed,\nno shade", 0.0, 0.5), ("closed,\nshaded 80%", 0.8, 0.5),
               ("open 10 ACH,\nno shade", 0.0, 10.0), ("open 10 ACH,\nshaded 80%", 0.8, 10.0)]
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    for i, (name, s, ach) in enumerate(designs):
        q_sun = solar_gain(ROOM["window_area"], ROOM["shgc"], sun, s)
        h_v = ventilation_conductance(ach, ROOM["volume"])
        t_in = steady_indoor_temperature(t_out, ua, h_v, q_sun, q_int)
        ax.bar(i, t_in - t_out, bottom=t_out, color=["#d9534f", "#e9a23b", "#90a4ae", "#2a9d8f"][i])
        ax.text(i, t_in + 0.3, f"{t_in:.1f} C", ha="center", fontsize=9)
        print(f"{name.replace(chr(10), ' '):26s} sun {q_sun:4.0f} W, H_v {h_v:5.0f} W/K -> steady indoor {t_in:.1f} C")
    ax.axhline(t_out, color="k", ls="--", lw=1)
    ax.text(3.45, t_out - 0.9, "outdoor 34 C", ha="right", fontsize=9)
    ax.set_xticks(range(4))
    ax.set_xticklabels([d[0] for d in designs], fontsize=9)
    ax.set_ylim(30, 50)
    ax.set_ylabel("steady indoor temperature (C)")
    ax.set_title("Shade cuts the gain; air flow carries it away (34 C outside, 500 W/m2 sun)")
    fig.tight_layout()
    fig.savefig(OUT / "steady_designs.png", dpi=120)

    # Figure 2: steady indoor temperature against air change rate, with and without shade
    ach = np.linspace(0.5, 30, 200)
    fig2, ax2 = plt.subplots(figsize=(6.6, 4.2))
    for s, col, lab in [(0.0, "#d9534f", "no shade"), (0.8, "#2a9d8f", "shade blocks 80% of the sun")]:
        q_sun = solar_gain(ROOM["window_area"], ROOM["shgc"], sun, s)
        t = [steady_indoor_temperature(t_out, ua, ventilation_conductance(a, ROOM["volume"]), q_sun, q_int) for a in ach]
        ax2.plot(ach, t, color=col, lw=2, label=lab)
        for a in (0.5, 10.0):
            ti = steady_indoor_temperature(t_out, ua, ventilation_conductance(a, ROOM["volume"]), q_sun, q_int)
            print(f"{lab:28s} ACH {a:4.1f}: steady indoor {ti:.1f} C")
    ax2.axhline(t_out, color="k", ls="--", lw=1)
    ax2.text(29.5, t_out + 0.3, "outdoor 34 C", ha="right", fontsize=9)
    ax2.set_xlabel("air changes per hour, ACH (1/h)")
    ax2.set_ylabel("steady indoor temperature (C)")
    ax2.set_title("Ventilation pulls the room toward outdoor; shade lowers the excess")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=9)
    fig2.tight_layout()
    fig2.savefig(OUT / "indoor_vs_ach.png", dpi=120)

# %% [markdown]
# ## Where this stops
# We assumed the sun's strength on the window (500 W/m2) and the shaded fraction (80%).
# Session 2 works both out from the sun's position, sizes a real overhang, and computes the
# air changes that wind and warm air actually produce through a window.
