"""Session 1 (Level 1): a drone hovers when its rotors push up exactly as hard as gravity pulls down.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: thrust, weight and why a drone cannot hover on a fixed throttle
# **A. Real-world problem.** A delivery drone of 1.2 kg must hover still above a doorstep.
# Its four rotors push air down and the air pushes the drone up. How fast must the rotors
# spin to hover? And if someone clips on a 0.2 kg parcel and the pilot does not touch the
# throttle, what happens next?
#
# **Plan.** (1) weight and rotor thrust, (2) the hover speed of each rotor, (3) thrust-to-weight
# ratio, (4) Newton's second law in the vertical direction, (5) what a fixed throttle does when
# the mass is not what we assumed. This last step is why every drone needs feedback.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G = 9.81          # gravitational acceleration (m/s^2)
K_T = 1.0e-5      # rotor thrust coefficient (N per (rad/s)^2), typical of a 10-inch propeller
RHO = 1.225       # density of air at sea level (kg/m^3)


# %% [markdown]
# ## Step 1: weight and rotor thrust
# Gravity pulls the drone down with its weight W = m g (newtons, N). A spinning propeller
# throws air downwards; by Newton's third law the air pushes the propeller up. For a fixed
# propeller this thrust grows with the **square** of the spin speed omega (rad/s):
#
#     T = k_T omega^2
#
# Double the speed and you get four times the thrust. k_T depends on the propeller's size,
# shape and the air density; we use 1.0e-5 N/(rad/s)^2.

# %%
def weight(mass, g=G):
    """Weight in N of a mass in kg."""
    if mass <= 0:
        raise ValueError("mass must be positive")
    return mass * g


def rotor_thrust(omega, k_t=K_T):
    """Thrust (N) of one rotor spinning at omega rad/s: T = k_T omega^2."""
    return k_t * np.asarray(omega, float) ** 2


def rpm_from_omega(omega):
    """Convert rad/s to revolutions per minute."""
    return np.asarray(omega, float) * 60.0 / (2.0 * np.pi)


# %% [markdown]
# ## Step 2: the hover speed
# To hover, the total thrust of the n rotors must equal the weight, so each rotor carries
# W / n and spins at
#
#     omega_hover = sqrt(m g / (n k_T))

# %%
def hover_omega(mass, n_rotors=4, k_t=K_T, g=G):
    """Spin speed (rad/s) at which n equal rotors exactly carry the weight."""
    if n_rotors < 1:
        raise ValueError("need at least one rotor")
    return np.sqrt(weight(mass, g) / (n_rotors * k_t))


# %% [markdown]
# ## Step 3: thrust-to-weight ratio
# A drone that can only just carry itself cannot climb, fight a gust or recover from a tilt.
# The thrust-to-weight ratio is the most total thrust divided by the weight. Builders aim for
# at least 2; racing drones go above 5.

# %%
def thrust_to_weight(mass, omega_max, n_rotors=4, k_t=K_T, g=G):
    """Largest total thrust divided by weight (no unit)."""
    return n_rotors * float(rotor_thrust(omega_max, k_t)) / weight(mass, g)


# %% [markdown]
# ## Step 4: Newton's second law, up and down
# Take "up" as positive. The net force is total thrust minus weight, so
#
#     m a = T_total - m g        a = T_total / m - g
#
# If the thrust is held fixed, a is constant and, starting at rest, the height changes by
# z(t) = a t^2 / 2. A small mistake in thrust grows into a large mistake in height, because
# the error is squared in time.

# %%
def vertical_acceleration(total_thrust, mass, g=G):
    """Vertical acceleration (m/s^2, up positive) for a given total thrust."""
    return total_thrust / mass - g


def open_loop_height(t, total_thrust, mass, g=G):
    """Height change (m) after time t (s), from rest, with the thrust held fixed."""
    a = vertical_acceleration(total_thrust, mass, g)
    return 0.5 * a * np.asarray(t, float) ** 2


def time_to_drop(distance, total_thrust, mass, g=G):
    """Time (s) to sink a distance (m) from rest. Returns inf if the drone does not sink."""
    a = vertical_acceleration(total_thrust, mass, g)
    if a >= 0:
        return float("inf")
    return float(np.sqrt(2.0 * distance / -a))


# %% [markdown]
# ## Step 5 (extra): hovering costs power even when nothing moves
# Momentum theory says a rotor of disc area A that makes thrust T in still air needs at least
# the ideal induced power P = T^1.5 / sqrt(2 rho A). Real rotors need roughly 1.5 times more.
# A heavier drone needs more thrust and therefore more power: (1.4 / 1.2)^1.5 = 1.26, so a
# 0.2 kg parcel costs about 26 percent more hover power.

# %%
def ideal_hover_power(thrust, radius, rho=RHO):
    """Ideal induced power (W) of one rotor of given radius (m) making a thrust (N)."""
    area = np.pi * radius ** 2
    return float(thrust) ** 1.5 / np.sqrt(2.0 * rho * area)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m, m_parcel = 1.2, 0.2
    w_h = hover_omega(m)
    print(f"weight of a {m} kg drone: {weight(m):.3f} N, per rotor {weight(m) / 4:.3f} N")
    print(f"hover speed: {w_h:.1f} rad/s = {float(rpm_from_omega(w_h)):.0f} rpm")
    print(f"thrust-to-weight at 1000 rad/s: {thrust_to_weight(m, 1000.0):.2f}")
    print(f"ideal hover power, 0.127 m rotors: {4 * ideal_hover_power(weight(m) / 4, 0.127):.1f} W")

    # Figure 1: thrust against spin speed, and the hover point for two masses
    omega = np.linspace(0, 1000, 300)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(rpm_from_omega(omega), rotor_thrust(omega), color="#1f6feb", lw=2.5, label="one rotor, T = k_T omega^2")
    for mass, col in [(m, "#2a9d8f"), (m + m_parcel, "#d9534f")]:
        t_each = weight(mass) / 4
        rpm = float(rpm_from_omega(hover_omega(mass)))
        ax.axhline(t_each, color=col, ls="--", lw=1)
        ax.plot(rpm, t_each, "o", color=col, label=f"{mass:.1f} kg hover: {t_each:.2f} N at {rpm:.0f} rpm")
    ax.set_xlabel("rotor speed (rpm)")
    ax.set_ylabel("thrust of one rotor (N)")
    ax.set_title("Thrust grows with the square of the rotor speed")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "thrust_curve.png", dpi=120)

    # Figure 2: a fixed throttle set for 1.2 kg, flown with three different real masses
    t = np.linspace(0, 2.0, 200)
    thrust = weight(m)          # the pilot set exactly the hover thrust of a 1.2 kg drone
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    for mass, col, lab in [(m - m_parcel, "#2a9d8f", "1.0 kg (lighter)"), (m, "k", "1.2 kg (as assumed)"),
                           (m + m_parcel, "#d9534f", "1.4 kg (parcel added)")]:
        z = open_loop_height(t, thrust, mass)
        ax2.plot(t, z, color=col, lw=2, label=f"{lab}: a = {vertical_acceleration(thrust, mass):+.2f} m/s^2")
        print(f"{lab}: height after 2 s = {z[-1]:+.2f} m")
    ax2.axhline(-1.0, color="#999999", ls=":", lw=1)
    ax2.text(0.05, -0.92, "1 m below start", fontsize=8, color="#666666")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("height change z (m)")
    ax2.set_title("Fixed throttle: a wrong mass means a growing height error")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8, loc="lower left")
    fig2.tight_layout()
    fig2.savefig(OUT / "open_loop_drift.png", dpi=120)
    print(f"with the parcel the drone sinks 1 m in {time_to_drop(1.0, thrust, m + m_parcel):.2f} s")

# %% [markdown]
# ## Where this stops
# A fixed throttle only works if we know the mass, the air density and the battery voltage
# exactly, and we never do. Session 2 measures the height and corrects the thrust all the
# time: feedback, with a PID controller.
