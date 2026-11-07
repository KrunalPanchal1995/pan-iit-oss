"""Session 1 (Level 1): a light sensor and a switch that turns an LED on when it gets dark.

Low-voltage educational model only (a few volts, a few milliamps). Not a design for mains lighting.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a light switch that watches the dark
# **A. Real-world problem.** A garden path light turns itself on at dusk and off at dawn, with no
# one touching a switch. It needs a *sensor* (something that feels light), a *decision* (is it dark
# enough?) and a *switch* that powers the lamp.
#
# **Plan.** (1) the light sensor (an LDR) and how its resistance changes, (2) the decision,
# (3) the block diagram of the whole controller, (4) plot both.
#
# The numbers here come from an *assumed, illustrative* LDR curve, not from a real data sheet.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
R10 = 10_000.0     # ohm: assumed LDR resistance at 10 lux (illustrative)
GAMMA = 0.7        # assumed slope of the LDR curve on a log-log graph (illustrative)


# %% [markdown]
# ## Step 1: the LDR
# LDR = light dependent resistor. In bright light its resistance is small; in the dark it is large.
# Light is measured in *lux* (a candle-lit room is a few lux, an office about 300 lux, a sunny
# day tens of thousands). Our illustrative model:
#
#     R_ldr = R10 * (lux / 10) ** (-GAMMA)
#
# Check by hand: at 10 lux the bracket is 1, so R = 10 000 ohm. At 100 lux the bracket is 10 and
# 10 ** (-0.7) = 0.2, so R is about 2 000 ohm: ten times more light, five times less resistance.

# %%
def ldr_resistance(lux, r10=R10, gamma=GAMMA):
    """LDR resistance in ohm for a light level in lux (lux must be above 0)."""
    lux = np.asarray(lux, dtype=float)
    return r10 * (lux / 10.0) ** (-gamma)


# %% [markdown]
# ## Step 2: the decision
# The controller compares the light with a *threshold*. Below it, the LED is on.

# %%
def led_is_on(lux, threshold_lux):
    """True when it is darker than the threshold (strictly below it)."""
    return np.asarray(lux, dtype=float) < threshold_lux


# %% [markdown]
# ## Step 3: the block diagram
# Four blocks in a chain; the signal flows left to right:
#
#     LIGHT -> [ LDR + divider ] -> [ comparator ] -> [ transistor switch ] -> [ LED ]
#              "how bright?"       "dark enough?"      "power the LED"
#
# Sessions 2 and 3 turn each block into numbers.

# %%
BLOCKS = ["LDR and divider (senses light)", "comparator (decides: dark enough?)",
          "transistor switch (carries the LED current)", "LED and resistor (the lamp)"]


def describe_chain(lux, threshold_lux):
    """One line per block for a given light level, so you can follow the signal."""
    on = bool(led_is_on(lux, threshold_lux))
    r = float(ldr_resistance(lux))
    return [f"light = {lux:g} lux",
            f"LDR resistance = {r:,.0f} ohm",
            f"{lux:g} lux is {'below' if on else 'above'} the {threshold_lux:g} lux threshold",
            f"LED is {'ON' if on else 'OFF'}"]


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for lux in (1, 10, 100, 1000):
        print(f"{lux:5d} lux -> LDR {float(ldr_resistance(lux)):10,.0f} ohm")
    for line in describe_chain(5, 20):
        print(line)
    lux = np.logspace(0, 3, 200)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.loglog(lux, ldr_resistance(lux), color="tab:blue")
    ax.plot([10], [R10], "ko")
    ax.annotate("10 lux: 10 000 ohm", (10, R10), textcoords="offset points", xytext=(8, 8))
    ax.set_xlabel("light level (lux)")
    ax.set_ylabel("LDR resistance (ohm)")
    ax.set_title("Illustrative LDR: resistance falls as light rises")
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "ldr_curve.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 3.2))
    ax2.semilogx(lux, led_is_on(lux, 20).astype(float), drawstyle="steps-post", color="tab:orange")
    ax2.axvline(20, color="gray", ls=":")
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(["OFF", "ON"])
    ax2.set_xlabel("light level (lux)")
    ax2.set_ylabel("LED state")
    ax2.set_title("Threshold 20 lux: LED on only below it")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "led_state.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
