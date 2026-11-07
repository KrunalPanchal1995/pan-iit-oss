"""Session 1 (Level 1): lift, drag and the pressure around a wing.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: lift, drag and the pressure around a wing
# **A. Real-world problem.** A small aeroplane in cruise must hold up its weight with lift,
# and its engine must push against drag the whole way. Where does the lift come from, why
# does it grow so fast with speed, and why does the drag (and so the fuel burnt every
# kilometre) depend on the shape of the wing?
#
# **Plan.** (1) dynamic pressure and the lift and drag equations, (2) the lift coefficient a
# wing needs to fly level, and the stall speed, (3) thrust = drag, so fuel per kilometre
# follows from the lift-to-drag ratio, (4) Bernoulli: faster air on top means lower
# pressure, and the pressure difference is the lift.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81            # m/s2, gravity
RHO_SEA = 1.225     # kg/m3, air density at sea level (standard atmosphere)


# %% [markdown]
# ## Step 1: dynamic pressure, lift and drag
# Moving air carries a "pressure of motion" called the dynamic pressure
#
#     q = 1/2 rho V^2        (Pa, with rho in kg/m3 and V in m/s)
#
# Engineers write every aerodynamic force as q times the wing area S times a number that
# only depends on the shape and the angle of the wing:
#
#     L = q S CL        D = q S CD
#
# CL and CD (lift and drag coefficients) have no unit. They let us test a small model in a
# wind tunnel and use the result for a full-size wing.

# %%
def dynamic_pressure(v, rho=RHO_SEA):
    """Dynamic pressure q = 1/2 rho V^2 in Pa."""
    if rho <= 0:
        raise ValueError("air density must be positive")
    return 0.5 * rho * np.asarray(v, float) ** 2


def lift(cl, v, area, rho=RHO_SEA):
    """Lift force in N from L = q S CL."""
    return dynamic_pressure(v, rho) * area * cl


def drag(cd, v, area, rho=RHO_SEA):
    """Drag force in N from D = q S CD."""
    return dynamic_pressure(v, rho) * area * cd


# %% [markdown]
# ## Step 2: the lift coefficient a wing needs, and the stall speed
# In level flight lift equals weight, L = m g. So the wing must work at
#
#     CL_needed = m g / (q S)
#
# Slow flight means a small q, so the wing needs a large CL (it must meet the air at a
# larger angle). A real wing can only reach a maximum CL_max before the flow breaks away
# (stall). The slowest speed it can fly level is the stall speed
#
#     V_stall = sqrt( 2 m g / (rho S CL_max) )

# %%
def cl_needed(mass, v, area, rho=RHO_SEA):
    """Lift coefficient needed for level flight (no unit)."""
    if area <= 0:
        raise ValueError("wing area must be positive")
    return mass * G / (dynamic_pressure(v, rho) * area)


def stall_speed(mass, area, cl_max, rho=RHO_SEA):
    """Slowest level-flight speed in m/s for a given maximum lift coefficient."""
    if cl_max <= 0 or area <= 0:
        raise ValueError("cl_max and area must be positive")
    return np.sqrt(2.0 * mass * G / (rho * area * cl_max))


# %% [markdown]
# ## Step 3: thrust = drag, and the fuel per kilometre
# In steady cruise the engine thrust T balances the drag D. Since L = W,
#
#     D = W / (L/D)
#
# The lift-to-drag ratio L/D = CL / CD is the "efficiency" of the wing shape. The work done
# against drag over a distance s is D s (joules). The engine turns only a share eta of the
# fuel energy into thrust work, so the fuel energy per kilometre is D x 1000 m / eta.
# Better shape -> higher L/D -> less drag -> less fuel. That is why this repo exists.

# %%
def cruise_drag(mass, l_over_d):
    """Drag in N of an aircraft of this mass flying level at this L/D."""
    if l_over_d <= 0:
        raise ValueError("L/D must be positive")
    return mass * G / l_over_d


def fuel_energy_per_km(drag_n, eta_engine=0.25):
    """Fuel energy in J needed to fly 1 km against this drag (engine/propeller efficiency eta)."""
    if not 0 < eta_engine <= 1:
        raise ValueError("engine efficiency must be between 0 and 1")
    return drag_n * 1000.0 / eta_engine


# %% [markdown]
# ## Step 4: where lift comes from: Bernoulli and the pressure coefficient
# Along a streamline of steady, low-speed air, p + 1/2 rho V^2 stays constant (Bernoulli).
# Where the air speeds up, the pressure drops. Engineers measure the local pressure by the
# pressure coefficient
#
#     Cp = (p - p_inf) / q_inf = 1 - (V / V_inf)^2
#
# Cp = 1 at a stagnation point (air stopped), Cp = 0 where the air moves at the free-stream
# speed, and Cp < 0 (suction) where it is faster. If the air on top of a wing is faster than
# underneath, the lower surface pushes up harder than the upper surface pushes down. For a
# toy wing with the same speeds along the whole chord, the lift coefficient is simply
#
#     CL = Cp_lower - Cp_upper

# %%
def pressure_coefficient(v_local, v_inf):
    """Cp = 1 - (V / V_inf)^2 from Bernoulli (no unit)."""
    if v_inf <= 0:
        raise ValueError("free-stream speed must be positive")
    return 1.0 - (np.asarray(v_local, float) / v_inf) ** 2


def toy_wing_cl(speed_ratio_upper, speed_ratio_lower):
    """CL of a toy wing whose upper and lower air speeds are fixed multiples of V_inf."""
    return float(pressure_coefficient(speed_ratio_lower, 1.0) - pressure_coefficient(speed_ratio_upper, 1.0))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # The worked example: a 1000 kg two-seater with a 16 m2 wing at 50 m/s
    m, s, v = 1000.0, 16.0, 50.0
    q = dynamic_pressure(v)
    cl = cl_needed(m, v, s)
    print(f"q = {q:.2f} Pa, CL needed = {cl:.4f}, stall speed (CL_max 1.4) = {stall_speed(m, s, 1.4):.2f} m/s")
    d = drag(0.03, v, s)
    print(f"with CD = 0.03: D = {d:.1f} N, L/D = {cl / 0.03:.2f}, fuel energy per km = {fuel_energy_per_km(d) / 1e6:.3f} MJ")
    print(f"toy wing, upper 1.2 V_inf, lower 0.95 V_inf: CL = {toy_wing_cl(1.2, 0.95):.4f}")

    # Figure 1: lift needs speed. Lift at fixed CL, and the CL needed, against speed
    vv = np.linspace(20.0, 80.0, 200)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for c in (0.3, 0.6, 1.2):
        axes[0].plot(vv, lift(c, vv, s) / 1000.0, label=f"CL = {c}")
    axes[0].axhline(m * G / 1000.0, color="k", ls="--", lw=1)
    axes[0].text(21, m * G / 1000.0 + 0.6, "weight of 1000 kg = 9.81 kN", fontsize=9)
    axes[0].set_xlabel("speed V (m/s)")
    axes[0].set_ylabel("lift L (kN)")
    axes[0].set_title("L = 1/2 rho V^2 S CL (S = 16 m2)")
    axes[0].set_ylim(0, 40)
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)
    axes[1].plot(vv, cl_needed(m, vv, s), color="#2a9d8f", lw=2, label="CL needed for level flight")
    axes[1].axhline(1.4, color="#d9534f", ls="--", label="CL_max = 1.4 (stall)")
    vs = stall_speed(m, s, 1.4)
    axes[1].plot(vs, 1.4, "o", color="#d9534f")
    axes[1].annotate(f"stall speed {vs:.1f} m/s", (vs, 1.4), xytext=(vs + 6, 1.65), arrowprops=dict(arrowstyle="->"))
    axes[1].plot(v, cl, "ko")
    axes[1].annotate(f"cruise 50 m/s: CL = {cl:.2f}", (v, cl), xytext=(v + 3, cl + 0.35), arrowprops=dict(arrowstyle="->"))
    axes[1].set_xlabel("speed V (m/s)")
    axes[1].set_ylabel("lift coefficient (no unit)")
    axes[1].set_ylim(0, 2.2)
    axes[1].set_title("Slow flight needs a large CL")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "lift_vs_speed.png", dpi=120)

    # Figure 2: (left) toy-wing pressures; (right) shape sets L/D and the fuel per km
    fig2, axes = plt.subplots(1, 2, figsize=(10, 4))
    cpu, cpl = pressure_coefficient(1.2, 1.0), pressure_coefficient(0.95, 1.0)
    axes[0].bar([0, 1], [cpu, cpl], color=["#1f6feb", "#d9534f"])
    axes[0].axhline(0, color="k", lw=1)
    axes[0].set_xticks([0, 1])
    axes[0].set_xticklabels(["upper surface\nV = 1.2 V_inf", "lower surface\nV = 0.95 V_inf"])
    axes[0].set_ylabel("pressure coefficient Cp (no unit)")
    axes[0].set_title(f"CL = Cp_lower - Cp_upper = {cpl:.4f} - ({cpu:.2f}) = {cpl - cpu:.4f}", fontsize=10)
    for k, val in enumerate([cpu, cpl]):
        axes[0].text(k, val + (0.03 if val > 0 else -0.06), f"{val:.4f}", ha="center")
    axes[0].set_ylim(-0.6, 0.3)
    axes[0].grid(alpha=0.3, axis="y")
    lds = [8.0, 12.0, 16.0]
    fuel = [fuel_energy_per_km(cruise_drag(m, ld)) / 1e6 for ld in lds]
    axes[1].bar(range(3), fuel, color="#2a9d8f")
    for k, (ld, f) in enumerate(zip(lds, fuel)):
        axes[1].text(k, f + 0.08, f"D = {cruise_drag(m, ld):.0f} N\n{f:.2f} MJ/km", ha="center", fontsize=9)
        print(f"L/D = {ld:.0f}: drag {cruise_drag(m, ld):.0f} N, fuel energy {f:.2f} MJ per km")
    axes[1].set_xticks(range(3))
    axes[1].set_xticklabels([f"L/D = {ld:.0f}" for ld in lds])
    axes[1].set_ylabel("fuel energy per km (MJ)")
    axes[1].set_ylim(0, 6.5)
    axes[1].set_title("1000 kg aircraft, engine efficiency 0.25")
    axes[1].grid(alpha=0.3, axis="y")
    fig2.tight_layout()
    fig2.savefig(OUT / "pressure_and_fuel.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Here CL, CD and the air speeds over the wing were simply given. Session 2 shows how the
# shape of an airfoil (its camber and thickness) and its angle of attack set CL, and how the
# drag grows with lift. Session 3 computes the real speeds all round the airfoil.
