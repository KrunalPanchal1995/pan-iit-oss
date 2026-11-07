"""Session 1 (Level 1): soil pushes sideways on a wall, and the wall can slide or tip.

Run:  python start.py 1
Educational only: never use this to design or check a real wall.
"""
# %% [markdown]
# # Session 1: soil pushes, the wall must not slide or tip
# **A. Real-world problem.** A garden bed is held up by a low wall. Behind the wall the soil
# wants to spread out sideways, like a heavy crowd leaning on a fence. The push grows fast
# as the soil gets deeper. Will the wall slide away, or tip over its front edge (the toe)?
#
# **Plan.** (1) the push of the soil, (2) the weight of the wall, (3) two ratios that tell us
# whether the wall slides or tips, (4) plot them against wall height.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

SOIL_WEIGHT = 18.0      # unit weight of the soil, kN per cubic metre
PUSH_FACTOR = 1.0 / 3.0  # how much of the soil's weight turns into a sideways push (Session 2 explains)
CONCRETE = 24.0         # unit weight of concrete, kN per cubic metre
FRICTION = 0.5          # friction coefficient between the wall base and the ground


# %% [markdown]
# ## Step 1: the push of the soil
# Near the top there is little soil above, so the push is small; at the bottom it is large.
# The push on the wall back looks like a triangle. Its total (kN per metre of wall length) is
#
#     push = 0.5 * PUSH_FACTOR * SOIL_WEIGHT * H * H
#
# and it acts one third of the way up from the bottom (the centre of a triangle).
# Check by hand for H = 4 m: 0.5 * (1/3) * 18 * 16 = 48 kN per metre.

# %%
def soil_push(H):
    """Total sideways push of the soil on a wall of height H (m), in kN per metre run."""
    return 0.5 * PUSH_FACTOR * SOIL_WEIGHT * H * H


def push_height(H):
    """Height above the base at which the push acts (m)."""
    return H / 3.0


# %% [markdown]
# ## Step 2: the weight of the wall
# A simple rectangular concrete wall of width B and height H weighs
# `CONCRETE * B * H` kN per metre. It acts through the middle of the base, B/2 from the toe.

# %%
def wall_weight(B, H):
    return CONCRETE * B * H


# %% [markdown]
# ## Step 3: slide or tip?
# **Sliding.** Friction under the base can resist at most `FRICTION * weight`. The ratio
# `friction / push` says how many times stronger the wall is than the push.
# **Tipping.** About the toe, the weight tries to keep the wall down (its turning effect is
# weight * B/2) and the push tries to tip it (push * H/3). The ratio of the two turning
# effects is the tipping ratio. A ratio below 1 means the wall slides or tips; engineers want
# a good margin, at least about 1.5 for sliding and 2 for tipping.

# %%
def slide_ratio(B, H):
    return FRICTION * wall_weight(B, H) / soil_push(H)


def tip_ratio(B, H):
    return wall_weight(B, H) * B / 2.0 / (soil_push(H) * push_height(H))


# %% [markdown]
# ## Step 4: see it
# Left: the picture of the wall, the soil wedge, the push arrow and the weight arrow.
# Right: both ratios against wall height for a 2 m wide wall.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    H, B = 4.0, 2.0
    print(f"H = {H} m, B = {B} m: push = {soil_push(H):.1f} kN/m at {push_height(H):.2f} m, weight = {wall_weight(B, H):.1f} kN/m")
    print(f"sliding ratio = {slide_ratio(B, H):.2f}, tipping ratio = {tip_ratio(B, H):.2f}")
    print(f"doubling the height to 8 m: push = {soil_push(8):.0f} kN/m")

    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.fill([0, B, B, 0], [0, 0, H, H], color="#9aa5b1", label="wall (concrete)")
    ax.fill([B, B + 4, B], [0, 0, H], color="#d9b382", alpha=0.7, label="soil wedge")
    ax.fill([B, B + 4, B + 4, B], [H, H, 0, 0], color="#d9b382", alpha=0.25)
    ax.annotate("", xy=(B + 0.05, H / 3), xytext=(B + 1.6, H / 3), arrowprops=dict(arrowstyle="->", color="crimson", lw=2.5))
    ax.text(B + 1.7, H / 3, f"push {soil_push(H):.0f} kN/m", color="crimson", va="center")
    ax.annotate("", xy=(B / 2, 0.05), xytext=(B / 2, 1.4), arrowprops=dict(arrowstyle="->", color="navy", lw=2.5))
    ax.text(B / 2, 1.5, f"weight {wall_weight(B, H):.0f}", color="navy", ha="center")
    ax.set_aspect("equal")
    ax.set_xlabel("distance from the toe (m)")
    ax.set_ylabel("height above the base (m)")
    ax.set_title("Soil pushes, the wall resists")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "wall_picture.png", dpi=120)

    Hs = np.linspace(1, 8, 71)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(Hs, [slide_ratio(2.0, h) for h in Hs], label="sliding ratio")
    ax2.plot(Hs, [tip_ratio(2.0, h) for h in Hs], label="tipping ratio")
    ax2.axhline(1.0, color="red", ls="--", label="ratio = 1")
    ax2.set_xlabel("wall height H (m)")
    ax2.set_ylabel("safety ratio (no unit)")
    ax2.set_title("A taller wall of the same width is less safe (B = 2 m)")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "ratio_vs_height.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
