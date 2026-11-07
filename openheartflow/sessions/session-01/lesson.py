"""Session 1 (Level 1): the heart is a pump, the vessels are pipes.

Run:  python start.py 1
General education only: this is not medical advice and the model is not a diagnostic tool.
"""
# %% [markdown]
# # Session 1: the heart is a pump, the vessels are pipes
# **A. Real-world problem.** Your heart does not "squirt" blood through the body: it pushes
# it round a closed loop of tubes, like a pump in a central-heating system. Why is the
# pressure highest just after the heart and lowest just before it? And why does narrowing
# the small vessels make the pump work harder? Today we build the simplest model of the loop.
#
# *This is general education. It is not medical advice and the model is not a diagnostic
# tool: never use it to judge anyone's health.*
#
# **Plan.** (1) the loop: heart, arteries, small vessels (arterioles and capillaries), veins,
# (2) flow = pressure difference / resistance, (3) the pressure falls along the loop,
# (4) narrow the small vessels and see what changes.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

TPR_TYPICAL = 18.6          # mmHg per (L/min): a typical textbook total resistance (93 / 5)
SHARES = {"arteries": 0.10, "small vessels": 0.80, "veins": 0.10}   # illustrative split of the resistance


# %% [markdown]
# ## Step 1: flow = pressure difference / resistance
# A pump pushes with a pressure difference `dP` (in mmHg, millimetres of mercury, the unit
# doctors use for blood pressure). The pipes resist with a resistance `R` (mmHg per L/min).
# The flow `Q` (litres per minute) is
#
#     Q = dP / R
#
# More push gives more flow; more resistance gives less flow. It is Ohm's law for pipes.
# Typical textbook numbers: a push of 93 mmHg through 18.6 mmHg per L/min gives 5 L/min.

# %%
def flow(dP, R):
    """Flow in L/min for a pressure difference dP (mmHg) and resistance R (mmHg per L/min)."""
    if R <= 0:
        raise ValueError("resistance must be positive")
    return dP / R


# %% [markdown]
# ## Step 2: the loop has three kinds of pipe in a row
# Blood leaves the heart into the arteries, passes the small vessels (arterioles and
# capillaries, where it feeds the tissues) and returns in the veins. Pipes in a row add their
# resistances. We use an *illustrative* split: 10% in the arteries, 80% in the small vessels
# and 10% in the veins. `narrow` multiplies the resistance of the small vessels only
# (1.0 = normal, 1.5 = 50% more resistance).

# %%
def segment_resistances(narrow=1.0, tpr=TPR_TYPICAL):
    """Resistance of arteries, small vessels and veins, in mmHg per (L/min)."""
    return np.array([SHARES["arteries"] * tpr,
                     SHARES["small vessels"] * tpr * narrow,
                     SHARES["veins"] * tpr])


def total_resistance(narrow=1.0, tpr=TPR_TYPICAL):
    return float(segment_resistances(narrow, tpr).sum())


# %% [markdown]
# ## Step 3: the pressure falls along the loop
# The same flow passes every segment, so the pressure lost in a segment is `Q * R_segment`.
# Starting at the pump outlet (pressure `dP` above the return pressure, which we take as 0)
# the pressure steps down: a little in the arteries, a lot in the small vessels, a little in
# the veins, and reaches 0 back at the heart.

# %%
def pressure_profile(dP, narrow=1.0, tpr=TPR_TYPICAL):
    """Pressure (mmHg) at the start of each segment and at the end of the loop: 4 numbers."""
    R = segment_resistances(narrow, tpr)
    Q = flow(dP, R.sum())
    return np.concatenate([[dP], dP - np.cumsum(Q * R)])


def push_needed(Q_target, narrow=1.0, tpr=TPR_TYPICAL):
    """Pressure difference (mmHg) the pump must give to deliver Q_target (L/min)."""
    return Q_target * total_resistance(narrow, tpr)


# %% [markdown]
# ## Step 4: see it
# Left: the pressure along the loop for normal and for narrowed small vessels. Right: the
# flow delivered by the same pump as the small vessels narrow.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("normal: flow", round(flow(93, total_resistance()), 2), "L/min")
    print("narrow 1.5, same pump:", round(flow(93, total_resistance(1.5)), 3), "L/min")
    print("pump needed for 5 L/min at narrow 1.5:", round(push_needed(5.0, 1.5), 1), "mmHg")
    xs = [0, 1, 2, 3]
    fig, ax = plt.subplots(figsize=(6, 4))
    for narrow, col in ((1.0, "tab:blue"), (1.5, "tab:red")):
        ax.plot(xs, pressure_profile(93, narrow), "o-", color=col, label=f"narrowing x{narrow}")
    ax.set_xticks(xs)
    ax.set_xticklabels(["heart outlet", "after arteries", "after small vessels", "back at heart"], fontsize=8)
    ax.set_ylabel("pressure above return (mmHg)")
    ax.set_title("Pressure falls along the loop (pump pressure 93 mmHg)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "pressure_along_loop.png", dpi=120)

    n = np.linspace(1.0, 2.0, 41)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(n, [flow(93, total_resistance(k)) for k in n])
    ax2.axhline(5.0, color="gray", ls=":")
    ax2.set_xlabel("narrowing factor of the small vessels (1 = normal)")
    ax2.set_ylabel("flow (L/min)")
    ax2.set_title("Same pump, narrower small vessels: less flow")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "flow_vs_narrowing.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
