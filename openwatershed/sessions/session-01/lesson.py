"""Session 1 (Level 1): rain falls on a catchment, some soaks in, the rest runs off and gathers in the river.

Educational model only. Real flood forecasts and design come from official agencies and qualified hydrologists.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: from rain to river
# **A. Real-world problem.** A storm drops the same 60 mm of rain on a town's hills twice: once in
# 1 hour, once spread over 6 hours. In which case does the river rise higher? The answer is not
# obvious, and it decides how high a bridge or a flood wall must be.
#
# **Plan.** (1) split rain into soaking-in and run-off, (2) turn run-off depth into a flow in
# m3/s, (3) let the catchment gather the water into the river with a delay, (4) compare a short
# intense storm with a long gentle one.
#
# *Educational model.* Real flood forecasts come from official agencies, not from this lesson.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

AREA = 20.0   # catchment area in km2 (a made-up valley)
K = 2.0       # catchment delay in hours: the bigger K, the slower the river rises


# %% [markdown]
# ## Step 1: some rain soaks in
# The ground can swallow water at a rate `f` (mm per hour), like a sponge. Rain that falls faster
# than `f` cannot soak in, so the excess runs off over the surface:
#
#     run-off rate = rain intensity - f      (never below zero)
#
# Rain of 10 mm/h on ground that swallows 5 mm/h gives 5 mm/h of run-off. Rain of 4 mm/h
# gives none.

# %%
def runoff_rate(i, f):
    """Run-off rate in mm/h from rain intensity i (mm/h) and soak-in rate f (mm/h)."""
    return max(i - f, 0.0)


# %% [markdown]
# ## Step 2: run-off depth becomes a flow
# 1 mm of water over 1 km2 is 0.001 m * 1 000 000 m2 = 1000 m3. So 1 mm/h over 1 km2 is
# 1000 m3 per hour = 1000 / 3600 = 0.2778 m3/s. Hence
#
#     flow (m3/s) = run-off rate (mm/h) * area (km2) / 3.6

# %%
def to_flow(rate_mm_h, area_km2):
    """Flow in m3/s from a depth rate (mm/h) falling on an area (km2)."""
    return rate_mm_h * area_km2 / 3.6


# %% [markdown]
# ## Step 3: the catchment gathers the water
# Run-off does not reach the river at once: it must trickle down slopes and gullies. The simplest
# picture is a tank (a *linear reservoir*) with a leak. Water runs in at rate `q_in`; the tank
# drains at `storage / K`. Then the river flow is `storage / K`.
#
# For a storm that gives constant run-off flow `q` for `D` hours the river flow rises as
# `q (1 - exp(-t/K))`, reaches `q (1 - exp(-D/K))` at the end of the storm, then falls as
# `exp(-(t-D)/K)`. A storm shorter than K never lets the river reach `q`.

# %%
def storm_peak(P, D, f, area=AREA, k=K):
    """Peak river flow (m3/s) for P mm of rain falling evenly over D hours."""
    i = P / D
    q = to_flow(runoff_rate(i, f), area)
    return q * (1.0 - np.exp(-D / k))


def hydrograph(P, D, f, t, area=AREA, k=K):
    """River flow (m3/s) at times t (hours) after the storm starts, exact solution."""
    t = np.asarray(t, dtype=float)
    q = to_flow(runoff_rate(P / D, f), area)
    qpk = q * (1.0 - np.exp(-D / k))
    return np.where(t <= D, q * (1.0 - np.exp(-t / k)), qpk * np.exp(-(t - D) / k))


def simulate(P, D, f, t_end=24.0, dt=0.005, area=AREA, k=K):
    """Same flow by stepping the tank forward in small time steps (a check on the formulas)."""
    n = int(round(t_end / dt))
    q = to_flow(runoff_rate(P / D, f), area)
    s, out = 0.0, np.zeros(n + 1)
    for j in range(n):
        t = j * dt
        s += dt * ((q if t < D else 0.0) - s / k)   # storage in (m3/s * h) units
        out[j + 1] = s / k
    return np.arange(n + 1) * dt, out


def runoff_volume(P, D, f, area=AREA):
    """Run-off volume in m3."""
    return runoff_rate(P / D, f) * D * area * 1000.0


# %% [markdown]
# ## Step 4: same rain, different storm
# Both storms drop 60 mm. The soak-in rate is f = 5 mm/h, the catchment is 20 km2, K = 2 h.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    f = 5.0
    print("1 mm/h on 1 km2 =", round(to_flow(1.0, 1.0), 4), "m3/s")
    t = np.linspace(0, 16, 400)
    fig, ax = plt.subplots(figsize=(6.4, 4))
    for D, col in ((1.0, "tab:red"), (6.0, "tab:blue")):
        ax.plot(t, hydrograph(60.0, D, f, t), color=col,
                label=f"60 mm in {D:g} h: peak {storm_peak(60.0, D, f):.1f} m3/s")
        print(f"60 mm in {D:g} h -> peak {storm_peak(60.0, D, f):.1f} m3/s,",
              f"run-off {runoff_volume(60.0, D, f) / 1000:.0f} thousand m3")
    ax.set_xlabel("time since the storm began (h)")
    ax.set_ylabel("river flow (m3/s)")
    ax.set_title("Same 60 mm of rain: short and intense beats long and gentle")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "two_storms.png", dpi=120)

    Ds = np.linspace(0.5, 12, 60)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    for f2, col in ((0.0, "tab:green"), (5.0, "tab:orange"), (10.0, "tab:purple")):
        ax2.plot(Ds, [storm_peak(60.0, d, f2) for d in Ds], color=col, label=f"soak-in {f2:g} mm/h")
    ax2.set_xlabel("storm duration D (h), total rain fixed at 60 mm")
    ax2.set_ylabel("peak river flow (m3/s)")
    ax2.set_title("Longer storms of the same depth give smaller peaks")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "peak_vs_duration.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
