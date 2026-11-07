"""Session 2 (Level 2): the voltage divider, the LED resistor and the transistor switch.

Low-voltage educational model only (5 V, milliamps). Typical values are labelled as typical.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: from a light level to a switched LED, with numbers
# **A. Real-world problem.** You want a night light that comes on below a chosen light level. Which
# resistor goes with the LDR? How big is the LED resistor? What stops the transistor from running
# warm? Today every block of the Session 1 chain gets a formula.
#
# **Plan.** (1) the divider turns resistance into a voltage, (2) choose the threshold,
# (3) the LED resistor, (4) the transistor as a switch with a base resistor, (5) standard values.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
VCC = 5.0            # V, supply
R10 = 10_000.0       # ohm, assumed LDR resistance at 10 lux (illustrative)
GAMMA = 0.7          # assumed LDR slope (illustrative)
VF = 2.0             # V, typical red LED forward voltage (typical)
I_LED = 0.010        # A, typical indicator LED current (typical)
VBE = 0.7            # V, typical base-emitter voltage of a small silicon transistor (typical)
VCE_SAT = 0.2        # V, typical collector-emitter voltage when saturated (typical)
BETA = 100.0         # typical current gain of a small transistor (varies a lot from part to part)
FORCED_GAIN = 10.0   # design rule: drive the base so that I_C / I_B is only about 10
E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]


# %% [markdown]
# ## Step 1: the divider
# The fixed resistor R and the LDR sit in series across the supply. The voltage across R is
#
#     V = Vcc * R / (R + R_ldr)
#
# Bright: R_ldr small, V close to Vcc. Dark: R_ldr large, V close to 0. Check by hand with
# R = 6 800 ohm and R_ldr = 6 800 ohm (equal): V = 5 * 0.5 = 2.5 V.

# %%
def ldr_resistance(lux, r10=R10, gamma=GAMMA):
    return r10 * (np.asarray(lux, dtype=float) / 10.0) ** (-gamma)


def lux_from_resistance(r_ldr, r10=R10, gamma=GAMMA):
    """Invert the LDR curve: the light level that gives this resistance."""
    return 10.0 * (r10 / np.asarray(r_ldr, dtype=float)) ** (1.0 / gamma)


def divider_voltage(vcc, r, r_ldr):
    """Voltage across the fixed resistor r (ohm) when the LDR r_ldr (ohm) is in series."""
    return vcc * r / (r + np.asarray(r_ldr, dtype=float))


# %% [markdown]
# ## Step 2: choose the threshold
# The comparator decides "dark" when V falls below a threshold voltage V_th. At the threshold light
# level the divider gives exactly V_th, so R_ldr = R (Vcc - V_th) / V_th. With V_th = Vcc / 2 the two
# resistors are equal: R = R_ldr(threshold lux). To design, solve for R.

# %%
def trip_lux(r, v_th, vcc=VCC, r10=R10, gamma=GAMMA):
    """Light level (lux) at which the divider output equals v_th."""
    r_ldr = r * (vcc - v_th) / v_th
    return float(lux_from_resistance(r_ldr, r10, gamma))


def fixed_resistor_for(lux_threshold, v_th, vcc=VCC, r10=R10, gamma=GAMMA):
    """Fixed resistor (ohm) that puts the trip point at lux_threshold."""
    return float(ldr_resistance(lux_threshold, r10, gamma)) * v_th / (vcc - v_th)


# %% [markdown]
# ## Step 3: the LED resistor
# An LED has an almost fixed voltage Vf across it (about 2 V for red, typical). The resistor takes the
# rest of the supply: R_led = (Vcc - Vf) / I. For 10 mA from 5 V: (5 - 2) / 0.010 = 300 ohm.

# %%
def led_resistor(vcc=VCC, vf=VF, current=I_LED):
    return (vcc - vf) / current


# %% [markdown]
# ## Step 4: the transistor as a switch
# The comparator output cannot carry 10 mA, so it drives the base of an NPN transistor. The LED and its
# resistor sit in the collector path. To switch hard (*saturate*) we feed the base about I_C / 10:
#
#     I_B = I_C / 10,        R_B = (V_drive - V_BE) / I_B
#
# Real current gain varies from part to part, so we do not trust beta = 100; we use a *forced gain* of 10.
# If the base current is too small, the transistor is only half on: dim LED, and the transistor
# itself dissipates power I_C * V_CE.

# %%
def base_resistor(i_c, v_drive=VCC, vbe=VBE, forced_gain=FORCED_GAIN):
    return (v_drive - vbe) / (i_c / forced_gain)


def transistor_state(r_b, r_led, vcc=VCC, v_drive=VCC, vf=VF, beta=BETA, vbe=VBE, vce_sat=VCE_SAT):
    """Operating point of the LED switch for a base resistor r_b (ohm)."""
    i_b = max(v_drive - vbe, 0.0) / r_b
    i_sat = (vcc - vf - vce_sat) / r_led            # most current the LED path can carry
    saturated = beta * i_b >= i_sat
    i_c = i_sat if saturated else beta * i_b
    vce = vce_sat if saturated else vcc - vf - i_c * r_led
    return {"i_b": i_b, "i_c": i_c, "vce": vce, "p_q": i_c * vce, "saturated": bool(saturated),
            "forced_gain": i_c / i_b}


# %% [markdown]
# ## Step 5: standard resistor values
# Shops sell the E12 series (12 values per decade: 1.0, 1.2, 1.5, ... 8.2, then x10). We pick a real part.

# %%
def e12_pick(value, mode="nearest"):
    """Pick an E12 value: 'nearest' (in ratio), 'up' (at or above) or 'down' (at or below)."""
    decade = 10.0 ** np.floor(np.log10(value))
    cands = np.unique(np.round([m * decade for m in E12] + [10.0 * decade, 0.1 * decade * E12[-1]], 6))
    if mode == "up":
        return float(cands[cands >= value * (1 - 1e-9)].min())
    if mode == "down":
        return float(cands[cands <= value * (1 + 1e-9)].max())
    return float(cands[np.argmin(np.abs(np.log(cands / value)))])


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    # the night light design problem: switch on below 20 lux
    r_ideal = fixed_resistor_for(20.0, VCC / 2)
    print(f"R_ldr at 20 lux = {float(ldr_resistance(20.0)):.0f} ohm -> ideal R = {r_ideal:.0f} ohm")
    for rr in (5600.0, 6800.0):
        print(f"R = {rr:.0f} ohm -> trip at {trip_lux(rr, VCC / 2):.1f} lux")
    r_led = led_resistor()
    r_led_part = e12_pick(r_led, "up")
    i_c = (VCC - VF) / r_led_part
    print(f"LED resistor ideal {r_led:.0f} ohm -> part {r_led_part:.0f} ohm -> I = {i_c * 1e3:.2f} mA")
    r_b = base_resistor(i_c)
    r_b_part = e12_pick(r_b, "down")
    st = transistor_state(r_b_part, r_led_part)
    print(f"base resistor ideal {r_b:.0f} ohm -> part {r_b_part:.0f} ohm; I_B = {st['i_b'] * 1e3:.3f} mA, "
          f"I_C = {st['i_c'] * 1e3:.2f} mA, saturated = {st['saturated']}")
    weak = transistor_state(470e3, r_led_part)
    print(f"too large R_B = 470 kohm: I_C = {weak['i_c'] * 1e3:.2f} mA, V_CE = {weak['vce']:.2f} V, "
          f"transistor power = {weak['p_q'] * 1e3:.2f} mW, saturated = {weak['saturated']}")

    lux = np.logspace(0, 3, 200)
    fig, ax = plt.subplots(figsize=(6, 4))
    for rr in (3300.0, 6800.0, 15000.0):
        ax.semilogx(lux, divider_voltage(VCC, rr, ldr_resistance(lux)), label=f"R = {rr / 1000:g} kohm")
    ax.axhline(VCC / 2, color="gray", ls=":", label="threshold 2.5 V")
    ax.set_xlabel("light level (lux)")
    ax.set_ylabel("divider voltage V (volt)")
    ax.set_title("Divider output rises with light; R moves the trip point")
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "divider_voltage.png", dpi=120)

    rb = np.linspace(1000, 100000, 300)
    ic = np.array([transistor_state(x, r_led_part)["i_c"] for x in rb]) * 1e3
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(rb / 1000, ic)
    ax2.axvline(r_b_part / 1000, color="green", ls="--", label=f"chosen R_B = {r_b_part / 1000:g} kohm")
    ax2.set_xlabel("base resistor R_B (kohm)")
    ax2.set_ylabel("LED current I_C (mA)")
    ax2.set_title("Small R_B: saturated, full current. Large R_B: dim LED")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "transistor_switch.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
