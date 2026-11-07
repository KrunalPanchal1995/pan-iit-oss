"""Session 3 (Level 3): simulate a reverse osmosis membrane and validate it.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulate a membrane module and validate it
# **A. Real-world problem.** Session 2 gave limits for a plant with an endless membrane and
# perfect machines. A real pressure vessel holds about 260 m2 of membrane, the pump wastes
# some energy, the energy recovery device (ERD) gives back most but not all of the brine's
# push, and a little salt slips through. Can we march along the membrane step by step,
# show that the simulation obeys the salt balance and the Session 2 limits, and pick the
# feed pressure for one vessel of a seawater plant?
#
# **Plan.** (1) water and salt flux laws, (2) march along the membrane area with RK4,
# (3) validate against a closed-form answer and the balances, (4) count the energy
# (pump, ERD), (5) choose a feed pressure that meets recovery and drinking-water limits.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R = 8.314
M_NACL = 58.44
KJ_PER_KWH = 3600.0
K_PI = 2 * 1000.0 / M_NACL * R * 298.15 / 1000.0   # kPa per (g/L) at 25 C, ideal van 't Hoff = 84.83

A_W = 1.0e-5     # water permeability, m3/(m2 h kPa)  (= 1 L/(m2 h bar), a typical seawater membrane)
B_S = 8.0e-5     # salt permeability, m3/(m2 h)       (= 0.08 L/(m2 h), illustrative)
AREA = 260.0     # membrane area of one pressure vessel (7 elements of about 37 m2), m2
Q_FEED = 12.0    # feed flow into one vessel, m3/h


def osmotic(c):
    """Osmotic pressure (kPa) of NaCl water with c g/L, 25 C, ideal law."""
    return K_PI * c


# %% [markdown]
# ## Step 1: the flux laws (solution-diffusion model)
# Through each square metre of membrane:
#
#     water:  Jw = A x (P - CP x pi(c))          (only if positive)
#     salt:   Js = B x CP x c
#
# P is the feed pressure (the fresh side is at about 0 kPa gauge), c the salt in the feed
# channel, and CP >= 1 the **concentration polarisation** factor: salt piles up at the
# membrane face, so the wall is saltier than the bulk. A and B are measured for each
# membrane. Jw is in m3 of water per m2 per hour.

# %%
def water_flux(p, c, a_w=A_W, cp=1.0):
    """Water flux (m3/(m2 h)); zero when the push is below the osmotic pressure at the wall."""
    return max(a_w * (p - cp * osmotic(c)), 0.0)


def salt_flux(c, b_s=B_S, cp=1.0):
    """Salt flux (kg/(m2 h)) = B x wall concentration (g/L = kg/m3)."""
    return b_s * cp * c


# %% [markdown]
# ## Step 2: march along the membrane
# Follow the feed channel from inlet to outlet. In a small piece of area da, water flow Q
# (m3/h) and salt flow S (kg/h) both drop:
#
#     dQ/da = -Jw          dS/da = -Js          c = S / Q
#
# We step through the area with the fourth-order Runge-Kutta method (RK4): four slope
# samples per step, averaged with weights 1, 2, 2, 1.

# %%
def simulate_module(p, c_feed=35.0, q_feed=Q_FEED, area=AREA, a_w=A_W, b_s=B_S, cp=1.0, n=400):
    """March along the membrane. Returns a dict with profiles and totals.

    p in kPa, c_feed in g/L, q_feed in m3/h, area in m2."""
    if p <= 0 or q_feed <= 0 or area <= 0 or c_feed < 0:
        raise ValueError("pressure, feed flow and area must be positive and salt not negative")
    if cp < 1.0:
        raise ValueError("concentration polarisation factor must be at least 1")

    def rhs(y):
        q, s = y
        c = s / q
        return np.array([-water_flux(p, c, a_w, cp), -salt_flux(c, b_s, cp)])

    h = area / n
    a = np.linspace(0.0, area, n + 1)
    y = np.zeros((n + 1, 2))
    y[0] = [q_feed, q_feed * c_feed]
    for k in range(n):
        k1 = rhs(y[k])
        k2 = rhs(y[k] + 0.5 * h * k1)
        k3 = rhs(y[k] + 0.5 * h * k2)
        k4 = rhs(y[k] + h * k3)
        y[k + 1] = y[k] + h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    q, s = y[:, 0], y[:, 1]
    q_perm = q_feed - q[-1]
    salt_perm = y[0, 1] - s[-1]
    return {"area": a, "q": q, "c": s / q, "flux": np.array([water_flux(p, ci, a_w, cp) for ci in s / q]),
            "q_perm": q_perm, "recovery": q_perm / q_feed, "c_brine": s[-1] / q[-1],
            "c_perm": salt_perm / q_perm if q_perm > 0 else 0.0, "salt_in": y[0, 1],
            "salt_out": s[-1] + salt_perm, "p": p, "q_feed": q_feed}


# %% [markdown]
# ## Step 3: a closed-form answer to validate against
# With no salt leak (B = 0) and CP = 1, the salt flow is fixed, c = cf Qf / Q, and the
# equation dQ/da = -A (P - k / Q) with k = pi_f Qf can be integrated by hand:
#
#     area = [ (Qf - Q)/P + (k / P^2) ln((P Qf - k) / (P Q - k)) ] / A
#
# Our RK4 march must reproduce this. Also: no area, however large, can push the brine above
# pi_b = P, so recovery can never exceed 1 - pi_f / P (the Session 2 limit).

# %%
def area_needed(p, recovery, c_feed=35.0, q_feed=Q_FEED, a_w=A_W):
    """Exact membrane area (m2) for a recovery with B = 0 and CP = 1."""
    k = osmotic(c_feed) * q_feed
    q = q_feed * (1.0 - recovery)
    if p * q <= k:
        raise ValueError("this recovery is not reachable at this pressure (brine would exceed P)")
    return ((q_feed - q) / p + k / p ** 2 * np.log((p * q_feed - k) / (p * q - k))) / a_w


def recovery_limit(p, c_feed=35.0):
    """Largest recovery any membrane area can give at pressure p: 1 - pi_f / P."""
    return max(0.0, 1.0 - osmotic(c_feed) / p)


# %% [markdown]
# ## Step 4: count the energy
# The high-pressure pump lifts all the feed to P with efficiency eta_pump. The brine leaves
# the vessel still at P; the ERD hands a share e of that pressure energy back to the feed.
# Per cubic metre of fresh water (1 kPa x 1 m3 = 1 kJ):
#
#     SEC = (P Qf / eta_pump - e P Qb) / Qp / 3600     kWh/m3
#
# With eta_pump = 1 and e = 1 this is just P / 3600.

# %%
def specific_energy(res, eta_pump=0.8, erd=0.95):
    """Specific energy consumption (kWh per m3 of fresh water) of one simulated vessel."""
    if not (0.0 < eta_pump <= 1.0 and 0.0 <= erd <= 1.0):
        raise ValueError("pump efficiency must be in (0, 1] and ERD efficiency in [0, 1]")
    p, qf, qp = res["p"], res["q_feed"], res["q_perm"]
    if qp <= 0:
        return float("inf")
    qb = qf - qp
    return (p * qf / eta_pump - erd * p * qb) / qp / KJ_PER_KWH


def least_work(c_feed, recovery):
    """Session 2 reversible least work (kWh/m3) for comparison."""
    return osmotic(c_feed) * np.log(1.0 / (1.0 - recovery)) / recovery / KJ_PER_KWH


# %% [markdown]
# ## Step 5: choose the feed pressure (mini-project)
# Sweep P in steps of 250 kPa and keep only the pressures that meet every limit; among
# those pick the one with the smallest SEC.

# %%
def choose_pressure(c_feed=35.0, r_min=0.45, c_perm_max=0.5, p_max=6900.0, eta_pump=0.8, erd=0.95,
                    cp=1.1, step=250.0):
    """Lowest-energy feed pressure (kPa) that meets recovery, permeate and pressure limits.

    Returns (pressure, result, sec) or None when no pressure works."""
    best = None
    for p in np.arange(3000.0, p_max + 1e-9, step):
        res = simulate_module(p, c_feed, cp=cp)
        if res["recovery"] >= r_min and res["c_perm"] <= c_perm_max:
            sec = specific_energy(res, eta_pump, erd)
            if best is None or sec < best[2]:
                best = (float(p), res, sec)
    return best


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # Figure 1: profiles along the membrane
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    for p, col in [(5500.0, "#8d99ae"), (6000.0, "#2a9d8f"), (6500.0, "#d9534f")]:
        res = simulate_module(p, cp=1.1)
        axes[0].plot(res["area"], res["flux"] * 1000, color=col, lw=2, label=f"P = {p / 1000:.1f} MPa")
        axes[1].plot(res["area"], res["c"], color=col, lw=2)
        print(f"P = {p:.0f} kPa: recovery {res['recovery']:.3f}, brine {res['c_brine']:.1f} g/L, "
              f"permeate {res['c_perm'] * 1000:.0f} mg/L, SEC {specific_energy(res):.2f} kWh/m3")
    axes[0].set_xlabel("membrane area from the inlet (m2)")
    axes[0].set_ylabel("water flux (L per m2 per hour)")
    axes[0].set_title("Flux falls as the feed gets saltier")
    axes[0].legend(fontsize=8)
    axes[1].set_xlabel("membrane area from the inlet (m2)")
    axes[1].set_ylabel("salt in the feed channel (g/L)")
    axes[1].set_title("The feed turns into brine")
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "module_profiles.png", dpi=120)

    # Figure 2: validation (RK4 against the closed form, and the recovery limit)
    fig2, axes2 = plt.subplots(1, 2, figsize=(10, 4.2))
    p = 6000.0
    res = simulate_module(p, b_s=0.0, area=2000.0, n=2000)
    rr = np.linspace(0.01, 0.97 * recovery_limit(p), 60)
    axes2[0].plot([area_needed(p, r) for r in rr], rr * 100, "k-", lw=3, alpha=0.4, label="closed form")
    axes2[0].plot(res["area"], (Q_FEED - res["q"]) / Q_FEED * 100, color="#2a9d8f", ls="--", lw=2, label="RK4 march")
    axes2[0].axhline(recovery_limit(p) * 100, color="#d9534f", ls=":", label="limit 1 - pi_f / P")
    axes2[0].set_xlabel("membrane area (m2)")
    axes2[0].set_ylabel("recovery (%)")
    axes2[0].set_title("P = 6 MPa, no salt leak")
    axes2[0].legend(fontsize=8, loc="lower right")
    areas = [50, 100, 200, 400, 800, 1600, 3200, 6400]
    secs = [specific_energy(simulate_module(p, b_s=0.0, area=a), 1.0, 1.0) for a in areas]
    rec = [simulate_module(p, b_s=0.0, area=a)["recovery"] for a in areas]
    axes2[1].semilogx(areas, secs, "o-", color="#2a9d8f", label="simulated, ideal pump and ERD")
    axes2[1].semilogx(areas, [least_work(35.0, r) for r in rec], "s-", color="k", label="least work at that recovery")
    axes2[1].set_xlabel("membrane area (m2)")
    axes2[1].set_ylabel("energy (kWh/m3)")
    axes2[1].set_title("Simulation never beats the least work")
    axes2[1].legend(fontsize=8)
    for ax in axes2:
        ax.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "validation.png", dpi=120)

    # Figure 3: the energy ladder, from physics to a real vessel (also the promo Target figure)
    best = choose_pressure()
    p_b, res_b, sec_b = best
    r_b = res_b["recovery"]
    rungs = [("least work,\ntiny recovery", least_work(35.0, 1e-9)),
             (f"least work,\nr = {r_b:.2f}", least_work(35.0, r_b)),
             ("1 stage at brine\npressure, ideal", osmotic(res_b["c_brine"]) / KJ_PER_KWH),
             ("real membrane\narea, ideal machines", specific_energy(res_b, 1.0, 1.0)),
             ("+ ERD 95 %", specific_energy(res_b, 1.0, 0.95)),
             ("+ pump 80 %\n(simulated vessel)", sec_b)]
    fig3, ax3 = plt.subplots(figsize=(8.6, 4.6))
    cols = ["#264653", "#2a9d8f", "#8ab17d", "#e9c46a", "#f4a261", "#d9534f"]
    for k, (name, e) in enumerate(rungs):
        ax3.bar(k, e, color=cols[k])
        ax3.text(k, e + 0.05, f"{e:.2f}", ha="center", fontsize=9)
        print(f"{name.replace(chr(10), ' '):38s}: {e:.3f} kWh/m3")
    ax3.axhspan(3.0, 4.0, color="#8d99ae", alpha=0.2)
    ax3.text(-0.4, 3.85, "whole real plants incl. intake and pretreatment: roughly 3 to 4 kWh/m3",
             fontsize=8, va="top")
    ax3.set_xticks(range(len(rungs)))
    ax3.set_xticklabels([n for n, _ in rungs], fontsize=8)
    ax3.set_ylabel("energy per m3 of fresh water (kWh/m3)")
    ax3.set_ylim(0, 4.2)
    ax3.set_title(f"Energy ladder: seawater 35 g/L, one vessel at {p_b / 1000:.2f} MPa (simplified model)")
    fig3.tight_layout()
    fig3.savefig(OUT / "energy_ladder.png", dpi=120)
    print(f"chosen P = {p_b:.0f} kPa, recovery {r_b:.3f}, permeate {res_b['c_perm'] * 1000:.0f} mg/L, "
          f"SEC {sec_b:.2f} kWh/m3; 100 MLD plant needs {sec_b * 100000 / 24 / 1000:.1f} MW")

# %% [markdown]
# ## Where this stops
# Our osmotic pressure is the ideal law (about 10 percent high for seawater), the pressure
# along the vessel does not drop, CP is a fixed number and the intake, pretreatment and
# second pass are left out. The roadmap shows how to add each one on the way to the Target.
