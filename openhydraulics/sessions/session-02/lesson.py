"""Session 2 (Level 2): the mathematics of the hydraulic jack: p = F/A, F2 = F1 A2/A1, work balance, p = rho g h.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the equations of a hydraulic jack
# **A. Real-world problem.** A workshop wants to lift a 1200 kg car by pushing a lever with
# no more than 200 N. How wide must the two pistons be, how long a lever do we need, and how
# many pumps of the handle does each centimetre of lift cost? Today we turn the Session 1
# idea into numbers and answer those questions.
#
# **Plan.** (1) pressure and its units, (2) Pascal's law and the work balance, (3) pressure
# due to the weight of a liquid column, (4) the design problem.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81                      # m/s^2
RHO_OIL = 870.0               # kg/m^3, a typical hydraulic oil
RHO_WATER = 1000.0            # kg/m^3
P_ATM = 101325.0              # Pa, standard atmosphere


# %% [markdown]
# ## Step 1: pressure and units
# p = F / A. One pascal is one N/m^2, which is small, so we also use kPa (1000 Pa) and bar
# (100 000 Pa; about one atmosphere). Always convert lengths to metres before dividing:
# a 20 mm piston has diameter 0.020 m.

# %%
def area_circle(d):
    """Area (m^2) of a circle of diameter d (m)."""
    return np.pi * d ** 2 / 4.0


def pressure(force, area):
    """p = F / A in Pa."""
    return force / area


def to_kpa(p):
    return p / 1000.0


def to_bar(p):
    return p / 1e5


# %% [markdown]
# ## Step 2: Pascal's law, mechanical advantage and the work balance
# Same pressure on both pistons: F1 / A1 = F2 / A2, so F2 = F1 (A2 / A1). The mechanical
# advantage is MA = F2 / F1 = A2 / A1. For an ideal jack (no friction, no leakage, liquid
# that cannot be squashed) the volume moved is equal on both sides, A1 d1 = A2 d2, so
# F1 d1 = F2 d2: the work put in equals the work got out.

# %%
def pascal_force(f1, a1, a2):
    """F2 = F1 * (A2 / A1) in N."""
    return f1 * a2 / a1


def mechanical_advantage(a1, a2):
    """MA = A2 / A1 (no unit)."""
    return a2 / a1


def big_piston_travel(d1, a1, a2):
    """Travel d2 of the big piston for a travel d1 of the small one (volume balance)."""
    return d1 * a1 / a2


# %% [markdown]
# ## Step 3: the pressure of a liquid column
# Even without a piston, a liquid has a pressure that grows with depth h: p = rho g h
# (rho = density in kg/m^3, g = 9.81 m/s^2). The total pressure at depth h in an open tank is
# p_atm + rho g h. In a jack the oil column is only tens of centimetres tall, so rho g h is
# tiny next to the megapascal pressures made by the pistons: we can ignore it there.

# %%
def hydrostatic_pressure(rho, h, g=G):
    """Gauge pressure rho * g * h in Pa."""
    return rho * g * h


# %% [markdown]
# ## Step 4: the design problem
# A lever of ratio r (handle length / distance from pivot to pump piston) multiplies the
# hand force: F1 = r * F_hand, and the handle moves r times as far as the pump piston.
# Steps: weight W = m g; the big piston must give F2 >= W; so A2 >= A1 W / F1.
# Each pump stroke of the small piston (stroke s1) lifts the car by s1 / MA. Pumps per
# centimetre = 0.01 m / (s1 / MA). (A real jack has check valves so that the pump piston can
# refill between strokes; the model ignores that.)

# %%
def min_big_diameter(mass, f_hand, lever, d1):
    """Smallest big-piston diameter (m) that just lifts mass (kg)."""
    f1 = lever * f_hand
    return d1 * np.sqrt(mass * G / f1)


def design_jack(mass, f_hand, lever, d1, d2, stroke):
    """Return the main numbers of a jack (SI units: kg, N, m)."""
    f1 = lever * f_hand
    a1, a2 = area_circle(d1), area_circle(d2)
    ma = mechanical_advantage(a1, a2)
    lift_per_stroke = big_piston_travel(stroke, a1, a2)
    return {
        "weight": mass * G,
        "F1": f1,
        "pressure": pressure(f1, a1),
        "MA": ma,
        "F2": pascal_force(f1, a1, a2),
        "lift_per_stroke": lift_per_stroke,
        "pumps_per_cm": 0.01 / lift_per_stroke,
        "hand_travel_per_stroke": lever * stroke,
        "lifts": pascal_force(f1, a1, a2) >= mass * G * (1.0 - 1e-9),   # tolerance for round-off at the exact limit
    }


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("units: 1 bar =", to_kpa(1e5), "kPa;  1 atm =", round(to_bar(P_ATM), 3), "bar")
    for name, rho, h in (("water 10 m", RHO_WATER, 10.0), ("oil 0.5 m", RHO_OIL, 0.5)):
        print(f"{name}: rho g h = {to_kpa(hydrostatic_pressure(rho, h)):.2f} kPa")

    m, f_hand, lever, d1, stroke = 1200.0, 200.0, 10.0, 0.020, 0.040
    d2_min = min_big_diameter(m, f_hand, lever, d1)
    print(f"smallest big piston: {d2_min * 1000:.1f} mm; choose 50 mm")
    r = design_jack(m, f_hand, lever, d1, 0.050, stroke)
    for k, v in r.items():
        print(f"  {k}: {v}")

    d2 = np.linspace(0.02, 0.08, 200)
    f2 = np.array([design_jack(m, f_hand, lever, d1, d, stroke)["F2"] for d in d2])
    pumps = np.array([design_jack(m, f_hand, lever, d1, d, stroke)["pumps_per_cm"] for d in d2])
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(d2 * 1000, f2 / 1000, label="F2 (lever 10, 200 N hand)")
    ax[0].axhline(m * G / 1000, color="C3", ls="--", label="weight of the car")
    ax[0].axvline(d2_min * 1000, color="gray", ls=":", label=f"minimum {d2_min * 1000:.1f} mm")
    ax[0].set_xlabel("big piston diameter (mm)")
    ax[0].set_ylabel("lifting force (kN)")
    ax[0].set_title("Big piston must exceed the minimum")
    ax[0].grid(alpha=0.3)
    ax[0].legend()
    ax[1].plot(d2 * 1000, pumps)
    ax[1].set_xlabel("big piston diameter (mm)")
    ax[1].set_ylabel("pumps per cm of lift")
    ax[1].set_title("The price: more pumps (40 mm stroke, 20 mm pump piston)")
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "design_curves.png", dpi=120)

    depth = np.linspace(0, 10, 50)
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    ax2.plot(to_kpa(hydrostatic_pressure(RHO_WATER, depth)), depth)
    ax2.invert_yaxis()
    ax2.set_xlabel("gauge pressure rho g h (kPa)")
    ax2.set_ylabel("depth h (m)")
    ax2.set_title("Pressure grows linearly with depth (water)")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "pressure_vs_depth.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
