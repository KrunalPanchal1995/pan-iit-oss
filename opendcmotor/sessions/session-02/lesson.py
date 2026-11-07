"""Session 2 (Level 2): the brushed DC motor model, its torque-speed line, power, and a gearbox design.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the DC motor equations
# **A. Real-world problem.** You must lift a 5 kg load with a small 12 V motor and a winch drum.
# The bare motor spins fast but is weak. A gearbox trades speed for torque. Which gear ratio
# lifts the load at the speed you want without overheating the motor?
#
# **Plan.** (1) write the two motor equations, (2) derive the torque-speed line and check it
# numerically, (3) find power and efficiency, (4) add a gearbox and search for a good ratio.
#
# *Low-voltage educational model only: a simplified steady-state model, not a design tool.*

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

V0 = 12.0       # V : supply voltage
R0 = 2.0        # ohm : winding resistance
K0 = 0.05       # N m/A (= V s/rad) : motor constant
B0 = 5e-5       # N m s/rad : viscous friction


# %% [markdown]
# ## Step 1: the two equations
# *Electrical:* the supply voltage V pushes current I through the winding resistance R, and the
# spinning rotor makes a back voltage that opposes it, proportional to speed w:
# `V = I R + k_e w`.   *Mechanical:* the torque is proportional to current: `T = k_t I`.
# In SI units k_t and k_e are the same number k (V s/rad = N m/A). Why? The electrical power
# that goes into the back voltage, `k_e w I`, must come out as mechanical power `T w = k_t I w`.
# Set them equal and `k_e = k_t`.
#
# Eliminate I: `I = (V - k w) / R`, so `T = k (V - k w) / R`, a straight line in w.
# At w = 0 (stall): `T_stall = k V / R`. At T = 0: `w_noload = V / k`.

# %%
def rpm(w):
    """rad/s -> rpm."""
    return w * 60.0 / (2.0 * math.pi)


def rad_per_s(n_rpm):
    """rpm -> rad/s."""
    return n_rpm * 2.0 * math.pi / 60.0


def stall_torque(V=V0, R=R0, k=K0):
    """Torque (N m) at zero speed, ideal motor without friction."""
    return k * V / R


def no_load_speed(V=V0, k=K0):
    """Speed (rad/s) at zero torque, ideal motor without friction."""
    return V / k


def current_at_speed(w, V=V0, R=R0, k=K0):
    """Winding current (A) at speed w (rad/s): I = (V - k w) / R."""
    return (V - k * w) / R


def shaft_torque(w, V=V0, R=R0, k=K0, b=0.0):
    """Torque (N m) at the shaft: k I minus viscous friction b w."""
    return k * current_at_speed(w, V, R, k) - b * w


# %% [markdown]
# ## Step 2: verify the line numerically
# Do not just trust the algebra: solve the electrical equation at many speeds, compute
# T = k I each time, fit a straight line, and compare with the formulas.

# %%
def numeric_line(V=V0, R=R0, k=K0, n=200):
    """Fit T against w using the equations only; returns (stall torque, no-load speed, max error)."""
    w = np.linspace(0.0, V / k, n)
    T = k * ((V - k * w) / R)
    slope, icpt = np.polyfit(w, T, 1)
    err = float(np.max(np.abs(T - (icpt + slope * w))))
    return float(icpt), float(-icpt / slope), err


# %% [markdown]
# ## Step 3: power and efficiency
# Electrical input power is `P_in = V I`. Mechanical output is `P_out = T w`. For the ideal motor
# `P_out / P_in = k I w / (V I) = k w / V = w / w_noload`: efficiency is just the speed fraction.
# Power `T w = T_stall (1 - w/w_noload) w` is a parabola with its top at **half the no-load
# speed**, where `P_max = T_stall w_noload / 4`. With friction `b`, the line becomes
# `T = T0 - a w` with `a = k^2/R + b`, the top moves to half the friction-reduced no-load speed
# `T0 / a`, and the efficiency there drops **below 50 percent**.

# %%
def line_parameters(V=V0, R=R0, k=K0, b=0.0):
    """(T0, a, w0): shaft torque T = T0 - a w, with a = k^2/R + b and w0 = T0 / a."""
    T0 = k * V / R
    a = k * k / R + b
    return T0, a, T0 / a


def mech_power(w, V=V0, R=R0, k=K0, b=0.0):
    """Shaft power (W) = shaft torque * speed."""
    return shaft_torque(w, V, R, k, b) * w


def efficiency(w, V=V0, R=R0, k=K0, b=0.0):
    """Shaft power divided by electrical input power V I (needs I > 0)."""
    I = current_at_speed(w, V, R, k)
    return mech_power(w, V, R, k, b) / (V * I)


def peak_power(V=V0, R=R0, k=K0, b=0.0):
    """(speed of peak power, peak power) = (w0 / 2, T0 w0 / 4)."""
    T0, a, w0 = line_parameters(V, R, k, b)
    return w0 / 2.0, T0 * w0 / 4.0


# %% [markdown]
# ## Step 4: add a gearbox and design
# A gearbox with ratio N and efficiency eta multiplies torque and divides speed:
# `T_out = N eta T_motor`, `w_out = w_motor / N`. A steady output load `T_load` needs motor
# torque `T_m = T_load / (N eta)`; the motor then runs at the speed where its line gives T_m.

# %%
def operating_point(T_load, N, V=V0, R=R0, k=K0, b=B0, eta=0.9):
    """Steady state with a gearbox: returns dict of motor speed, output speed, current, efficiency."""
    T_m = T_load / (N * eta)
    T0, a, w0 = line_parameters(V, R, k, b)
    w_m = (T0 - T_m) / a
    if w_m <= 0:
        return {"w_motor": 0.0, "w_out": 0.0, "current": V / R, "eff": 0.0, "moves": False}
    I = current_at_speed(w_m, V, R, k)
    return {"w_motor": w_m, "w_out": w_m / N, "current": I, "eff": T_load * (w_m / N) / (V * I), "moves": True}


def choose_ratio(T_load, w_need, I_max, ratios, V=V0, R=R0, k=K0, b=B0, eta=0.9):
    """Best ratio from a list: must reach w_need (rad/s) with current <= I_max (A); highest efficiency wins.
    Returns (ratio, operating point) or (None, None) if no ratio qualifies."""
    best = (None, None)
    for N in ratios:
        op = operating_point(T_load, N, V, R, k, b, eta)
        if op["moves"] and op["w_out"] >= w_need and op["current"] <= I_max:
            if best[0] is None or op["eff"] > best[1]["eff"]:
                best = (N, op)
    return best


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"stall torque {stall_torque():.3f} N m, no-load speed {no_load_speed():.1f} rad/s = {rpm(no_load_speed()):.0f} rpm")
    print("stall current", V0 / R0, "A")
    T0n, w0n, err = numeric_line()
    print(f"numeric fit: stall {T0n:.4f} N m, no-load {w0n:.2f} rad/s, max error {err:.1e}")
    T0, a, w0 = line_parameters(b=B0)
    print(f"with friction: T0 {T0:.3f}, no-load {w0:.1f} rad/s, slope a {a:.5f} N m s/rad")
    wp, Pp = peak_power()
    print(f"ideal peak power {Pp:.2f} W at {wp:.1f} rad/s, efficiency there {efficiency(wp):.3f}")
    wp, Pp = peak_power(b=B0)
    print(f"with friction peak {Pp:.2f} W at {wp:.1f} rad/s, efficiency there {efficiency(wp, b=B0):.3f}, current {current_at_speed(wp):.2f} A")
    T_load = 5.0 * 9.81 * 0.02      # 5 kg on a 2 cm radius drum
    print(f"load torque at drum {T_load:.3f} N m; need drum speed 5 rad/s")
    for N in (10, 15, 21, 30, 40, 50):
        op = operating_point(T_load, N)
        print(f"N={N:2d}: out {op['w_out']:5.2f} rad/s, current {op['current']:.2f} A, efficiency {op['eff']:.3f}")
    ratios = list(range(5, 61))
    ok = [N for N in ratios if operating_point(T_load, N)["moves"] and operating_point(T_load, N)["w_out"] >= 5.0
          and operating_point(T_load, N)["current"] <= 1.5]
    best, op = choose_ratio(T_load, 5.0, 1.5, ratios)
    print("allowed ratios:", ok[0], "to", ok[-1], "; best ratio", best, f"efficiency {op['eff']:.3f}")

    w = np.linspace(0, w0 - 1e-6, 200)
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(w, shaft_torque(w, b=B0), color="tab:blue")
    ax[0].set_xlabel("shaft speed (rad/s)")
    ax[0].set_ylabel("shaft torque (N m)")
    ax[0].set_title("Torque-speed line (12 V, with friction)")
    ax[0].grid(alpha=0.3)
    ax[1].plot(w, mech_power(w, b=B0), color="tab:red", label="shaft power (W)")
    ax[1].set_xlabel("shaft speed (rad/s)")
    ax[1].set_ylabel("shaft power (W)")
    ax[1].set_title("Power peaks at half the no-load speed")
    ax[1].grid(alpha=0.3)
    ax_e = ax[1].twinx()
    ax_e.plot(w[1:], 100 * efficiency(w[1:], b=B0), color="tab:green", label="efficiency (%)")
    ax_e.set_ylabel("efficiency (%)")
    ax[1].legend(loc="upper left", fontsize=8)
    ax_e.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "curve_and_power.png", dpi=120)

    Ns = np.array(ratios)
    ops = [operating_point(T_load, int(N)) for N in Ns]
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(Ns, [o["w_out"] for o in ops], color="tab:blue", label="output speed (rad/s)")
    ax2.axhline(5.0, color="tab:blue", ls="--", lw=1, label="required 5 rad/s")
    ax2.plot(Ns, [o["current"] for o in ops], color="tab:green", label="current (A)")
    ax2.axhline(1.5, color="tab:green", ls=":", label="current limit 1.5 A")
    ax2.axvspan(ok[0], ok[-1], color="gray", alpha=0.15)
    ax2.set_xlabel("gear ratio N")
    ax2.set_ylabel("output speed (rad/s) or current (A)")
    ax2.set_title("Gear-ratio window for the winch (shaded)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "gear_window.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
