"""Session 2 (Level 2): Kirchhoff's laws, dividers and a two-loop circuit.

Run:  python start.py 2
Low-voltage educational circuits only (never mains). Ideal sources and ideal resistors.
"""
# %% [markdown]
# # Session 2: Kirchhoff's two laws
# **A. Real-world problem.** A microcontroller board runs on 3.3 V but your battery pack gives
# 5 V. Two resistors can drop the voltage, but when the sensor you connect draws current the
# output sags. How do we predict the sag and design around it? And what if two batteries feed
# the same circuit: which way does the current flow?
#
# **Plan.** (1) state the current law (KCL) and voltage law (KVL), (2) dividers, (3) the loading
# effect, (4) a two-loop circuit solved with simultaneous equations, (5) a design inverse problem.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the two laws
# **KCL (current law):** at any node the currents flowing in add up to the currents flowing out
# (charge does not pile up). **KVL (voltage law):** going once around any closed loop, the
# voltage rises and drops add up to zero (energy is conserved).
#
# ## Step 2: the voltage divider
# Two resistors in series across V_in: the same current I = V_in / (R1 + R2) passes both, so
# V_out across R2 is V_in * R2 / (R1 + R2). Current divider: a total current I_t splitting into
# two parallel branches gives I1 = I_t * R2 / (R1 + R2) (the smaller resistor takes more).

# %%
def divider_out(vin, r1, r2):
    """Unloaded voltage divider: V_out across R2 (volts)."""
    if r1 < 0 or r2 <= 0:
        raise ValueError("R1 must be >= 0 and R2 > 0")
    return vin * r2 / (r1 + r2)


def current_divider(i_total, r1, r2):
    """Split a total current between two parallel resistors. Returns (i1, i2) in amperes."""
    if r1 <= 0 or r2 <= 0:
        raise ValueError("both resistors must be positive")
    return i_total * r2 / (r1 + r2), i_total * r1 / (r1 + r2)


def parallel(a, b):
    """Two resistors in parallel (ohm)."""
    return a * b / (a + b)


# %% [markdown]
# ## Step 3: the loading effect
# A load R_L connected across the output sits in parallel with R2. The lower resistor becomes
# R2 || R_L = R2 R_L / (R2 + R_L), which is smaller, so the output drops.
# Check by hand: 5 V, R1 = 1700, R2 = 3300 ohm gives 3.30 V unloaded. With R_L = 4700 ohm the
# lower part becomes 3300 || 4700 = 1938.75 ohm and V_out = 5 * 1938.75 / (1700 + 1938.75) = 2.664 V.

# %%
def loaded_out(vin, r1, r2, rl=np.inf):
    """Divider output when a load rl (ohm) is connected across R2. rl = inf means no load."""
    lower = r2 if np.isinf(rl) else parallel(r2, rl)
    return divider_out(vin, r1, lower)


def supply_current(vin, r1, r2, rl=np.inf):
    """Current drawn from the source (A)."""
    lower = r2 if np.isinf(rl) else parallel(r2, rl)
    return vin / (r1 + lower)


# %% [markdown]
# ## Step 4: a circuit with two batteries (two loops)
# Battery V1 with R1 and battery V2 with R2 both feed node A; R3 goes from A to ground (0 V).
# Let I1 and I2 flow out of the batteries towards A, so R3 carries I1 + I2. KVL on loop 1 and
# loop 2:
#     V1 = R1 I1 + R3 (I1 + I2)        ->  (R1 + R3) I1 +  R3 I2       = V1
#     V2 = R2 I2 + R3 (I1 + I2)        ->   R3 I1       + (R2 + R3) I2 = V2
# Two equations, two unknowns. By Cramer's rule: det = (R1+R3)(R2+R3) - R3^2,
# I1 = (V1 (R2+R3) - R3 V2) / det and I2 = ((R1+R3) V2 - R3 V1) / det.
# A negative current simply means the current really flows the other way.

# %%
def two_loop_by_hand(v1, v2, r1, r2, r3):
    """Closed-form (Cramer) solution. Returns (i1, i2, i3, v_a) with i3 = i1 + i2 the R3 current."""
    det = (r1 + r3) * (r2 + r3) - r3 * r3
    i1 = (v1 * (r2 + r3) - r3 * v2) / det
    i2 = ((r1 + r3) * v2 - r3 * v1) / det
    return i1, i2, i1 + i2, r3 * (i1 + i2)


def two_loop(v1, v2, r1, r2, r3):
    """The same circuit solved by numpy: A x = b with x = (I1, I2)."""
    a = np.array([[r1 + r3, r3],
                  [r3, r2 + r3]], dtype=float)
    b = np.array([v1, v2], dtype=float)
    i1, i2 = np.linalg.solve(a, b)
    return float(i1), float(i2), float(i1 + i2), float(r3 * (i1 + i2))


def kcl_residual(i1, i2, i3):
    """Currents into node A minus current out through R3 (should be 0)."""
    return i1 + i2 - i3


def kvl_residual(v1, r1, i1, v_a):
    """Loop 1 around V1, R1 and R3: rise V1 minus drop R1*I1 minus node voltage (should be 0)."""
    return v1 - r1 * i1 - v_a


# %% [markdown]
# ## Step 5: the design (inverse) problem
# We want exactly V_target at the output WITH the load connected. Choose R1, then the loaded
# lower part must be R_low = R1 V_target / (V_in - V_target), and since R_low = R2 || R_L,
# 1/R2 = 1/R_low - 1/R_L (needs R_low < R_L).

# %%
def design_r2(vin, vtarget, r1, rl):
    """R2 that gives vtarget across the load rl, given R1. Raises ValueError if impossible."""
    if not 0 < vtarget < vin:
        raise ValueError("target must lie between 0 and the input voltage")
    r_low = r1 * vtarget / (vin - vtarget)
    if r_low >= rl:
        raise ValueError("load is too heavy: even with R2 open the load alone pulls the output too low")
    return 1.0 / (1.0 / r_low - 1.0 / rl)


def stiffness_table(vin=5.0, vtarget=3.3, rl=4700.0, r1_list=(100, 220, 470, 1000, 2200)):
    """For each R1: the R2 that hits the target with the load, the supply current and the
    error if the load is removed (an unloaded divider with the same resistors)."""
    rows = []
    for r1 in r1_list:
        r2 = design_r2(vin, vtarget, r1, rl)
        rows.append((r1, r2, supply_current(vin, r1, r2, rl), divider_out(vin, r1, r2) - vtarget))
    return rows


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("loading effect, 5 V, R1 = 1700, R2 = 3300 ohm")
    for rl in (np.inf, 47000, 10000, 4700, 1000):
        print(f"  load {rl:>8} ohm -> V_out = {loaded_out(5.0, 1700, 3300, rl):.3f} V")
    print("two-loop (10 V, 4 V, 100, 200, 300 ohm): I1, I2, I3, V_A =", np.round(two_loop(10, 4, 100, 200, 300), 5))
    print("design with R1 = 1000 ohm, load 4700 ohm: R2 =", round(design_r2(5, 3.3, 1000, 4700), 1), "ohm")
    for r1, r2, i, e in stiffness_table():
        print(f"  R1 {r1:5d}  R2 {r2:8.1f}  supply {1000 * i:6.2f} mA  error without load {e:+.3f} V")

    rl = np.linspace(200, 20000, 400)
    fig, ax = plt.subplots(figsize=(6.4, 4))
    ax.plot(rl, [loaded_out(5, 1700, 3300, x) for x in rl], label="R1 = 1700, R2 = 3300 ohm")
    ax.plot(rl, [loaded_out(5, 1000, 3300, x) for x in rl], label="R1 = 1000, R2 = 3300 ohm")
    ax.axhline(3.3, color="gray", ls=":")
    ax.set_xlabel("load resistance (ohm)")
    ax.set_ylabel("output voltage (V)")
    ax.set_title("A divider sags when the load is light on resistance")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "divider_loading.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    v2 = np.linspace(-4, 12, 81)
    ax2.plot(v2, [1000 * two_loop(10, x, 100, 200, 300)[0] for x in v2], label="I1 (battery 1)")
    ax2.plot(v2, [1000 * two_loop(10, x, 100, 200, 300)[1] for x in v2], label="I2 (battery 2)")
    ax2.axhline(0, color="gray", lw=0.8)
    ax2.set_xlabel("battery 2 voltage V2 (V)")
    ax2.set_ylabel("battery current (mA)")
    ax2.set_title("Two batteries on one node (V1 = 10 V): I2 changes sign")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "two_loop_currents.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
