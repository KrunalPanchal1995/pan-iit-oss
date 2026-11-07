"""Session 1 (Level 1): a motor turns electricity into rotation, and a load slows it down.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: more load, slower motor
# **A. Real-world problem.** A small 12 V motor spins a toy wheel fast. Hang a heavy load on it
# and it slows down. Hold the shaft firmly and it stops (and gets hot). How does the speed
# depend on the load, and can we draw that as one simple picture?
#
# **Plan.** (1) learn the two numbers that describe a motor, (2) find its speed under a load,
# (3) convert between rad/s and rpm, (4) draw the torque-speed line and read it.
#
# *Low-voltage educational model only: a simplified line, not a design tool.*

# %%
import math
import pathlib

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# the example motor at 12 V
T_STALL = 0.30        # N m : torque when the shaft is held still
W_NOLOAD = 240.0      # rad/s : speed with nothing to turn


# %% [markdown]
# ## Step 1: two numbers describe the motor
# *Torque* (N m) is the twisting effort of the shaft. *Speed* is how fast it turns, in rad/s (radians
# per second) or rpm (turns per minute); one turn is 2 pi radians, so rpm = rad/s * 60 / (2 pi).
# A brushed DC motor has a useful property: its torque falls on a **straight line** from the
# **stall torque** (shaft held, speed 0) to the **no-load speed** (nothing to turn, torque 0).

# %%
def rpm(w):
    """rad/s -> revolutions per minute."""
    return w * 60.0 / (2.0 * math.pi)


def rad_per_s(n_rpm):
    """revolutions per minute -> rad/s."""
    return n_rpm * 2.0 * math.pi / 60.0


def torque_at_speed(w, t_stall=T_STALL, w_noload=W_NOLOAD):
    """Torque (N m) the motor gives at speed w (rad/s): the straight line."""
    return t_stall * (1.0 - w / w_noload)


# %% [markdown]
# ## Step 2: the operating point
# When the motor drives a steady load torque, it settles where the load meets the line. Solve
# `load = t_stall * (1 - w / w_noload)` for w, which gives `w = w_noload * (1 - load / t_stall)`.
# A load at or above the stall torque cannot be turned, so the speed is 0 (never negative).

# %%
def speed_at_load(load, t_stall=T_STALL, w_noload=W_NOLOAD):
    """Steady speed (rad/s) under a load torque (N m); 0 if the load beats the stall torque."""
    if load < 0:
        raise ValueError("load torque must be zero or positive")
    return max(0.0, w_noload * (1.0 - load / t_stall))


def mech_power(load, t_stall=T_STALL, w_noload=W_NOLOAD):
    """Mechanical power (W) delivered to the load = torque * speed."""
    return load * speed_at_load(load, t_stall, w_noload)


# %% [markdown]
# ## Step 3: the supply voltage
# More volts, more speed and more torque. In Session 2 we derive why; for now take it as a rule:
# both numbers grow in proportion to the voltage (T_STALL and W_NOLOAD above are the 12 V values).

# %%
def motor_at_voltage(volts):
    """(t_stall, w_noload) at a supply voltage, scaled from the 12 V values."""
    s = volts / 12.0
    return T_STALL * s, W_NOLOAD * s


# %% [markdown]
# ## Step 4: see it
# The line, with the operating points for three loads, and the speed-versus-load lines for three voltages.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    OUT.mkdir(exist_ok=True)
    for load in (0.06, 0.12, 0.18, 0.30, 0.35):
        w = speed_at_load(load)
        print(f"load {load:.2f} N m -> speed {w:6.1f} rad/s = {rpm(w):7.1f} rpm, power {mech_power(load):5.2f} W")
    w = np.linspace(0, W_NOLOAD, 100)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(w, torque_at_speed(w), color="tab:blue", label="motor torque (12 V)")
    for load in (0.06, 0.12, 0.18):
        ax.axhline(load, color="gray", ls=":", lw=1)
        ax.plot(speed_at_load(load), load, "o", color="tab:red")
    ax.set_xlabel("shaft speed (rad/s)")
    ax.set_ylabel("torque (N m)")
    ax.set_title("Torque-speed line: stall 0.30 N m, no-load 240 rad/s")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "torque_speed_line.png", dpi=120)

    loads = np.linspace(0, 0.30, 31)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for v in (6, 9, 12):
        ts, wn = motor_at_voltage(v)
        ax2.plot(loads, [rpm(speed_at_load(x, ts, wn)) for x in loads], label=f"{v} V")
    ax2.set_xlabel("load torque (N m)")
    ax2.set_ylabel("speed (rpm)")
    ax2.set_title("More volts shifts the line up; more load slows the motor")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "speed_vs_load.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
