"""Session 3 (Level 3): check a gravity retaining wall against sliding and overturning.

Run:  python start.py 3
Educational only: never use this to size or check a real wall.
"""
# %% [markdown]
# # Session 3: sliding, overturning and the middle third
# **A. Real-world problem.** A small wall holds up a garden bed. It must not slide, must not
# tip over about its toe, and its base must not lift off the ground at the heel.
#
# **Plan.** (1) earth pressure with backfill slope, surcharge and water, (2) the two safety
# factors and the base pressure, (3) validate against closed forms and moment equilibrium,
# (4) sweep width, friction and slope, (5) see how water in the backfill destroys the margin.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

GAMMA_W = 9.81     # unit weight of water, kN/m^3


# %% [markdown]
# ## Step 1: earth pressure coefficients
# Rankine (smooth vertical wall, backfill rising at angle beta):
# Ka = cos(b) * (cos(b) - sqrt(cos(b)^2 - cos(phi)^2)) / (cos(b) + sqrt(cos(b)^2 - cos(phi)^2)).
# For beta = 0 it becomes (1 - sin phi) / (1 + sin phi). Coulomb allows a rough, leaning wall
# (angle alpha from vertical, wall friction delta) and also reduces to Rankine when
# alpha = beta = delta = 0.

# %%
def ka_rankine(phi_deg, beta_deg=0.0):
    """Rankine active coefficient for a vertical wall and a backfill sloping up at beta."""
    phi, beta = np.radians(phi_deg), np.radians(beta_deg)
    if beta >= phi:
        raise ValueError("backfill slope must be smaller than phi")
    root = np.sqrt(np.cos(beta) ** 2 - np.cos(phi) ** 2)
    return float(np.cos(beta) * (np.cos(beta) - root) / (np.cos(beta) + root))


def ka_coulomb(phi_deg, delta_deg=0.0, alpha_deg=0.0, beta_deg=0.0):
    """Coulomb active coefficient. alpha: wall back leaning from vertical, delta: wall friction."""
    phi, delta, alpha, beta = (np.radians(v) for v in (phi_deg, delta_deg, alpha_deg, beta_deg))
    inner = np.sin(phi + delta) * np.sin(phi - beta) / (np.cos(alpha + delta) * np.cos(alpha - beta))
    return float(np.cos(phi - alpha) ** 2
                 / (np.cos(alpha) ** 2 * np.cos(alpha + delta) * (1.0 + np.sqrt(inner)) ** 2))


# %% [markdown]
# ## Step 2: all the forces on the wall, per metre run
# A rectangular gravity wall of width B and height H, concrete unit weight gc. Soil force
# on the back is Rankine with backfill slope beta (force parallel to the slope, so it has a
# horizontal part Ph = Pa cos(beta) and a vertical part Pv = Pa sin(beta), acting on the back
# of the wall at the heel). Surcharge q (kPa) adds Ka q H. Water table at height hw above
# the base adds hydrostatic push and an uplift triangle under the base (pressure gamma_w hw at
# the heel, zero at the toe). Passive resistance in front of the toe is neglected.

# %%
def horizontal_forces(H, phi, gamma, beta=0.0, q=0.0, hw=0.0, gsat=20.0):
    """List of (name, force kN/m, height above base m) of the horizontal push on the wall back."""
    ka = ka_rankine(phi, beta)
    d = H - hw                                   # depth of the dry zone
    gsub = gsat - GAMMA_W                        # submerged unit weight
    if beta != 0.0 and (hw > 0.0 or q > 0.0):
        raise ValueError("slope is not combined with water or surcharge in this model")
    if beta != 0.0:
        pa = 0.5 * ka * gamma * H ** 2
        return [("soil", pa * np.cos(np.radians(beta)), H / 3.0)]
    parts = [("soil dry zone, triangle", 0.5 * ka * gamma * d ** 2, hw + d / 3.0),
             ("soil dry zone, rectangle on wet zone", ka * gamma * d * hw, hw / 2.0),
             ("soil wet zone, triangle", 0.5 * ka * gsub * hw ** 2, hw / 3.0)]
    if hw > 0.0:
        parts.append(("water", 0.5 * GAMMA_W * hw ** 2, hw / 3.0))
    if q > 0.0:
        parts.append(("surcharge", ka * q * H, H / 2.0))
    return [p for p in parts if p[1] > 0.0]


def wall_state(B, H, mu, phi, gamma, gc=24.0, beta=0.0, q=0.0, hw=0.0, gsat=20.0):
    """Everything about the wall: forces, moments about the toe, factors of safety, base pressure."""
    parts = horizontal_forces(H, phi, gamma, beta, q, hw, gsat)
    ph = sum(f for _, f, _ in parts)
    mo = sum(f * z for _, f, z in parts)                       # overturning moment, kN m/m
    pv = 0.0
    if beta != 0.0:
        pa = ph / np.cos(np.radians(beta))
        pv = pa * np.sin(np.radians(beta))
    W = gc * B * H
    U = 0.5 * GAMMA_W * hw * B
    m_res = W * B / 2.0 + pv * B                               # resisting moment about the toe
    m_ot = mo + U * 2.0 * B / 3.0                              # overturning incl. uplift
    N = W + pv - U                                             # net vertical force on the base
    fs_slide = mu * N / ph if N > 0 else 0.0
    fs_ot = m_res / m_ot
    xbar = (m_res - m_ot) / N if N > 0 else -np.inf            # where N acts, from the toe
    e = B / 2.0 - xbar
    q_toe = N / B * (1.0 + 6.0 * e / B)
    q_heel = N / B * (1.0 - 6.0 * e / B)
    return {"Ph": ph, "Mo": mo, "W": W, "U": U, "Pv": pv, "N": N, "M_res": m_res, "M_ot": m_ot,
            "FS_slide": fs_slide, "FS_ot": fs_ot, "xbar": xbar, "e": e,
            "q_toe": q_toe, "q_heel": q_heel, "middle_third": bool(abs(e) <= B / 6.0 + 1e-12)}


# %% [markdown]
# ## Step 3: pass or fail
# Commonly used guidance (not a code): FS_slide at least about 1.5, FS_ot at least about 2.0,
# and the resultant inside the middle third (e <= B/6), so the heel pressure is not negative.

# %%
FS_SLIDE_MIN, FS_OT_MIN = 1.5, 2.0


def passes(s):
    return bool(s["FS_slide"] >= FS_SLIDE_MIN and s["FS_ot"] >= FS_OT_MIN and s["middle_third"])


def min_width(H, mu, phi, gamma, gc=24.0, hw=0.0, q=0.0, step=0.05, Bmax=10.0):
    """Smallest B (multiple of step) that passes all three checks, or None."""
    for k in range(1, int(round(Bmax / step)) + 1):
        B = round(k * step, 10)
        if passes(wall_state(B, H, mu, phi, gamma, gc, 0.0, q, hw)):
            return B
    return None


# %% [markdown]
# ## Step 4: validation by numerical integration
# Build the pressure profile point by point, integrate it for force and moment, and compare
# with the closed forms. Then check that the base pressure carries the vertical load and
# gives the right moment (equilibrium of the whole free body).

# %%
def numeric_push(H, phi, gamma, q=0.0, hw=0.0, gsat=20.0, n=4000):
    """Integrate effective soil + water pressure along the wall. Returns (force, moment about base)."""
    ka = ka_rankine(phi)
    z = (np.arange(n) + 0.5) * H / n                           # depth of each slice centre
    dz = H / n
    d = H - hw
    sv = np.where(z <= d, gamma * z, gamma * d + (gsat - GAMMA_W) * (z - d))   # effective vertical stress
    p = ka * sv + q * ka + np.where(z > d, GAMMA_W * (z - d), 0.0)
    force = float(np.sum(p) * dz)
    moment = float(np.sum(p * (H - z)) * dz)
    return force, moment


def base_pressure_check(s, B, n=2000):
    """Integrate the linear base pressure: returns (force, moment about the toe)."""
    x = (np.arange(n) + 0.5) * B / n
    qx = s["q_toe"] + (s["q_heel"] - s["q_toe"]) * x / B
    return float(np.sum(qx) * B / n), float(np.sum(qx * x) * B / n)


# %% [markdown]
# ## Step 5: see it
# Left: the safety factors against wall width, with the two limits. Right: the same wall as the
# water table rises in the backfill (the failure case).

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    H, mu, phi, gamma = 4.0, 0.5, 30.0, 18.0
    s = wall_state(2.0, H, mu, phi, gamma)
    print(f"Ka Rankine = {ka_rankine(30):.4f}, Coulomb(delta=0) = {ka_coulomb(30):.4f}, Coulomb(delta=20) = {ka_coulomb(30, 20):.4f}")
    print(f"design wall B=2 m: Pa={s['Ph']:.1f} kN/m  W={s['W']:.1f}  FS_slide={s['FS_slide']:.2f}  FS_ot={s['FS_ot']:.2f}  e={s['e']:.3f} m  B/6={2/6:.3f} m")
    f, m = numeric_push(H, phi, gamma)
    print(f"numeric push {f:.2f} kN/m at {m / f:.3f} m above base")
    w = wall_state(2.0, H, mu, phi, gamma, hw=4.0)
    print(f"saturated: Ph={w['Ph']:.2f}  uplift={w['U']:.2f}  FS_slide={w['FS_slide']:.2f}  FS_ot={w['FS_ot']:.3f}")
    print("min width dry:", min_width(H, mu, phi, gamma), "  min width, water 2 m:", min_width(H, mu, phi, gamma, hw=2.0), " water 4 m:", min_width(H, mu, phi, gamma, hw=4.0))

    Bs = np.linspace(0.8, 4.0, 65)
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    fs = [wall_state(b, H, mu, phi, gamma) for b in Bs]
    ax[0].plot(Bs, [r["FS_slide"] for r in fs], label="sliding")
    ax[0].plot(Bs, [r["FS_ot"] for r in fs], label="overturning")
    ax[0].axhline(FS_SLIDE_MIN, color="C0", ls=":")
    ax[0].axhline(FS_OT_MIN, color="C1", ls=":")
    ax[0].set_xlabel("wall width B (m)")
    ax[0].set_ylabel("factor of safety (no unit)")
    ax[0].set_title("Dry backfill: H = 4 m, friction 0.5")
    ax[0].grid(alpha=0.3)
    ax[0].legend()
    hws = np.linspace(0, 4, 41)
    ws = [wall_state(2.0, H, mu, phi, gamma, hw=h) for h in hws]
    ax[1].plot(hws, [r["FS_slide"] for r in ws], label="sliding")
    ax[1].plot(hws, [r["FS_ot"] for r in ws], label="overturning")
    ax[1].axhline(1.0, color="red", ls="--", label="FS = 1")
    ax[1].set_xlabel("water level in backfill above base (m)")
    ax[1].set_ylabel("factor of safety (no unit)")
    ax[1].set_title("B = 2 m wall as the water rises")
    ax[1].grid(alpha=0.3)
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(OUT / "safety_factors.png", dpi=120)

    mus = np.linspace(0.3, 0.7, 5)
    betas = np.linspace(0, 20, 5)
    tab = np.array([[wall_state(2.0, H, m_, phi, gamma, beta=b_)["FS_slide"] for b_ in betas] for m_ in mus])
    fig2, ax2 = plt.subplots(figsize=(5.5, 4))
    im = ax2.imshow(tab, origin="lower", aspect="auto", extent=[-2.5, 22.5, 0.25, 0.75], cmap="viridis")
    ax2.set_xlabel("backfill slope beta (degrees)")
    ax2.set_ylabel("base friction coefficient (no unit)")
    ax2.set_title("FS_slide, B = 2 m (colour)")
    fig2.colorbar(im, ax=ax2, label="FS_slide")
    fig2.tight_layout()
    fig2.savefig(OUT / "sweep_slide.png", dpi=120)
    print(np.round(tab, 2))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
