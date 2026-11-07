"""Session 2 (Level 2): size a footing from the allowable pressure, Terzaghi capacity, eccentric loads.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: from soil strength to footing size
# **A. Real-world problem.** A 600 kN column must stand on soil whose allowable bearing
# pressure is 150 kPa. How wide must the square footing be once we count the footing's own
# weight and a factor of safety? And where does the allowable pressure come from?
# Educational model only: never use it to design a real foundation.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
GAMMA_CONCRETE = 24.0     # unit weight of reinforced concrete, kN/m^3 (typical textbook value)


# %% [markdown]
# ## Step 1: contact pressure with the footing's own weight
# Soil carries the column load P plus the footing weight W = 24 * B^2 * t (t = thickness).
#
#     q = (P + 24 B^2 t) / B^2 = P / B^2 + 24 t
#
# The allowable pressure q_allow already contains a factor of safety, so we need q <= q_allow:
#
#     B >= sqrt( P / (q_allow - 24 t) )

# %%
def contact_pressure(load_kn, side_m, thickness_m=0.6):
    """Pressure (kPa) on the soil under a square footing including its own weight."""
    return (load_kn + GAMMA_CONCRETE * side_m ** 2 * thickness_m) / side_m ** 2


def required_side(load_kn, q_allow_kpa, thickness_m=0.6, step=0.05):
    """Smallest square side (m), rounded UP to `step`, with contact pressure <= q_allow."""
    net = q_allow_kpa - GAMMA_CONCRETE * thickness_m
    if net <= 0:
        raise ValueError("the footing weight alone uses up the allowable pressure")
    exact = math.sqrt(load_kn / net)
    return math.ceil(exact / step - 1e-9) * step


# %% [markdown]
# ## Step 2: where allowable pressure comes from (Terzaghi, strip footing)
# Terzaghi's bearing capacity equation for a long strip footing:
#
#     q_ult = c N_c + q N_q + 0.5 gamma B N_gamma
#
# c = cohesion (kPa), q = soil pressure beside the footing at its base = gamma * D_f (kPa),
# gamma = soil unit weight (kN/m^3), B = width (m). For saturated clay in short-term loading
# (phi = 0) the factors are N_c = 5.7, N_q = 1, N_gamma = 0, so q_ult = 5.7 c + gamma D_f.
# The allowable pressure is q_allow = q_ult / FS, with a factor of safety FS of about 3.
# For phi > 0, N_q and N_c follow from formulas below (N_gamma needs a table: not computed here).

# %%
def terzaghi_nq(phi_deg):
    p = math.radians(phi_deg)
    a = math.exp((0.75 * math.pi - p / 2) * math.tan(p))
    return a * a / (2 * math.cos(math.pi / 4 + p / 2) ** 2)


def terzaghi_nc(phi_deg):
    """N_c = (N_q - 1) cot(phi); for phi = 0 the standard Terzaghi value 5.7 is returned."""
    if phi_deg == 0:
        return 5.7
    return (terzaghi_nq(phi_deg) - 1) / math.tan(math.radians(phi_deg))


def q_ult_strip_phi0(cohesion_kpa, gamma_knm3=0.0, depth_m=0.0):
    """Ultimate bearing pressure (kPa) of a strip footing on clay with phi = 0."""
    return 5.7 * cohesion_kpa + gamma_knm3 * depth_m


def allowable_from_ultimate(q_ult_kpa, fs=3.0):
    return q_ult_kpa / fs


def factor_of_safety(q_ult_kpa, q_applied_kpa):
    return q_ult_kpa / q_applied_kpa


# %% [markdown]
# ## Step 3: eccentric loads and the middle third
# If the load acts a distance e from the footing centre, one edge is pressed harder.
# For a footing of width B (length L), the edge pressures are
#
#     q_max,min = P / (B L) * (1 +- 6 e / B)
#
# The small edge pressure reaches zero when e = B/6 (the "middle third" rule). Beyond that
# the soil cannot pull on the footing: part of the base lifts off and the contact length
# shrinks to 3 (B/2 - e), giving q_max = 2 P / (3 L (B/2 - e)).

# %%
def edge_pressures(load_kn, width_m, e_m, length_m=1.0):
    """Return (q_max, q_min, full_contact). Use length_m = 1 for a load per metre of a strip."""
    if e_m <= width_m / 6 * (1 + 1e-12):
        mean = load_kn / (width_m * length_m)
        k = 6 * e_m / width_m
        return mean * (1 + k), mean * (1 - k), True
    contact = 3 * (width_m / 2 - e_m)
    if contact <= 0:
        raise ValueError("load acts outside the footing")
    return 2 * load_kn / (contact * length_m), 0.0, False


# %% [markdown]
# ## Step 4: see it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    B = required_side(600, 150)
    print("600 kN on 150 kPa, t = 0.6 m: exact", round(math.sqrt(600 / (150 - 14.4)), 3), "-> B =", round(B, 2), "m")
    print("contact pressure at that size:", round(contact_pressure(600, B), 1), "kPa; at 2.10 m:", round(contact_pressure(600, 2.10), 1), "kPa")
    print("clay c = 50 kPa strip: q_ult =", q_ult_strip_phi0(50), "kPa, q_allow (FS 3) =", round(allowable_from_ultimate(285), 1), "kPa")
    print("phi = 30: Nq =", round(terzaghi_nq(30), 1), " Nc =", round(terzaghi_nc(30), 1))
    print("strip 2 m wide, 300 kN/m, e = 0.2:", [round(v, 1) if not isinstance(v, bool) else v for v in edge_pressures(300, 2.0, 0.2)])
    print("e = B/6:", [round(v, 1) if not isinstance(v, bool) else v for v in edge_pressures(300, 2.0, 2.0 / 6)])
    print("e = 0.5:", [round(v, 1) if not isinstance(v, bool) else v for v in edge_pressures(300, 2.0, 0.5)])

    qa = np.linspace(60, 400, 100)
    fig, ax = plt.subplots(figsize=(6, 4))
    for P, col in ((300, "C0"), (600, "C1"), (1200, "C2")):
        ax.plot(qa, [math.sqrt(P / (q - 14.4)) for q in qa], color=col, label=f"P = {P} kN")
    ax.plot([150], [math.sqrt(600 / (150 - 14.4))], "ko")
    ax.set_xlabel("allowable bearing pressure q_allow (kPa)")
    ax.set_ylabel("required square side B (m)")
    ax.set_title("Weaker soil needs a much wider footing (t = 0.6 m)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "required_width.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    x = np.linspace(-1, 1, 201)
    for e, col in ((0.0, "C0"), (0.2, "C1"), (1.0 / 3, "C2"), (0.5, "C3")):
        qmax, qmin, full = edge_pressures(300, 2.0, e)
        if full:
            q = (300 / 2.0) * (1 + 12 * e * x / 2.0 ** 2)     # straight-line pressure, x measured from the centre
        else:
            xl = 1.0 - 3 * (1.0 - e)
            q = np.where(x >= xl, qmax * (x - xl) / (1.0 - xl), 0.0)
        ax2.plot(x, q, color=col, label=f"e = {e:.2f} m")
    ax2.set_xlabel("position across the footing (m)")
    ax2.set_ylabel("pressure on soil (kPa)")
    ax2.set_title("Eccentric load, strip 2 m wide, 300 kN/m")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "eccentric_pressure.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
