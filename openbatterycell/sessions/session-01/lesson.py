"""Session 1 (Level 1): two metals make a battery cell.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: two metals make a battery cell
# **A. Real-world problem.** Push a zinc nail and a copper coin into a lemon and wire them to a
# tiny meter: the meter shows a voltage. Nothing was plugged in. Where does the voltage come
# from? The answer is not the lemon. It is the two different metals: one metal gives up its
# electrons more eagerly than the other.
#
# **Plan.** (1) put the metals on an "eagerness ladder", (2) turn a pair of metals into a cell
# voltage, (3) stack cells in series to reach a target voltage, (4) draw the picture of
# electrons and ions.
#
# *Safety: this is an educational model. Never short-circuit or open real batteries.*

# %%
import math
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the eagerness ladder
# Chemists measure how eagerly a metal wants to *keep* its electrons with a number called the
# **standard electrode potential**, in volts (V), measured against a reference called the
# standard hydrogen electrode (defined as 0 V). A more negative number means the metal gives
# up electrons more easily. These are well-known textbook values at 25 C:

# %%
E_STD = {              # volts, reduction potential at 25 C, 1 mol/L solutions
    "Li": -3.04,       # Li+ + e-  -> Li
    "Zn": -0.76,       # Zn2+ + 2e- -> Zn
    "Fe": -0.44,       # Fe2+ + 2e- -> Fe
    "H": 0.00,         # standard hydrogen electrode (reference)
    "Cu": 0.34,        # Cu2+ + 2e- -> Cu
    "Ag": 0.80,        # Ag+ + e-  -> Ag
}


# %% [markdown]
# ## Step 2: two metals give a voltage
# Put two different metals in contact through a wire and a salt bridge. The metal lower on the
# ladder (the **anode**) pushes electrons into the wire. The metal higher on the ladder (the
# **cathode**) pulls them in. The voltage of the cell is the height difference:
#
#     cell voltage = E(cathode) - E(anode)
#
# Zinc and copper: 0.34 - (-0.76) = 1.10 V. That is the Daniell cell.

# %%
def cell_voltage(e_cathode, e_anode):
    """Cell voltage in volts. Negative means you named the electrodes the wrong way round."""
    return round(float(e_cathode) - float(e_anode), 6)


def electron_direction(e_cathode, e_anode):
    """Where do the electrons travel in the outside wire?"""
    v = cell_voltage(e_cathode, e_anode)
    if v > 0:
        return "anode to cathode"
    if v < 0:
        return "cathode to anode (swap the labels)"
    return "no flow (same metal on both sides)"


def best_pair(table=E_STD):
    """The pair of listed metals with the largest cell voltage: (anode, cathode, volts)."""
    names = list(table)
    best = None
    for a in names:
        for c in names:
            v = cell_voltage(table[c], table[a])
            if best is None or v > best[2]:
                best = (a, c, v)
    return best


# %% [markdown]
# ## Step 3: stacking cells
# One cell is only about a volt. To get more, connect cells in a row so that the voltages add
# ("series"). The number of cells needed for a target voltage is the target divided by one
# cell, **rounded up**, because you cannot build half a cell.

# %%
def series_voltage(v_cell, n_cells):
    return v_cell * n_cells


def cells_needed(v_target, v_cell):
    """Smallest whole number of series cells whose total voltage reaches v_target."""
    if v_cell <= 0:
        raise ValueError("cell voltage must be positive")
    return max(1, math.ceil(v_target / v_cell - 1e-9))   # 1e-9 protects exact multiples


# %% [markdown]
# ## Step 4: what moves inside?
# * **Wire:** electrons flow from the zinc to the copper.
# * **Zinc side:** zinc atoms leave the rod as Zn2+ ions (each leaves 2 electrons behind).
# * **Copper side:** Cu2+ ions from the solution take 2 electrons and stick to the rod as copper.
# * **Salt bridge:** charged ions drift through it so that neither beaker builds up charge.
#
# The picture below is drawn by the code. Notice that electrons travel through the wire only
# while ions can travel through the salt bridge: break either and the current stops.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    # --- figure 1: the ladder ---
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    names = list(E_STD)
    vals = [E_STD[k] for k in names]
    cols = ["#d9534f" if v < 0 else ("#999999" if v == 0 else "#2a9d8f") for v in vals]
    ax.barh(names, vals, color=cols)
    for i, v in enumerate(vals):
        ax.text(v + (0.08 if v >= 0 else -0.08), i, f"{v:+.2f} V", va="center", ha="left" if v >= 0 else "right", fontsize=9)
    ax.set_xlim(-4.0, 1.5)
    ax.invert_yaxis()
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("standard electrode potential (V, against the hydrogen electrode)")
    ax.set_title("The eagerness ladder: more negative = gives up electrons more easily", fontsize=9)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "potential_ladder.png", dpi=120)

    # --- figure 2: the Daniell cell picture ---
    fig2, ax2 = plt.subplots(figsize=(7.2, 4.4))
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 6)
    ax2.axis("off")
    for x0, name, col in ((0.6, "Zn rod (anode)\nZn -> Zn2+ + 2 e-", "#8c92ac"), (5.6, "Cu rod (cathode)\nCu2+ + 2 e- -> Cu", "#b87333")):
        ax2.add_patch(plt.Rectangle((x0, 0.4), 3.8, 3.0, fc="#cfe8f3", ec="k"))
        ax2.add_patch(plt.Rectangle((x0 + 1.6, 1.0), 0.5, 3.9, fc=col, ec="k"))
        ax2.text(x0 + 1.9, 0.75, name, ha="center", va="center", fontsize=8)
    ax2.plot([2.5, 2.5, 7.5, 7.5], [4.9, 5.5, 5.5, 4.9], "k-", lw=1.5)
    ax2.annotate("", xy=(6.6, 5.5), xytext=(3.4, 5.5), arrowprops=dict(arrowstyle="->", color="#2a6fdb", lw=2))
    ax2.text(5.0, 5.75, "electrons (e-) in the wire: zinc to copper", ha="center", fontsize=9, color="#2a6fdb")
    ax2.add_patch(plt.Rectangle((4.2, 2.4), 1.6, 0.7, fc="#f4f1de", ec="k"))
    ax2.text(5.0, 2.75, "salt bridge", ha="center", va="center", fontsize=8)
    ax2.annotate("", xy=(5.8, 2.15), xytext=(4.2, 2.15), arrowprops=dict(arrowstyle="->", color="#d9534f"))
    ax2.text(5.0, 1.85, "negative ions drift", ha="center", fontsize=7.5, color="#d9534f")
    ax2.text(1.2, 3.0, "Zn2+ enters\nthe solution", fontsize=8)
    ax2.text(8.3, 3.0, "Cu2+ leaves\nthe solution", fontsize=8)
    ax2.set_title("Daniell cell: 0.34 - (-0.76) = 1.10 V")
    fig2.tight_layout()
    fig2.savefig(OUT / "cell_picture.png", dpi=120)

    a, c, v = best_pair()
    print(f"Daniell cell Zn/Cu: {cell_voltage(E_STD['Cu'], E_STD['Zn']):.2f} V")
    print(f"largest voltage in the table: {a} (anode) with {c} (cathode) = {v:.2f} V")
    print(f"cells of 1.10 V needed for 4.5 V: {cells_needed(4.5, 1.10)} -> {series_voltage(1.10, cells_needed(4.5, 1.10)):.2f} V")

# %% [markdown]
# ## Where this stops
# Real cells deliver less than the textbook number when current flows, and their voltage
# changes as the chemicals are used up. Session 2 turns these ideas into formulas for
# capacity and energy; Session 3 simulates a discharging cell.
