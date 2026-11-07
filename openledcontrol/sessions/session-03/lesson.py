"""Session 3 (Level 3): simulate the whole controller over a day, with and without hysteresis.

Low-voltage educational model only. The light curve and the LDR are synthetic and illustrative.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a day in the life of the controller
# **A. Real-world problem.** At dusk the light does not fall smoothly: clouds, trees and passing cars
# make it wobble. A comparator with a single threshold then flips the LED on and off, on and off,
# as the noisy light crosses the threshold. That *chatter* wears relays and annoys people. The cure
# is a *Schmitt trigger*: two thresholds, so once the LED is on it needs clearly more light to turn
# off. Today you simulate 24 hours, count the flips, check the thresholds against hand calculation,
# test how component tolerances move the trip point, and build the logic for a two-condition alarm.

# %%
import itertools
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
VCC = 5.0          # V
R10 = 10_000.0     # ohm, assumed LDR resistance at 10 lux (illustrative)
GAMMA = 0.7        # assumed LDR slope (illustrative)
R_FIXED = 6800.0   # ohm, divider resistor from Session 2
R_LED = 330.0      # ohm, LED resistor from Session 2
VF = 2.0           # V, typical red LED forward voltage (typical)
VCE_SAT = 0.2      # V, typical saturated transistor (typical)
R_BASE = 4700.0    # ohm, base resistor from Session 2
VBE = 0.7          # V, typical
V_LO, V_HI = 2.25, 2.75      # V, Schmitt thresholds: LED on below V_LO, off above V_HI
DT_MIN = 1.0       # minutes per simulation step


# %% [markdown]
# ## Step 1: the sensor and the hand-calculated thresholds
# Same maths as Session 2: V = Vcc R / (R + R_ldr), and the light level at which V equals a threshold
# is lux = 10 (R10 / R_ldr) ** (1 / gamma) with R_ldr = R (Vcc - V) / V.

# %%
def ldr_resistance(lux, r10=R10, gamma=GAMMA):
    return r10 * (np.asarray(lux, dtype=float) / 10.0) ** (-gamma)


def sensor_voltage(lux, vcc=VCC, r=R_FIXED, r10=R10, gamma=GAMMA):
    r_ldr = ldr_resistance(lux, r10, gamma)
    return vcc * r / (r + r_ldr)


def lux_at_voltage(v, vcc=VCC, r=R_FIXED, r10=R10, gamma=GAMMA):
    """Light level (lux) at which the divider output is v: the hand-calculated threshold."""
    r_ldr = r * (vcc - v) / v
    return 10.0 * (r10 / r_ldr) ** (1.0 / gamma)


# %% [markdown]
# ## Step 2: a synthetic day
# The log of the light level follows a sine over 24 hours: log10(lux) = 1.3 + 3.2 sin(2 pi (t - 6) / 24).
# It crosses 20 lux at 06:00 and 18:00, peaks near 31 600 lux at noon and falls to 0.013 lux at midnight.
# Clouds are a slowly varying random factor exp(sigma * n), where n is a smoothed random number
# (AR(1), seeded so every run gives the same day).

# %%
def clean_lux(minutes):
    t = np.asarray(minutes, dtype=float) / 60.0
    return 10.0 ** (1.3 + 3.2 * np.sin(2 * np.pi * (t - 6.0) / 24.0))


def cloud_factor(n, seed, sigma=0.35, rho=0.8):
    """Seeded, smoothly varying multiplicative noise with a log-standard-deviation sigma."""
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(n)
    x = np.empty(n)
    x[0] = e[0]
    k = np.sqrt(1.0 - rho ** 2)
    for i in range(1, n):
        x[i] = rho * x[i - 1] + k * e[i]
    return np.exp(sigma * x)


def day_lux(seed=7, sigma=0.35, n=1440):
    minutes = np.arange(n) * DT_MIN
    lux = clean_lux(minutes)
    return minutes, lux * cloud_factor(n, seed, sigma) if sigma > 0 else lux


# %% [markdown]
# ## Step 3: two kinds of comparator
# * plain: the LED is on whenever V is below one threshold V_th = (V_LO + V_HI) / 2
# * Schmitt: on when V drops below V_LO; off only when V rises above V_HI; in between it keeps its state.

# %%
def plain_comparator(v, v_th=(V_LO + V_HI) / 2):
    return np.asarray(v) < v_th


def schmitt(v, v_lo=V_LO, v_hi=V_HI):
    v = np.asarray(v)
    state = np.empty(len(v), dtype=bool)
    cur = bool(v[0] < (v_lo + v_hi) / 2)
    for i, x in enumerate(v):
        if x < v_lo:
            cur = True
        elif x > v_hi:
            cur = False
        state[i] = cur
    return state


def count_switches(state):
    """Number of state changes (on to off or off to on)."""
    s = np.asarray(state, dtype=int)
    return int(np.abs(np.diff(s)).sum())


# %% [markdown]
# ## Step 4: power and on-hours
# When the LED is on the supply delivers the LED current plus the base current; always, the divider
# draws Vcc / (R + R_ldr). Energy = power times time.

# %%
def led_path_current(vcc=VCC, r_led=R_LED, vf=VF, vce_sat=VCE_SAT):
    return (vcc - vf - vce_sat) / r_led


def simulate_day(seed=7, sigma=0.35, hysteresis=True, force_on=None, force_off=None, vcc=VCC):
    """Run the controller for 24 hours. force_on / force_off: optional boolean arrays (manual override)."""
    minutes, lux = day_lux(seed, sigma)
    v = sensor_voltage(lux, vcc)
    dark = schmitt(v) if hysteresis else plain_comparator(v)
    led = dark.copy()
    if force_on is not None:
        led = led | np.asarray(force_on, dtype=bool)
    if force_off is not None:
        led = led & ~np.asarray(force_off, dtype=bool)
    i_led = led_path_current(vcc)
    i_base = (vcc - VBE) / R_BASE
    i_div = vcc / (R_FIXED + ldr_resistance(lux))
    i_supply = i_div + led * (i_led + i_base)
    hours = DT_MIN / 60.0
    return {"minutes": minutes, "lux": lux, "v": v, "dark": dark, "led": led,
            "switches": count_switches(led), "on_hours": float(led.sum() * hours),
            "energy_wh": float(np.sum(vcc * i_supply) * hours), "i_supply": i_supply}


# %% [markdown]
# ## Step 5: validate against the hand calculation
# With no clouds the light is the clean sine, so the switch-on and switch-off times can be calculated
# by solving log10(lux) = 1.3 + 3.2 sin(x) for the threshold lux. The simulation must agree to within
# one time step.

# %%
def analytic_cross_times(lux_threshold):
    """(falling-light time, rising-light time) in hours when the clean light equals lux_threshold."""
    s = (np.log10(lux_threshold) - 1.3) / 3.2
    x = np.arcsin(s)
    t_fall = 6.0 + 24.0 * (np.pi - x) / (2 * np.pi)       # evening: light falling through the level
    t_rise = 6.0 + 24.0 * x / (2 * np.pi)                  # morning: light rising through the level
    return float(t_fall % 24.0), float(t_rise % 24.0)


# %% [markdown]
# ## Step 6: Monte Carlo on tolerances
# Real parts are not exact. We draw the LDR scale R10 (assumed 20 percent standard deviation, illustrative),
# the fixed resistor (up to 5 percent either way) and the supply (4.5 to 5.5 V) and look at the trip light
# level. Two designs: a FIXED 2.5 V reference, or a reference that is a fixed fraction of the supply
# (ratiometric, Vcc / 2), for which the supply cancels.

# %%
def monte_carlo_trip(n=4000, seed=3, ratiometric=False, r10_sigma=0.20, r_tol=0.05, v_lo=4.5, v_hi=5.5):
    rng = np.random.default_rng(seed)
    r10 = R10 * (1 + r10_sigma * rng.standard_normal(n))
    r = R_FIXED * (1 + r_tol * (2 * rng.random(n) - 1))
    vcc = v_lo + (v_hi - v_lo) * rng.random(n)
    v_th = vcc / 2 if ratiometric else np.full(n, 2.5)
    r_ldr = r * (vcc - v_th) / v_th
    lux = 10.0 * (r10 / r_ldr) ** (1.0 / GAMMA)
    return lux, vcc


# %% [markdown]
# ## Step 7: a small gate simulator and the two-condition alarm
# Digital logic: signals are 0 or 1 and gates combine them. An alarm that fires when EITHER of two
# independent safety conditions is violated is OR. Build it from gates and test every input row.

# %%
GATES = {"AND": lambda a, b: a & b, "OR": lambda a, b: a | b, "NAND": lambda a, b: 1 - (a & b),
         "NOR": lambda a, b: 1 - (a | b), "XOR": lambda a, b: a ^ b, "NOT": lambda a: 1 - a}


def evaluate(netlist, inputs):
    """netlist: list of (output_name, gate, [input names]) in order. Returns all signal values."""
    sig = dict(inputs)
    for out, gate, ins in netlist:
        sig[out] = int(GATES[gate](*[sig[i] for i in ins]))
    return sig


def truth_table(netlist, input_names, output_name):
    """All 2**n rows as (input tuple, output) in counting order."""
    rows = []
    for combo in itertools.product((0, 1), repeat=len(input_names)):
        sig = evaluate(netlist, dict(zip(input_names, combo)))
        rows.append((combo, sig[output_name]))
    return rows


ALARM_OR = [("alarm", "OR", ["A", "B"])]
ALARM_NAND = [("nA", "NOT", ["A"]), ("nB", "NOT", ["B"]), ("alarm", "NAND", ["nA", "nB"])]    # De Morgan
ALARM_XOR = [("alarm", "XOR", ["A", "B"])]                                              # the wrong gate
OVERRIDE = [("keep_on", "OR", ["DARK", "FORCE_ON"]), ("n_off", "NOT", ["FORCE_OFF"]), ("led", "AND", ["keep_on", "n_off"])]


# %% [markdown]
# ## Step 8: the failure cases
# (a) no hysteresis: count the flips. (b) the transistor is not saturated: dim LED and extra heat.
# For a 100 mA lamp (R = 30 ohm) the transistor is the hot part when half on.

# %%
def unsaturated_power(r_b, r_led, beta=100.0, vcc=VCC):
    i_b = (vcc - VBE) / r_b
    i_sat = (vcc - VF - VCE_SAT) / r_led
    i_c = min(beta * i_b, i_sat)
    vce = VCE_SAT if beta * i_b >= i_sat else vcc - VF - i_c * r_led
    return i_c, vce, i_c * vce


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    lux_on, lux_off = lux_at_voltage(V_LO), lux_at_voltage(V_HI)
    print(f"hand calculation: LED on below {lux_on:.1f} lux ({V_LO} V), off above {lux_off:.1f} lux ({V_HI} V)")
    for hyst in (False, True):
        r = simulate_day(hysteresis=hyst)
        print(f"hysteresis={hyst}: {r['switches']} switches, LED on {r['on_hours']:.2f} h, energy {r['energy_wh'] * 1000:.0f} mWh")
    clean = simulate_day(sigma=0.0, hysteresis=True)
    t_on = analytic_cross_times(lux_on)[0]
    t_off = analytic_cross_times(lux_off)[1]
    print(f"clean day: analytic on at {t_on:.3f} h, off at {t_off:.3f} h, on-hours {(24 - t_on) + t_off:.3f}; "
          f"simulated on-hours {clean['on_hours']:.3f}")
    for ratio in (False, True):
        lux_mc, vcc_mc = monte_carlo_trip(ratiometric=ratio)
        p5, p50, p95 = np.percentile(lux_mc, [5, 50, 95])
        print(f"ratiometric={ratio}: trip lux 5/50/95 percentile = {p5:.1f} / {p50:.1f} / {p95:.1f}")
    for rb in (4700.0, 47000.0, 470000.0):
        ic, vce, pq = unsaturated_power(rb, 30.0)
        print(f"100 mA lamp, R_B = {rb:.0f}: I_C = {ic * 1e3:.1f} mA, V_CE = {vce:.2f} V, P = {pq * 1e3:.1f} mW")

    fig, axes = plt.subplots(3, 1, figsize=(8, 7), sharex=True)
    for hyst, ax, name in ((False, axes[1], "one threshold"), (True, axes[2], "Schmitt trigger")):
        r = simulate_day(hysteresis=hyst)
        ax.step(r["minutes"] / 60, r["led"], where="post")
        ax.set_ylabel("LED (1 = on)")
        ax.set_title(f"{name}: {r['switches']} switches in 24 h")
        ax.grid(alpha=0.3)
    r = simulate_day(hysteresis=True)
    axes[0].semilogy(r["minutes"] / 60, r["lux"], lw=0.8)
    axes[0].axhline(lux_on, color="green", ls="--", label=f"on below {lux_on:.1f} lux")
    axes[0].axhline(lux_off, color="red", ls="--", label=f"off above {lux_off:.1f} lux")
    axes[0].set_ylabel("light (lux)")
    axes[0].set_title("A cloudy synthetic day")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)
    axes[2].set_xlabel("time of day (hours)")
    fig.tight_layout()
    fig.savefig(OUT / "day_simulation.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    for ratio, label in ((False, "fixed 2.5 V reference"), (True, "reference = Vcc / 2")):
        lux_mc, _ = monte_carlo_trip(ratiometric=ratio)
        ax2.hist(np.log10(lux_mc), bins=60, alpha=0.55, label=label)
    ax2.set_xlabel("trip point, log10 of light level (lux)")
    ax2.set_ylabel("number of circuits (out of 4000)")
    ax2.set_title("Tolerance spread of the trip point")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "monte_carlo.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
