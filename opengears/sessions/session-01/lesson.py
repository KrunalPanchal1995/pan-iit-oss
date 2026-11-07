"""Session 1 (Level 1): two gears trade speed for torque, and an idler only flips the direction.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: two gears trade speed for torque
# **A. Real-world problem.** A bicycle, a clock, a hand drill and a car gearbox all use gears.
# Why does a small gear driving a big gear turn the big one slowly but with more twisting
# force? And why do two meshing gears turn in opposite directions?
#
# **Plan.** (1) one mesh: speed, torque and direction, (2) a chain of gears with idlers,
# (3) check that power (torque times speed) is the same going in and coming out, (4) draw a train.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: one mesh
# The teeth of two meshing gears pass the contact point one after the other, so the number of
# teeth that go past must be equal on both gears: `N_driver * w_driver = N_driven * w_driven`.
# So the driven gear turns at `w_out = w_in * N_driver / N_driven` (w = speed in rpm).
#
# For an ideal mesh (no friction) the power stays the same, so the torque goes the other way:
# `T_out = T_in * N_driven / N_driver`. The two gears turn in opposite directions; we show that
# with a minus sign. Check by hand: 20 teeth driving 60 teeth at 120 rpm and 5 N m gives
# w_out = 120 * 20 / 60 = 40 rpm and T_out = 5 * 60 / 20 = 15 N m, both with a minus sign.

# %%
def mesh(w_in, torque_in, n_driver, n_driven):
    """One ideal external mesh. Returns (w_out, torque_out); the minus sign means 'turns the other way'."""
    ratio = n_driven / n_driver
    return -w_in / ratio, -torque_in * ratio


# %% [markdown]
# ## Step 2: a chain of gears
# Gears 1, 2, ..., n in a row, each meshing with the next. A gear in the middle is called an
# *idler*: it is driven by one gear and drives the next. Every mesh flips the direction, so
# after k meshes the direction is (-1)^k. The idler's tooth count cancels out of the ratio.

# %%
def train(w_in, torque_in, teeth):
    """Speed and torque out of a row of gears with the given tooth counts (ideal)."""
    w, t = w_in, torque_in
    for n_a, n_b in zip(teeth[:-1], teeth[1:]):
        w, t = mesh(w, t, n_a, n_b)
    return w, t


def direction(k_meshes):
    """+1 if the last gear turns the same way as the first, -1 if the opposite way."""
    return (-1) ** k_meshes


def power_watts(torque_nm, w_rpm):
    """Power = torque x angular speed, with w converted from rpm to rad/s."""
    return torque_nm * w_rpm * 2 * np.pi / 60


# %% [markdown]
# ## Step 3: draw a train
# The picture needs a gear outline: a circle of radius `module * N / 2` (the pitch circle) with
# N teeth around it. The module is the tooth size in mm; two gears can only mesh if they share it.

# %%
def gear_outline(n_teeth, module, angle=0.0):
    """Closed polygon (x, y) of a simple gear with n_teeth teeth, turned by angle (radians)."""
    r = module * n_teeth / 2
    pitch = 2 * np.pi / n_teeth
    a = []
    rad = []
    for k in range(n_teeth):
        c = k * pitch
        a += [c - 0.40 * pitch, c - 0.18 * pitch, c + 0.18 * pitch, c + 0.40 * pitch]
        rad += [r - 1.25 * module, r + module, r + module, r - 1.25 * module]
    a = np.array(a) + angle
    rad = np.array(rad)
    return rad * np.cos(a), rad * np.sin(a)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m = 1.0
    teeth = [20, 30, 60]
    print("train", teeth, "->", train(120, 5, teeth))
    x = 0.0
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ang = 0.0
    centres = []
    for i, n in enumerate(teeth):
        r = m * n / 2
        if i > 0:
            x += m * teeth[i - 1] / 2 + r
            ang = np.pi - (np.pi + ang * teeth[i - 1]) / n   # tooth meets gap at the contact point
        px, py = gear_outline(n, m, ang)
        ax.fill(px + x, py, alpha=0.5, label=f"gear {i + 1}: {n} teeth")
        centres.append(x)
        ax.text(x, 0, f"{n}", ha="center", va="center")
    ax.set_aspect("equal")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title("Gear 1 drives gear 3 through an idler: ratio 3, same direction")
    fig.tight_layout()
    fig.savefig(OUT / "gear_train.png", dpi=120)

    n_driven = np.arange(10, 61)
    w_out = 120 * 20 / n_driven
    t_out = 5 * n_driven / 20
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(n_driven, w_out, label="output speed (rpm)")
    ax2.set_xlabel("teeth on the driven gear (20-tooth driver)")
    ax2.set_ylabel("output speed (rpm)")
    ax3 = ax2.twinx()
    ax3.plot(n_driven, t_out, color="tab:red", label="output torque (N m)")
    ax3.set_ylabel("output torque (N m)")
    ax2.set_title("A bigger driven gear: slower and stronger")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "speed_torque_vs_teeth.png", dpi=120)
    w, t = train(120, 5, [20, 60])
    print("mesh 20 -> 60:", w, t, "power in", round(power_watts(5, 120), 2), "out", round(power_watts(t, w), 2))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Change the tooth counts, predict the output speed and direction first, then run it. Answer the
# four questions in the README (section F), then run the checkpoint.
