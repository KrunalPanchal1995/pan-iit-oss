"""Session 2 (Level 2): resistance of a vessel, cardiac output and mean arterial pressure.

Run:  python start.py 2
General education only: this is not medical advice and the model is not a diagnostic tool.
"""
# %% [markdown]
# # Session 2: why a small change in a vessel's width is a big change in pressure
# **A. Real-world problem.** The body can change the width of its small vessels in seconds.
# A change of only a few percent in radius changes how hard the heart must push. Why is the
# effect so large? And how do heart rate, the volume pumped per beat and the vessel width
# combine into one blood-pressure number?
#
# *This is general education. It is not medical advice and the model is not a diagnostic
# tool. All values are typical textbook figures, not a norm for any person.*
#
# **Plan.** (1) resistance of one pipe (Poiseuille), (2) cardiac output = heart rate x stroke
# volume, (3) mean arterial pressure = output x total resistance, (4) a design problem.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

PA_PER_MMHG = 133.322       # 1 mmHg in pascals
MU_BLOOD = 3.5e-3           # Pa s: a typical textbook viscosity of blood (treated as constant)
TPR_TYPICAL = 18.6          # mmHg per (L/min): typical 93 mmHg / 5 L/min


# %% [markdown]
# ## Step 1: resistance of one pipe
# For slow, smooth (laminar) flow of a thick fluid in a straight round tube of length `L` and
# radius `r`, Poiseuille's law gives the resistance
#
#     R = 8 mu L / (pi r^4)          (SI units: Pa s per m^3)
#
# The radius is raised to the *fourth* power: half the radius means 2^4 = 16 times the
# resistance. Doctors read pressures in mmHg and flows in mL/s, so we convert:
# 1 mmHg = 133.322 Pa and 1 mL/s = 1e-6 m^3/s.

# %%
def poiseuille_R(mu, length, radius):
    """Resistance in Pa s / m^3 of a straight round tube (mu in Pa s, length and radius in m)."""
    if radius <= 0 or length <= 0 or mu <= 0:
        raise ValueError("mu, length and radius must be positive")
    return 8.0 * mu * length / (np.pi * radius ** 4)


def to_mmHg_per_mLs(R_si):
    """Convert Pa s / m^3 into mmHg per (mL/s)."""
    return R_si * 1e-6 / PA_PER_MMHG


def resistance_factor(radius_ratio):
    """How many times the resistance grows when the radius becomes radius_ratio times as big."""
    return radius_ratio ** -4


def radius_ratio_for(resistance_ratio):
    """Radius ratio that multiplies the resistance by resistance_ratio (inverse of the above)."""
    return resistance_ratio ** -0.25


# %% [markdown]
# ## Step 2: cardiac output
# Each beat pushes out a *stroke volume* `SV` (mL). With `HR` beats per minute the heart
# delivers the *cardiac output* `CO = HR x SV`, in mL per minute; divide by 1000 for L/min.
# Typical textbook values: 70 beats per minute and 70 mL give 4.9, about 5 L/min.

# %%
def cardiac_output(hr, sv_mL):
    """Cardiac output in L/min from heart rate (beats/min) and stroke volume (mL)."""
    return hr * sv_mL / 1000.0


# %% [markdown]
# ## Step 3: mean arterial pressure
# The flow through the whole body obeys `Q = dP / R`. Taking the pressure of the returning
# blood as about 0, the average pressure in the arteries is
#
#     MAP = CO x TPR
#
# where TPR is the total peripheral resistance. Typical textbook values: MAP about 93 mmHg and
# CO about 5 L/min give TPR = 18.6 mmHg per (L/min). A common rule of thumb for MAP from a
# reading "systolic/diastolic" is diastolic + (systolic - diastolic)/3; for 120/80 it is 93.3.

# %%
def map_from_co(co, tpr):
    return co * tpr


def tpr_from(map_mmHg, co):
    if co <= 0:
        raise ValueError("cardiac output must be positive")
    return map_mmHg / co


def map_from_bp(systolic, diastolic):
    """Rule-of-thumb mean arterial pressure from a systolic/diastolic reading (mmHg)."""
    return diastolic + (systolic - diastolic) / 3.0


def map_model(hr, sv_mL, radius_ratio=1.0, tpr0=TPR_TYPICAL):
    """MAP (mmHg) when all the small vessels have radius_ratio times their normal radius."""
    return map_from_co(cardiac_output(hr, sv_mL), tpr0 * resistance_factor(radius_ratio))


# %% [markdown]
# ## Step 4: see it
# Left: MAP against vessel radius at constant output. Right: the resistance factor 1/r^4.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    R1 = poiseuille_R(MU_BLOOD, 0.10, 1.0e-3)
    R2 = poiseuille_R(MU_BLOOD, 0.10, 0.5e-3)
    print("R (r = 1.0 mm):", round(to_mmHg_per_mLs(R1), 3), "mmHg per mL/s")
    print("R (r = 0.5 mm):", round(to_mmHg_per_mLs(R2), 2), "mmHg per mL/s; ratio", round(R2 / R1, 3))
    print("CO:", cardiac_output(70, 70), "L/min; TPR from 93 and 5:", tpr_from(93, 5))
    print("MAP +20% resistance at constant CO:", round(map_from_co(5.0, TPR_TYPICAL * 1.2), 1), "mmHg")
    print("radius change that gives +20% resistance:", round(radius_ratio_for(1.2), 4))
    r = np.linspace(0.8, 1.2, 81)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(r, [map_from_co(5.0, TPR_TYPICAL * resistance_factor(x)) for x in r])
    ax.axhline(93, color="gray", ls=":")
    ax.set_xlabel("vessel radius / normal radius")
    ax.set_ylabel("mean arterial pressure at 5 L/min (mmHg)")
    ax.set_title("A few percent in radius moves the pressure a lot")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "map_vs_radius.png", dpi=120)

    rr = np.linspace(0.3, 1.5, 100)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.semilogy(rr, resistance_factor(rr))
    ax2.axvline(0.5, color="gray", ls=":")
    ax2.set_xlabel("radius / normal radius")
    ax2.set_ylabel("resistance / normal resistance (log scale)")
    ax2.set_title("R grows as 1 / r^4: half the radius is 16 times the resistance")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "resistance_vs_radius.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
