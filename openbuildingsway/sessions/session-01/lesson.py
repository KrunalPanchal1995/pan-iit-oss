"""Session 1 (Level 1): a tall building sways like a pendulum, and the ground can match its rhythm.

Educational model only. Never use it for real seismic design.
Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a building is a mass on a spring
# **A. Real-world problem.** After an earthquake, some buildings are badly shaken and the
# building next door is fine. Tall flexible buildings sway slowly, short stiff ones sway fast,
# and the ground has its own favourite rhythm. When the two rhythms match, the sway grows. Today
# you build the smallest model that shows this: one lump of mass on one spring.
#
# **Plan.** (1) the sway period from mass and stiffness, (2) the sway as a wave in time,
# (3) a rule of thumb for real buildings, (4) how much the building amplifies slow, matched
# and fast shaking.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the period of the sway
# Picture the whole building as a mass m (kg) on a spring of stiffness k (newtons per metre of
# sideways push). Heavier means slower; stiffer means faster. The time for one full back-and-forth
# sway is the *period* T:
#
#     w = sqrt(k / m)        (angular frequency, radians per second)
#     T = 2 pi / w           (period, seconds)

# %%
def sway_frequency(k, m):
    """Angular frequency w = sqrt(k / m) in rad/s (k in N/m, m in kg)."""
    return float(np.sqrt(k / m))


def sway_period(k, m):
    """Period T = 2 pi / w in seconds."""
    return float(2 * np.pi / sway_frequency(k, m))


# %% [markdown]
# ## Step 2: the sway in time
# Push the building and let go. It swings back and forth like a pendulum, and slowly dies away.
# Here we only draw the clean wave: x(t) = x0 cos(w t).

# %%
def free_sway(t, x0, k, m):
    """Sideways displacement of the roof in metres at time t (s), starting at rest from x0."""
    return x0 * np.cos(sway_frequency(k, m) * np.asarray(t, float))


# %% [markdown]
# ## Step 3: a rule of thumb
# Engineers often guess the period of a typical frame building (columns and beams) as
# **T about 0.1 s per storey**. It is only a rough empirical guide: shear walls, soft ground
# and tall slender towers can be very different.

# %%
def rule_of_thumb_period(storeys):
    """T = 0.1 N seconds (rough rule for typical frame buildings)."""
    return 0.1 * storeys


# %% [markdown]
# ## Step 4: resonance, first look
# Shake the ground back and forth with period T_g. If the shaking is much slower than the
# building's own period, the building just follows the ground (gain about 1). If T_g equals the
# building's period, each push adds to the last, and a typical damped building sways about ten
# times more. If the shaking is much faster, the building hardly moves. The *gain* is the sway
# divided by the sway for a very slow push. Session 2 derives the formula; here we just use it.
# With r = T / T_g (building period over ground period) and damping ratio zeta:
#
#     gain = 1 / sqrt((1 - r^2)^2 + (2 zeta r)^2)

# %%
def gain(t_building, t_ground, zeta=0.05):
    """Dynamic gain (no unit) of a damped building shaken harmonically with period t_ground."""
    r = np.asarray(t_building, float) / np.asarray(t_ground, float)
    return 1.0 / np.sqrt((1 - r ** 2) ** 2 + (2 * zeta * r) ** 2)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m, k = 2.0e5, 2.0e7
    print(f"m = {m:.0f} kg, k = {k:.0f} N/m -> w = {sway_frequency(k, m):.3f} rad/s, T = {sway_period(k, m):.4f} s")
    cases = [("reference", k, m), ("heavier (2 m)", k, 2 * m), ("stiffer (4 k)", 4 * k, m)]
    t = np.linspace(0, 4, 800)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    for name, kk, mm in cases:
        T = sway_period(kk, mm)
        ax.plot(t, 100 * free_sway(t, 0.05, kk, mm), label=f"{name}: T = {T:.3f} s")
        print(f"{name}: T = {T:.4f} s")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("roof sway (cm)")
    ax.set_title("Heavy sways slowly, stiff sways fast")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "sway_periods.png", dpi=120)

    tg = np.linspace(0.2, 3.0, 400)
    fig2, ax2 = plt.subplots(figsize=(7, 3.6))
    for tb in (0.5, 1.0):
        ax2.plot(tg, gain(tb, tg), label=f"building period {tb} s")
    ax2.set_yscale("log")
    ax2.set_xlabel("ground shaking period (s)")
    ax2.set_ylabel("gain: sway / slow-push sway (no unit)")
    ax2.set_title("Resonance: the gain peaks when the periods match")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "gain_vs_ground_period.png", dpi=120)
    for n in (3, 10, 20):
        print(f"{n} storeys: rule of thumb T = {rule_of_thumb_period(n):.1f} s")
    print(f"gain when periods match (5% damping): {gain(1.0, 1.0):.2f}")

# %% [markdown]
# ## Where this stops
# A real building is not one lump: it bends in several patterns at once (Session 3), and the
# gain above is for steady, repeated shaking, not for one real earthquake.
