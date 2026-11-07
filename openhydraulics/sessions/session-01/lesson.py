"""Session 1 (Level 1): pressure pushes equally everywhere, so a small piston can move a big one.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a small push, a big lift
# **A. Real-world problem.** A garage jack lifts a whole car when you pump a handle with one
# hand. Where does the extra force come from? Nothing is magic: the liquid inside passes the
# *pressure* from a small piston to a big piston, and a big piston turns the same pressure
# into a bigger force.
#
# **Plan.** (1) define pressure, (2) push a small piston and find the force on a big one,
# (3) see what we pay for it (distance), (4) draw a hydraulic jack.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81                      # m/s^2, gravity
CAR_WEIGHT = 1200.0 * G       # N, weight of a 1200 kg car


# %% [markdown]
# ## Step 1: pressure
# Pressure is force spread over an area: p = F / A. Push 100 N on 0.001 m^2 and the pressure
# is 100 000 Pa (pascal, one newton per square metre). The key fact (Pascal's law): in a
# liquid that is not moving, a pressure added at one place is felt equally in all directions
# and at every point of the liquid.

# %%
def area_circle(d):
    """Area (m^2) of a round piston of diameter d (m)."""
    return np.pi * d ** 2 / 4.0


def pressure(force, area):
    """Pressure p = F / A in pascal (N and m^2 in, Pa out)."""
    return force / area


# %% [markdown]
# ## Step 2: the small piston pushes, the big piston lifts
# The liquid has one pressure p. On the small piston it equals F1 / A1; on the big piston the
# same p gives F2 = p * A2. So F2 = F1 * (A2 / A1). Doubling the diameter makes the area
# four times bigger, so the force becomes four times bigger.

# %%
def output_force(f1, d1, d2):
    """Force (N) on the big piston when f1 (N) pushes the small one (diameters d1, d2 in m)."""
    return pressure(f1, area_circle(d1)) * area_circle(d2)


def multiplier(d1, d2):
    """Force multiplier A2 / A1 = (d2 / d1)^2 (no unit)."""
    return (d2 / d1) ** 2


# %% [markdown]
# ## Step 3: what we pay (distance divides)
# The liquid cannot be squashed, so the volume that leaves the small cylinder enters the big
# one: A1 * s1 = A2 * s2. A bigger area means a smaller movement. The big piston rises by
# s2 = s1 / multiplier: force multiplies, distance divides.

# %%
def output_distance(s1, d1, d2):
    """Movement (same unit as s1) of the big piston when the small one moves s1."""
    return s1 / multiplier(d1, d2)


# %% [markdown]
# ## Step 4: see it
# Left: a hydraulic jack drawn to scale. Right: the output force against the size of the big
# piston for a 200 N push on a 2 cm piston, with the weight of a 1200 kg car as a line.

# %%
def draw_jack(ax, d1=0.02, d2=0.06, s1=0.05, f1=200.0):
    """Draw a simple two-piston jack (diameters and stroke in m) on a matplotlib axis."""
    from matplotlib.patches import Rectangle
    w1, w2 = d1 * 10.0, d2 * 10.0          # drawn widths (1 m of diameter = 10 drawing units)
    xs, xb = 0.0, 1.2                      # centres of the two cylinders
    s2 = output_distance(s1, d1, d2)
    y1 = 0.9 - s1 * 5.0                    # small piston top goes down
    y2 = 0.9 + s2 * 5.0                    # big piston top goes up
    ax.add_patch(Rectangle((xs - w1 / 2, 0.1), w1, y1 - 0.1, fc="#cfe8ff", ec="none"))
    ax.add_patch(Rectangle((xb - w2 / 2, 0.1), w2, y2 - 0.1, fc="#cfe8ff", ec="none"))
    ax.add_patch(Rectangle((xs, 0.1), xb - xs, 0.1, fc="#cfe8ff", ec="none"))
    for x, w in ((xs, w1), (xb, w2)):
        ax.plot([x - w / 2, x - w / 2, x + w / 2, x + w / 2], [1.1, 0.1, 0.1, 1.1], "k", lw=1.5)
    ax.add_patch(Rectangle((xs - w1 / 2, y1), w1, 0.06, fc="#444"))
    ax.add_patch(Rectangle((xb - w2 / 2, y2), w2, 0.06, fc="#444"))
    ax.annotate("", xy=(xs, y1 + 0.08), xytext=(xs, 1.35), arrowprops=dict(arrowstyle="->", lw=2, color="C3"))
    ax.text(xs, 1.42, f"push F1 = {f1:.0f} N", ha="center")
    ax.text(xb, y2 + 0.15, f"lifts F2 = {output_force(f1, d1, d2):.0f} N", ha="center")
    ax.text(xs, -0.05, f"small piston {d1 * 100:.0f} cm", ha="center")
    ax.text(xb, -0.05, f"big piston {d2 * 100:.0f} cm", ha="center")
    ax.set_xlim(-0.6, 1.9)
    ax.set_ylim(-0.2, 1.6)
    ax.set_aspect("equal")
    ax.axis("off")


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    f1, d1, s1 = 200.0, 0.02, 0.05
    for d2 in (0.02, 0.04, 0.06, 0.10):
        print(f"big piston {d2 * 100:4.0f} cm: pressure {pressure(f1, area_circle(d1)) / 1000:.0f} kPa, "
              f"multiplier {multiplier(d1, d2):5.1f}, force {output_force(f1, d1, d2):7.0f} N, "
              f"moves {output_distance(s1, d1, d2) * 1000:5.1f} mm for a {s1 * 100:.0f} cm push")
    fig, ax = plt.subplots(figsize=(6, 4))
    draw_jack(ax)
    ax.set_title("A hydraulic jack: small piston in, big piston out")
    fig.savefig(OUT / "jack_picture.png", dpi=120)

    d2 = np.linspace(0.02, 0.18, 200)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(d2 * 100, output_force(f1, d1, d2) / 1000, label="output force F2")
    ax2.axhline(CAR_WEIGHT / 1000, color="C3", ls="--", label="weight of a 1200 kg car")
    ax2.set_xlabel("big piston diameter (cm)")
    ax2.set_ylabel("output force (kN)")
    ax2.set_title("200 N on a 2 cm piston: force grows with diameter squared")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "force_vs_diameter.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
