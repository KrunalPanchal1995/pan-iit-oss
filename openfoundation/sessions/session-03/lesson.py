"""Session 3 (Level 3): settlement, consolidation, stress spreading, and a footing layout with even settlement.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: how far does it sink, and how fast?
# **A. Real-world problem.** A footing can be strong enough and still sink too far, or sink
# more under one column than under its neighbour, which cracks walls. Settlement has two
# parts: an immediate elastic part and, in clay, a slow squeezing-out of water called
# consolidation that takes years. Today you compute both, check the stress spreading with
# 2:1 and with Boussinesq, validate against closed forms, and then size a small building's
# footings for even settlement. Educational model only: never use it to design a real foundation.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
GAMMA_CONCRETE = 24.0     # kN/m^3
I_RIGID_SQUARE = 0.82     # our chosen influence factor for a rigid square footing (textbook value)


# %% [markdown]
# ## Step 1: immediate (elastic) settlement
# The soil is treated as an elastic half-space with Young's modulus E (kPa) and Poisson's
# ratio nu. A footing of width B carrying pressure q settles
#
#     s = q B (1 - nu^2) I / E
#
# I is an influence factor that depends on the footing shape and stiffness. We choose
# I = 0.82 for a rigid square footing (a textbook value; the checkpoint brackets it between
# the exact rigid circle, pi/4 = 0.785, and the flexible square average, about 0.95).

# %%
def immediate_settlement(q_kpa, width_m, e_kpa, nu=0.3, influence=I_RIGID_SQUARE):
    """Elastic settlement (m)."""
    return q_kpa * width_m * (1 - nu ** 2) * influence / e_kpa


def _corner(a, b):
    """Corner settlement of a uniformly loaded a x b rectangle, in units of q (1 - nu^2) / (pi E)."""
    d = math.hypot(a, b)
    return a * math.log((b + d) / a) + b * math.log((a + d) / b)


def flexible_square_factors(n=40):
    """Influence factors (centre, average) of a UNIFORMLY loaded flexible square, by superposition of corner formulas."""
    pts = (np.arange(n) + 0.5) / n          # side = 1
    vals = np.zeros((n, n))
    for i, x in enumerate(pts):
        for j, y in enumerate(pts):
            vals[i, j] = sum(_corner(u, v) for u in (x, 1 - x) for v in (y, 1 - y)) / math.pi
    return 4 * _corner(0.5, 0.5) / math.pi, float(vals.mean())


# %% [markdown]
# ## Step 2: consolidation settlement of a clay layer
# When a clay layer is loaded, water is slowly squeezed out and the layer thins. For a layer
# of thickness H with compression index Cc, initial void ratio e0, initial effective stress
# sigma0 at mid-layer and added stress dsigma:
#
#     s = H Cc / (1 + e0) * log10( (sigma0 + dsigma) / sigma0 )
#
# How fast? With time factor T_v = c_v t / H_dr^2 (c_v = coefficient of consolidation,
# H_dr = longest drainage path) the average degree of consolidation is the series
#
#     U = 1 - sum over m of  2 / M^2 * exp(-M^2 T_v),   M = (2m + 1) pi / 2.

# %%
def consolidation_settlement(h_m, cc, e0, sigma0_kpa, dsigma_kpa):
    return h_m * cc / (1 + e0) * math.log10((sigma0_kpa + dsigma_kpa) / sigma0_kpa)


def degree_of_consolidation(tv, terms=2000):
    m = (np.arange(terms) + 0.5) * math.pi
    return float(1 - np.sum(2 / m ** 2 * np.exp(-m ** 2 * tv)))


def time_factor_for(u, tol=1e-12):
    """Invert U(T_v) by bisection (0 < u < 1)."""
    lo, hi = 0.0, 5.0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if degree_of_consolidation(mid) < u:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def time_for_degree(u, cv_m2_per_year, h_dr_m):
    """Time in years to reach average degree of consolidation u."""
    return time_factor_for(u) * h_dr_m ** 2 / cv_m2_per_year


CLAY_TOP_M = 2.0         # clay starts 2 m below the footing base
FOOTING_DEPTH_M = 1.0    # footing base is 1 m below the ground surface
GAMMA_EFF = 9.0          # effective unit weight of the soil, kN/m^3 (assumed)
CC, E0 = 0.3, 0.9        # compression index and initial void ratio of the clay (assumed)


def clay_layer_response(load_kn, side_m, h_dr_m, cv_m2_per_year):
    """Double-drained clay layer of thickness 2 * h_dr below a square footing (2:1 spread to mid-layer).

    Returns (added stress at mid-layer in kPa, initial effective stress in kPa, final settlement in m, t90 in years).
    """
    z_mid = CLAY_TOP_M + h_dr_m
    dsig = stress_2to1(load_kn, side_m, z_mid)
    sig0 = GAMMA_EFF * (FOOTING_DEPTH_M + z_mid)
    s_final = consolidation_settlement(2 * h_dr_m, CC, E0, sig0, dsig)
    return dsig, sig0, s_final, time_for_degree(0.9, cv_m2_per_year, h_dr_m)


# %% [markdown]
# ## Step 3: how the stress spreads with depth
# Under a footing carrying P, the added vertical stress dies away with depth z.
# * 2:1 approximation (a quick rule, only an approximation): the load spreads at a slope of
#   2 vertical to 1 horizontal, so a square footing of side B loads a square of side B + z:
#   dsigma = P / (B + z)^2.
# * Boussinesq (elastic half-space), point load P, directly below it:
#   dsigma = 3 P / (2 pi z^2). In general dsigma = 3 P z^3 / (2 pi R^5), R = distance to the load.
# Add up point loads over the footing area to get the stress under a real footing.

# %%
def stress_2to1(load_kn, side_m, z_m):
    return load_kn / (side_m + z_m) ** 2


def boussinesq_axis(load_kn, z_m):
    """Vertical stress (kPa) on the axis of a point load."""
    return 3 * load_kn / (2 * math.pi * z_m ** 2)


def boussinesq_point(load_kn, x_m, y_m, z_m):
    r = math.sqrt(x_m ** 2 + y_m ** 2 + z_m ** 2)
    return 3 * load_kn * z_m ** 3 / (2 * math.pi * r ** 5)


def stress_square_centre(q_kpa, side_m, z_m, n=60):
    """Stress under the centre of a uniformly loaded square, by summing n x n point loads."""
    h = side_m / n
    xs = (np.arange(n) + 0.5) * h - side_m / 2
    gx, gy = np.meshgrid(xs, xs)
    r = np.sqrt(gx ** 2 + gy ** 2 + z_m ** 2)
    return float(np.sum(3 * q_kpa * h * h * z_m ** 3 / (2 * math.pi * r ** 5)))


def stress_circle_numeric(q_kpa, radius_m, z_m, n=2000):
    """Stress under the centre of a uniformly loaded circle, by summing rings of point loads."""
    dr = radius_m / n
    r = (np.arange(n) + 0.5) * dr
    dp = q_kpa * 2 * math.pi * r * dr
    big_r = np.sqrt(r ** 2 + z_m ** 2)
    return float(np.sum(3 * dp * z_m ** 3 / (2 * math.pi * big_r ** 5)))


def stress_circle_closed(q_kpa, radius_m, z_m):
    """Closed form under the centre of a uniformly loaded circle."""
    return q_kpa * (1 - (1 / (1 + (radius_m / z_m) ** 2)) ** 1.5)


# %% [markdown]
# ## Step 4: failure cases
# 1. Bearing failure: the soil shears when the pressure reaches q_ult; we require the
#    pressure to stay below q_ult / FS.
# 2. Differential settlement: neighbouring footings settle by different amounts.

# %%
def strip_bearing_check(line_load_knm, width_m, cohesion_kpa, thickness_m=0.6, fs_required=3.0):
    """Check a strip footing on phi = 0 clay. Returns (pressure, q_ult, FS, passes)."""
    q = line_load_knm / width_m + GAMMA_CONCRETE * thickness_m
    q_ult = 5.7 * cohesion_kpa
    fs = q_ult / q
    return q, q_ult, fs, fs >= fs_required


def collapse_line_load(width_m, cohesion_kpa, thickness_m=0.6):
    """Line load (kN/m) at which the pressure equals q_ult (FS = 1)."""
    return (5.7 * cohesion_kpa - GAMMA_CONCRETE * thickness_m) * width_m


def settlements(loads_kn, sides_m, e_kpa, nu=0.3, influence=I_RIGID_SQUARE):
    """Elastic settlement (m) of each square footing under its column load (net pressure P / B^2)."""
    return [immediate_settlement(p / b ** 2, b, e_kpa, nu, influence) for p, b in zip(loads_kn, sides_m)]


def differential(values):
    return max(values) - min(values)


# %% [markdown]
# ## Step 5: mini-project helper, even settlement
# Elastic settlement of a rigid square footing is s = k P / B with k = (1 - nu^2) I / E:
# for the same load a wider footing sinks LESS. Bearing needs B >= B_bear; a target
# settlement s_t needs B >= k P / s_t. Take the larger, rounded up to 0.05 m.

# %%
def bearing_side(load_kn, q_allow_kpa, thickness_m=0.6, step=0.05):
    net = q_allow_kpa - GAMMA_CONCRETE * thickness_m
    return math.ceil(math.sqrt(load_kn / net) / step - 1e-9) * step


def design_for_target(loads_kn, q_allow_kpa, s_target_m, e_kpa, nu=0.3, influence=I_RIGID_SQUARE, step=0.05):
    """Sides (m) meeting both the bearing limit and a target settlement."""
    k = (1 - nu ** 2) * influence / e_kpa
    return [max(bearing_side(p, q_allow_kpa), math.ceil(k * p / s_target_m / step - 1e-9) * step) for p in loads_kn]


# %% [markdown]
# ## Step 6: see it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("elastic: q 150 kPa, B 2 m, E 20 MPa, nu 0.3 ->", round(immediate_settlement(150, 2.0, 20000) * 1000, 1), "mm")
    print("flexible square factors (centre, average):", [round(v, 3) for v in flexible_square_factors()])
    s = consolidation_settlement(4.0, 0.3, 0.9, 100.0, 50.0)
    print("consolidation settlement:", round(s * 1000, 1), "mm")
    print("Tv for U = 50%, 90%:", round(time_factor_for(0.5), 3), round(time_factor_for(0.9), 3))
    print("t50, t90 (cv 1.5 m2/yr, Hdr 2 m):", round(time_for_degree(0.5, 1.5, 2.0), 2), round(time_for_degree(0.9, 1.5, 2.0), 2), "years")
    print("z = 3 m under 600 kN / 2 m square:", round(stress_2to1(600, 2, 3), 1), round(stress_square_centre(150, 2, 3), 1), round(boussinesq_axis(600, 3), 1))
    print("circle a = 1, z = 1:", round(stress_circle_numeric(100, 1, 1), 2), round(stress_circle_closed(100, 1, 1), 2))
    print("strip 150 kN/m on B 1.5 c 50:", [round(v, 2) if not isinstance(v, bool) else v for v in strip_bearing_check(150, 1.5, 50)], "collapse", round(collapse_line_load(1.5, 50), 1), "kN/m")

    loads = [250, 450, 800, 1200]
    std = [bearing_side(p, 150) for p in loads]
    print("standard sides", [round(b, 2) for b in std], "settlements mm", [round(v * 1000, 1) for v in settlements(loads, std, 20000)])
    for st in (0.008, 0.010, 0.012):
        ev = design_for_target(loads, 150, st, 20000)
        sv = settlements(loads, ev, 20000)
        print("target", st * 1000, "mm sides", [round(b, 2) for b in ev], "settle", [round(v * 1000, 1) for v in sv],
              "diff", round(differential(sv) * 1000, 2), "area", round(sum(b * b for b in ev), 1))

    z = np.linspace(0.5, 8, 100)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(z, [stress_2to1(600, 2, v) for v in z], label="2:1 approximation")
    ax.plot(z, [stress_square_centre(150, 2, v) for v in z], label="Boussinesq, sum over the footing")
    ax.plot(z, [boussinesq_axis(600, v) for v in z], "--", label="Boussinesq, one point load")
    ax.set_xlabel("depth below footing z (m)")
    ax.set_ylabel("added vertical stress on the axis (kPa)")
    ax.set_title("600 kN on a 2 m square footing")
    ax.set_ylim(0, 160)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "stress_with_depth.png", dpi=120)

    tv = np.logspace(-3, 1, 200)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.semilogx(tv, [100 * degree_of_consolidation(t) for t in tv], color="C0")
    ax2.plot([time_factor_for(0.5), time_factor_for(0.9)], [50, 90], "ro")
    ax2.set_xlabel("time factor T_v (no unit, log scale)")
    ax2.set_ylabel("average degree of consolidation U (%)")
    ax2.set_title("U = 50% at T_v = 0.197, U = 90% at T_v = 0.848")
    ax2.grid(alpha=0.3, which="both")
    fig2.tight_layout()
    fig2.savefig(OUT / "consolidation_curve.png", dpi=120)

    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ev = design_for_target(loads, 150, 0.010, 20000)
    xs = np.arange(len(loads))
    ax3.bar(xs - 0.2, [v * 1000 for v in settlements(loads, std, 20000)], 0.4, label="sized for bearing only")
    ax3.bar(xs + 0.2, [v * 1000 for v in settlements(loads, ev, 20000)], 0.4, label="sized for 10 mm target")
    ax3.set_xticks(xs, [f"{p} kN" for p in loads])
    ax3.set_xlabel("column load")
    ax3.set_ylabel("elastic settlement (mm)")
    ax3.set_title("Differential settlement of four footings")
    ax3.grid(alpha=0.3, axis="y")
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(OUT / "differential_settlement.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
