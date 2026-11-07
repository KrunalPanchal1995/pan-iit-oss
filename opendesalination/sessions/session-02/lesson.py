"""Session 2 (Level 2): recovery, brine and the least work of separation.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: recovery and the least work
# **A. Real-world problem.** A seawater plant does not take a tiny sip of fresh water; it
# takes about half of what it pumps in. The salt stays behind, so the leftover water (the
# **brine**) gets saltier and pushes back harder. How does the minimum energy grow with the
# share of fresh water we take (the **recovery**), and how close can a real one-stage plant
# with a pump get to that minimum?
#
# **Plan.** (1) a salt balance gives the brine concentration, (2) a piston slowly squeezing
# a batch of seawater gives the reversible (least) work, (3) a one-stage plant must push
# everything at the final brine pressure, (4) more stages and an energy recovery device
# close the gap.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R = 8.314
M_NACL = 58.44
KJ_PER_KWH = 3600.0


def osmotic_pressure(salt_g_per_l, t_celsius=25.0, i=2):
    """Osmotic pressure in kPa (ideal van 't Hoff law, as in Session 1)."""
    if salt_g_per_l < 0:
        raise ValueError("salt concentration cannot be negative")
    return i * salt_g_per_l / M_NACL * 1000.0 * R * (t_celsius + 273.15) / 1000.0


def _check_recovery(r):
    if not 0.0 < r < 1.0:
        raise ValueError("recovery must be between 0 and 1 (not 0 percent or 100 percent)")


# %% [markdown]
# ## Step 1: the salt balance
# Feed a volume V of seawater with salt concentration cf. Take out a fraction r of it as
# fresh water (r is the **recovery**). A perfect membrane keeps all the salt, so all of it
# ends up in the brine volume (1 - r) V:
#
#     cb = cf / (1 - r)
#
# At r = 0.5 the brine is twice as salty as the sea, so its osmotic pressure is doubled too.

# %%
def brine_concentration(c_feed, r):
    """Salt concentration of the brine (same unit as c_feed) at recovery r."""
    _check_recovery(r)
    return c_feed / (1.0 - r)


# %% [markdown]
# ## Step 2: the reversible (least) work: a slow piston
# Put the seawater in a cylinder whose base is a membrane. Push the piston down very
# slowly, always only just above the osmotic pressure of the water left inside. When a
# fraction x of the water has gone out, the inside is cf / (1 - x) salty, so the pressure is
#
#     pi(x) = pi_f / (1 - x)
#
# The work is the area under this curve (pressure x volume, like a gas in a pump). Adding up the
# thin strips (an integral) gives, per cubic metre of fresh water,
#
#     W_rev = pi_f x ln(1 / (1 - r)) / r
#
# As r goes to 0 this tends to pi_f, the Session 1 answer. No process can use less.

# %%
def w_reversible(c_feed, r, t_celsius=25.0):
    """Least work (kWh per m3 of fresh water) to recover a fraction r of the feed."""
    _check_recovery(r)
    pf = osmotic_pressure(c_feed, t_celsius)
    return pf * np.log(1.0 / (1.0 - r)) / r / KJ_PER_KWH


def batch_piston_work(c_feed, r, t_celsius=25.0, n=2000):
    """The same least work by adding up n thin strips under pi(x) (trapezoid rule)."""
    _check_recovery(r)
    pf = osmotic_pressure(c_feed, t_celsius)
    x = np.linspace(0.0, r, n + 1)
    p = pf / (1.0 - x)
    area = float(np.sum(0.5 * (p[1:] + p[:-1]) * np.diff(x)))   # kJ per m3 of feed
    return area / r / KJ_PER_KWH


# %% [markdown]
# ## Step 3: a one-stage plant pushes everything at the brine pressure
# A real plant is a steady flow: seawater is pumped to a pressure P and flows past the
# membrane. Water leaves only while P is above the local osmotic pressure, and at the end
# of the membrane the water is brine. So P must be at least pi_b = pi_f / (1 - r).
#
# * **No energy recovery.** The pump pushes all the feed (1 / r m3 per m3 of fresh water)
#   to P, so W = pi_f / (r (1 - r)). This is smallest at r = 0.5, where it is 4 pi_f.
# * **With an energy recovery device (ERD)** of efficiency e, the high-pressure brine
#   gives back e of its pressure energy: W = pi_f (1 - e (1 - r)) / (r (1 - r)).
#   With e = 1 only the fresh water's own push remains: W = pi_f / (1 - r).

# %%
def w_single_stage(c_feed, r, erd=0.0, t_celsius=25.0):
    """Least work (kWh/m3) of a one-stage plant at exactly the brine osmotic pressure.

    erd is the energy recovery device efficiency (0 = none, 1 = perfect)."""
    _check_recovery(r)
    if not 0.0 <= erd <= 1.0:
        raise ValueError("ERD efficiency must be between 0 and 1")
    pf = osmotic_pressure(c_feed, t_celsius)
    return pf * (1.0 - erd * (1.0 - r)) / (r * (1.0 - r)) / KJ_PER_KWH


def recovery_for_pressure(c_feed, p_max, t_celsius=25.0):
    """Highest recovery a pump pressure p_max (kPa) can reach: pi_b = p_max."""
    pf = osmotic_pressure(c_feed, t_celsius)
    if p_max <= pf:
        return 0.0
    return 1.0 - pf / p_max


# %% [markdown]
# ## Step 4: more stages get closer to the minimum
# Split the plant into n stages. Each stage removes r / n of the original feed and needs
# only the pressure at its own outlet. With perfect energy recovery the work is a
# staircase under the curve pi(x):
#
#     W_n = (1 / r) x sum over k of pi_f / (1 - k r / n) x (r / n)
#
# n = 1 is the one-stage plant with a perfect ERD; as n grows the staircase fits the curve
# and W_n falls towards W_rev. With a real ERD of efficiency e the brine still leaves at the
# last stage pressure, so (1 - e) of its push energy is lost on top:
#
#     extra = (1 - e) x pi_f / (1 - r) x (1 - r) / r  =  (1 - e) x pi_f / r

# %%
def w_staged(c_feed, r, n, erd=1.0, t_celsius=25.0):
    """Work (kWh/m3) of n ideal stages; erd is the energy recovery efficiency (1 = perfect)."""
    _check_recovery(r)
    if int(n) != n or n < 1:
        raise ValueError("number of stages must be a whole number of at least 1")
    if not 0.0 <= erd <= 1.0:
        raise ValueError("ERD efficiency must be between 0 and 1")
    pf = osmotic_pressure(c_feed, t_celsius)
    k = np.arange(1, int(n) + 1)
    stairs = np.sum(pf / (1.0 - k * r / n) * (r / n))           # kJ per m3 of feed
    brine_loss = (1.0 - erd) * pf / (1.0 - r) * (1.0 - r)         # unrecovered brine push
    return float((stairs + brine_loss) / r / KJ_PER_KWH)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    cf, r0 = 35.0, 0.5
    pf = osmotic_pressure(cf)

    # Figure 1: the pressure staircase (like a P-V diagram)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    x = np.linspace(0, r0, 200)
    for ax, n in zip(axes, (1, 3)):
        ax.fill_between(x, 0, pf / (1 - x) / 1000, color="#2a9d8f", alpha=0.35, label="least work (area)")
        ax.plot(x, pf / (1 - x) / 1000, "k-", lw=2, label="osmotic pressure inside")
        edges = np.linspace(0, r0, n + 1)
        for a, b in zip(edges[:-1], edges[1:]):
            pk = pf / (1 - b) / 1000
            ax.fill_between([a, b], 0, pk, color="#e9c46a", alpha=0.35, step="pre")
            ax.plot([a, a, b, b], [0, pk, pk, 0], color="#b07d00", lw=1.5)
        ax.set_title(f"{n} stage{'s' if n > 1 else ''}: {w_staged(cf, r0, n):.3f} kWh/m3 (least {w_reversible(cf, r0):.3f})")
        ax.set_xlabel("fraction of the feed taken as fresh water")
        ax.set_xlim(0, 0.52)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("pressure (MPa)")
    axes[0].legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "pressure_staircase.png", dpi=120)

    # Figure 2: energy against recovery
    rr = np.linspace(0.05, 0.85, 161)
    fig2, ax2 = plt.subplots(figsize=(6.8, 4.4))
    ax2.plot(rr * 100, [w_single_stage(cf, r) for r in rr], color="#d9534f", lw=2, label="1 stage, no energy recovery")
    ax2.plot(rr * 100, [w_single_stage(cf, r, 0.9) for r in rr], color="#e9c46a", lw=2, label="1 stage, ERD 90 %")
    ax2.plot(rr * 100, [w_staged(cf, r, 1) for r in rr], color="#b07d00", lw=2, ls="--", label="1 stage, perfect ERD")
    ax2.plot(rr * 100, [w_staged(cf, r, 3) for r in rr], color="#8d99ae", lw=2, ls="-.", label="3 stages, perfect ERD")
    ax2.plot(rr * 100, [w_reversible(cf, r) for r in rr], "k-", lw=2.5, label="least work (reversible)")
    ax2.plot(50, w_single_stage(cf, 0.5), "o", color="#d9534f")
    ax2.set_xlabel("recovery r (%)")
    ax2.set_ylabel("energy per m3 of fresh water (kWh/m3)")
    ax2.set_ylim(0, 6)
    ax2.set_title("Seawater 35 g/L, 25 C: energy against recovery")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8, loc="upper center")
    fig2.tight_layout()
    fig2.savefig(OUT / "energy_vs_recovery.png", dpi=120)

    print(f"feed osmotic pressure {pf:.0f} kPa; brine at r = 0.5: {brine_concentration(cf, 0.5):.0f} g/L")
    for name, w in [("least work", w_reversible(cf, r0)), ("strips (check)", batch_piston_work(cf, r0)),
                    ("1 stage, no ERD", w_single_stage(cf, r0)), ("1 stage, ERD 0.9", w_single_stage(cf, r0, 0.9)),
                    ("1 stage, perfect ERD", w_single_stage(cf, r0, 1.0)), ("3 stages", w_staged(cf, r0, 3))]:
        print(f"{name:22s}: {w:.3f} kWh/m3")

# %% [markdown]
# ## Where this stops
# We assumed the membrane is huge, so water flows even when the push is only just above the
# osmotic pressure. A real membrane has a finite area and needs extra push to make water
# flow at a useful rate; the pump and the ERD also lose energy. Session 3 simulates a real
# membrane module and checks the simulation against these limits.
