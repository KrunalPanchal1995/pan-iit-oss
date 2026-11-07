"""Session 1 (Level 1): the rocket equation and why rockets drop stages.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: the rocket equation and staging
# **A. Real-world problem.** A launch vehicle such as India's PSLV weighs about 300 tonnes on
# the pad, yet only one or two tonnes reach orbit. Almost all of the rest is propellant that
# is thrown out of the nozzle on the way up. Why does a rocket need so much propellant, and
# why does it throw away empty tanks and engines (stages) during the climb?
#
# **Plan.** (1) exhaust speed from specific impulse, (2) the rocket equation
# delta-v = ve ln(m0 / mf), (3) the speed needed for a low orbit, (4) one stage against two.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G0 = 9.80665          # standard gravity, m/s2 (used to define specific impulse)
MU = 3.986004418e14   # Earth's gravitational parameter G M, m3/s2
R_EARTH = 6.371e6     # mean Earth radius, m
DV_TO_LEO = 9400.0    # typical delta-v budget to a low orbit including losses, m/s


# %% [markdown]
# ## Step 1: exhaust speed and specific impulse
# A rocket pushes itself forward by throwing gas backwards. Engineers rate an engine by its
# **specific impulse** Isp, in seconds. The effective exhaust speed is
#
#     ve = Isp x g0        (g0 = 9.80665 m/s2)
#
# A kerosene engine at sea level has Isp near 280 to 300 s (ve near 2.9 km/s); a hydrogen
# upper-stage engine in vacuum near 450 s (ve near 4.4 km/s).

# %%
def exhaust_velocity(isp):
    """Effective exhaust speed ve (m/s) from specific impulse Isp (s)."""
    if isp <= 0:
        raise ValueError("specific impulse must be positive")
    return isp * G0


# %% [markdown]
# ## Step 2: the rocket equation
# Momentum is conserved: each small mass dm thrown back at speed ve speeds up the remaining
# rocket by dv = ve dm / m. Adding up all the small pieces (integrating) from the full mass m0
# to the empty mass mf gives the **Tsiolkovsky rocket equation**
#
#     delta-v = ve ln(m0 / mf)
#
# delta-v is the speed change the rocket could get in empty space, with no gravity and no air.
# The logarithm is the bad news: doubling the speed needs the mass ratio m0 / mf squared.

# %%
def delta_v(isp, m0, mf):
    """Ideal speed change (m/s) of one burn from full mass m0 to empty mass mf (kg)."""
    if not 0 < mf <= m0:
        raise ValueError("need 0 < mf <= m0")
    return exhaust_velocity(isp) * np.log(m0 / mf)


def mass_ratio_needed(dv, isp):
    """Mass ratio m0 / mf needed for a speed change dv (m/s): the rocket equation turned round."""
    return float(np.exp(dv / exhaust_velocity(isp)))


# %% [markdown]
# ## Step 3: how fast is orbit?
# In a circular orbit gravity supplies exactly the force needed to bend the path into a
# circle: v**2 / r = G M / r**2, so
#
#     v_circ = sqrt(G M / r),     r = R_earth + h
#
# At h = 200 km this is about 7.8 km/s. Gravity and air drag on the way up cost another
# 1.5 to 2 km/s, so a typical budget to low orbit is about 9.4 km/s (we use this number).

# %%
def circular_speed(h):
    """Speed (m/s) of a circular orbit at altitude h (m) above the mean Earth radius."""
    if h < 0:
        raise ValueError("altitude must not be negative")
    return float(np.sqrt(MU / (R_EARTH + h)))


# %% [markdown]
# ## Step 4: staging
# A stage is a set of tanks plus engines. Once its propellant is gone, its empty (dry) mass
# is dead weight. A multi-stage rocket burns stage 1, **drops** it, then lights stage 2, which
# now pushes a much lighter rocket. Each stage gets its own rocket equation and the delta-v
# values add up. Each stage is described by its propellant mass, its dry mass and its Isp.

# %%
def stack_delta_v(stages, payload):
    """Total ideal delta-v (m/s) and the list of per-stage values for a stack of stages.

    stages: list of dicts with keys prop (kg), dry (kg), isp (s), first stage first.
    payload: mass (kg) carried by the last stage."""
    if payload < 0:
        raise ValueError("payload must not be negative")
    per_stage = []
    for i, s in enumerate(stages):
        above = payload + sum(t["prop"] + t["dry"] for t in stages[i + 1:])
        m0 = above + s["prop"] + s["dry"]
        mf = above + s["dry"]
        per_stage.append(delta_v(s["isp"], m0, mf))
    return float(sum(per_stage)), per_stage


def single_stage_equivalent(stages):
    """One stage with the same total propellant and dry mass as the stack (and the stage-1 Isp)."""
    return [dict(prop=sum(s["prop"] for s in stages), dry=sum(s["dry"] for s in stages), isp=stages[0]["isp"])]


# The teaching launcher used in every session (illustrative numbers, not a real vehicle)
LAUNCHER = [dict(prop=90000.0, dry=7000.0, isp=290.0),     # stage 1: kerosene-like booster
            dict(prop=15000.0, dry=1500.0, isp=340.0)]     # stage 2: vacuum upper stage
PAYLOAD = 1000.0                                           # kg


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # numbers used in the worked example
    print(f"ve for Isp 300 s = {exhaust_velocity(300):.1f} m/s")
    print(f"delta-v for Isp 300 s, 100 t -> 25 t = {delta_v(300, 100e3, 25e3):.0f} m/s")
    print(f"circular speed at 200 km = {circular_speed(200e3):.0f} m/s")
    total, parts = stack_delta_v(LAUNCHER, PAYLOAD)
    single, _ = stack_delta_v(single_stage_equivalent(LAUNCHER), PAYLOAD)
    print(f"two stages: stage 1 {parts[0]:.0f} m/s + stage 2 {parts[1]:.0f} m/s = {total:.0f} m/s")
    print(f"same masses as one stage: {single:.0f} m/s (budget to orbit {DV_TO_LEO:.0f} m/s)")

    # Figure 1: the rocket equation, delta-v against mass ratio for three engines
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ratio = np.linspace(1.0, 20.0, 300)
    for isp, colour in ((250, "#d9534f"), (300, "#e9a23b"), (450, "#2a9d8f")):
        ax.plot(ratio, exhaust_velocity(isp) * np.log(ratio) / 1000, color=colour, label=f"Isp = {isp} s")
    ax.axhline(DV_TO_LEO / 1000, color="k", ls="--", lw=1)
    ax.text(19.8, DV_TO_LEO / 1000 + 0.2, "about 9.4 km/s needed for low orbit", ha="right", fontsize=9)
    ax.axhline(circular_speed(200e3) / 1000, color="grey", ls=":", lw=1)
    ax.text(19.8, circular_speed(200e3) / 1000 - 0.55, "orbital speed at 200 km, 7.8 km/s", ha="right", fontsize=9, color="grey")
    ax.set_xlabel("mass ratio m0 / mf (no unit)")
    ax.set_ylabel("ideal delta-v (km/s)")
    ax.set_title("The rocket equation: delta-v = ve ln(m0 / mf)")
    ax.set_xlim(1, 20)
    ax.set_ylim(0, 14)
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "rocket_equation.png", dpi=120)

    # Figure 2: staging, the same masses as one stage or as two stages
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.bar(0, single / 1000, color="#d9534f", label="one stage")
    ax2.bar(1, parts[0] / 1000, color="#264653", label="stage 1")
    ax2.bar(1, parts[1] / 1000, bottom=parts[0] / 1000, color="#2a9d8f", label="stage 2")
    ax2.text(0, single / 1000 + 0.2, f"{single / 1000:.2f} km/s", ha="center")
    ax2.text(1, total / 1000 + 0.2, f"{total / 1000:.2f} km/s", ha="center")
    ax2.axhline(DV_TO_LEO / 1000, color="k", ls="--", lw=1)
    ax2.text(1.45, DV_TO_LEO / 1000 + 0.15, "needed: 9.4 km/s", ha="right", fontsize=9)
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(["one stage\n(105 t propellant, 8.5 t dry)", "two stages\n(drop 7 t after stage 1)"])
    ax2.set_ylabel("ideal delta-v (km/s)")
    ax2.set_ylim(0, 13)
    ax2.set_title("Same propellant, same dry mass, 1 t payload")
    ax2.legend(loc="upper left", fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "staging.png", dpi=120)

    # copy for the docs
    up = OUT.resolve().parents
    docs = up[2] / "docs" / "figures" if len(up) > 2 else OUT    # repo/docs/figures, when run from the repo
    if docs != OUT and docs.exists() and (docs.parent.parent / "start.py").exists():
        fig.savefig(docs / "s01_rocket_equation.png", dpi=120)
        fig2.savefig(docs / "s01_staging.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The rocket equation gives the speed in empty space. A real launch fights gravity and air
# while it climbs. Session 2 flies the rocket straight up and measures those losses.
