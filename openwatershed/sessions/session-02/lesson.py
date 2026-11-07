"""Session 2 (Level 2): the rational method, the SCS curve number, and a design problem.

Educational model only. Real flood design uses official rainfall data, local rules and a qualified hydrologist.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: two standard recipes for a flood
# **A. Real-world problem.** A culvert (a pipe under a road) must carry the flood of a small
# stream. Engineers need two numbers: how much of a storm becomes run-off (a *depth* in mm) and
# how big the flow peak is (m3/s). This session builds both with two classic formulas and
# applies them to a made-up catchment, Mango Creek.
#
# **Plan.** (1) the rational method and its unit factor 3.6, (2) the SCS curve number run-off,
# (3) time of concentration Tc, (4) a design problem. Pipe hydraulics is in `openpipeflow` and
# retaining structures in `openretainingwall`; here we stop at the flow in the stream.
#
# *Educational model.* Not a design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the rational method
# `Q = C * i * A / 3.6` with Q the peak flow (m3/s), C the run-off coefficient (0 to 1, the share
# of rain that runs off), i the rain intensity (mm/h) and A the area (km2).
# Why 3.6? 1 mm/h over 1 km2 is 0.001 m * 1 000 000 m2 = 1000 m3 per hour = 1000/3600 = 0.2778
# m3/s, and 1/0.2778 = 3.6.

# %%
def rational_peak(C, i, A):
    """Peak flow in m3/s: C (0..1), i in mm/h, A in km2."""
    return C * i * A / 3.6


# %% [markdown]
# ## Step 2: the SCS curve number method
# Soil and land cover are summarised by a *curve number* CN between 0 and 100 (higher = more
# run-off: roofs and roads near 98, forest on sandy soil near 40). From CN we get
#
#     S  = 25400 / CN - 254        (mm, the most water the ground can still hold)
#     Ia = 0.2 * S                 (mm, rain lost at the start before any run-off)
#     Q  = (P - Ia)^2 / (P - Ia + S)   for P > Ia, otherwise 0
#
# P is the storm rain depth (mm) and Q the run-off depth (mm). The 0.2 is the standard
# approximation; it is a rule of thumb, not a law.

# %%
def scs_S(CN):
    """Maximum retention S in mm."""
    return 25400.0 / np.asarray(CN, dtype=float) - 254.0


def scs_runoff(P, CN):
    """Run-off depth Q (mm) from storm depth P (mm) and curve number CN."""
    P = np.asarray(P, dtype=float)
    S = scs_S(CN)
    Ia = 0.2 * S
    x = P - Ia
    safe = np.where(x > 0, x, 0.0)
    return np.where(x > 0, safe ** 2 / (safe + S), 0.0)


# %% [markdown]
# ## Step 3: time of concentration
# Tc is the time water needs to travel from the farthest point of the catchment to the outlet.
# The Kirpich formula (metric form, approximate, made for small rural catchments):
#
#     Tc (minutes) = 0.0195 * L^0.77 * S^(-0.385)
#
# L = longest flow path in metres, S = average slope (drop divided by length, no unit).
# Why does the design storm last Tc? A shorter storm is more intense but the far corner has not
# delivered its water yet; a longer storm is gentler (lower i). The peak is best at D = Tc.
# We model the contributing area as A * min(1, D / Tc), a simple approximation.

# %%
def kirpich_tc_min(L_m, slope):
    """Approximate time of concentration in minutes."""
    return 0.0195 * L_m ** 0.77 * slope ** (-0.385)


def idf_made_up(t_min):
    """A MADE-UP rain intensity (mm/h) for a storm of t_min minutes. Real curves come from the weather service."""
    return 2000.0 / (np.asarray(t_min, dtype=float) + 15.0)


def peak_for_duration(C, D_min, A, Tc_min):
    """Rational-style peak (m3/s) for a storm of D_min minutes: only the part of A within reach contributes."""
    frac = np.minimum(1.0, np.asarray(D_min, dtype=float) / Tc_min)
    return C * idf_made_up(D_min) * A * frac / 3.6


# %% [markdown]
# ## Step 4: Mango Creek (made up)
# A = 4.5 km2, longest path 3200 m, drop 64 m, rational C = 0.45 (mixed farmland and houses),
# CN = 80, a 100 mm storm.

# %%
MANGO = dict(A=4.5, L=3200.0, drop=64.0, C=0.45, CN=80.0, P=100.0)

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m = MANGO
    tc = kirpich_tc_min(m["L"], m["drop"] / m["L"])
    i = float(idf_made_up(tc))
    print(f"Tc = {tc:.1f} min, i(Tc) = {i:.1f} mm/h, rational peak = {rational_peak(m['C'], i, m['A']):.1f} m3/s")
    q = float(scs_runoff(m["P"], m["CN"]))
    print(f"S = {float(scs_S(m['CN'])):.1f} mm, Ia = {0.2 * float(scs_S(m['CN'])):.1f} mm, runoff = {q:.2f} mm,",
          f"volume = {q / 1000 * m['A'] * 1e6:,.0f} m3")

    P = np.linspace(0, 200, 400)
    fig, ax = plt.subplots(figsize=(6.4, 4))
    for cn, col in ((60, "tab:green"), (75, "tab:orange"), (90, "tab:red")):
        ax.plot(P, scs_runoff(P, cn), color=col, label=f"CN {cn} (Ia = {0.2 * float(scs_S(cn)):.1f} mm)")
    ax.plot(P, P, "k:", lw=1, label="all rain runs off (Q = P)")
    ax.set_xlabel("storm rain depth P (mm)")
    ax.set_ylabel("run-off depth Q (mm)")
    ax.set_title("SCS curve number: no run-off until Ia, then Q approaches P - Ia - S")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "scs_curves.png", dpi=120)

    D = np.linspace(5, 150, 300)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    ax2.plot(D, peak_for_duration(m["C"], D, m["A"], tc), color="tab:blue")
    ax2.axvline(tc, color="gray", ls="--")
    ax2.annotate(f"Tc = {tc:.0f} min", (tc, 0.5), xytext=(tc + 6, 3))
    ax2.set_xlabel("storm duration D (min)")
    ax2.set_ylabel("peak flow (m3/s)")
    ax2.set_title("Mango Creek: the worst storm lasts as long as Tc")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "peak_vs_duration.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
