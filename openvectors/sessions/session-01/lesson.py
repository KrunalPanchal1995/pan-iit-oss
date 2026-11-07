"""Session 1 (Level 1): vectors are arrows, and arrows add head to tail.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: arrows that add up
# **A. Real-world problem.** You row a boat straight at a landing on the far bank of a river.
# The water carries you sideways while you row. Where do you land? Two motions happen at once,
# and each one is an *arrow* (a vector): how fast and which way.
#
# **Plan.** (1) store an arrow as two numbers, (2) add arrows head to tail, (3) apply it to a
# boat crossing a river, (4) find the heading that lands the boat straight across.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
WIDTH = 60.0     # river width in metres (the bank-to-bank distance)


# %% [markdown]
# ## Step 1: an arrow is a pair of numbers
# We use x for "downstream, along the river" and y for "across the river, to the far bank".
# An arrow (vx, vy) says: move vx along the river and vy across, every second. Its *length*
# is the speed, its *direction* is where it points.
#
# The boat's own arrow (its velocity relative to the water) has speed `speed` and points
# `heading` degrees away from straight across. Heading 0 is straight across; a positive
# heading leans *upstream* (against the current, towards negative x).

# %%
def boat_velocity(speed, heading_deg):
    """Arrow of the boat relative to the water, in m/s. x = downstream, y = across."""
    h = np.radians(heading_deg)
    return np.array([-speed * np.sin(h), speed * np.cos(h)])


def current_velocity(current):
    """Arrow of the river current: it points downstream (+x)."""
    return np.array([current, 0.0])


def length(arrow):
    """How long the arrow is (its speed)."""
    return float(np.hypot(arrow[0], arrow[1]))


# %% [markdown]
# ## Step 2: adding arrows, head to tail
# Put the tail of the second arrow on the head of the first. The sum is the arrow from the
# very first tail to the very last head. In numbers you simply add the matching entries:
# (a_x + b_x, a_y + b_y). Order does not matter: a + b = b + a.

# %%
def add(a, b):
    return np.asarray(a, dtype=float) + np.asarray(b, dtype=float)


def ground_velocity(speed, heading_deg, current):
    """The boat's real motion over the ground = boat arrow + current arrow."""
    return add(boat_velocity(speed, heading_deg), current_velocity(current))


# %% [markdown]
# ## Step 3: where does the boat land?
# The boat crosses at the speed of the "across" part of its ground arrow. So the time is
# width / vy, and the sideways drift is vx times that time.

# %%
def crossing(speed, heading_deg, current, width=WIDTH):
    """Return (landing x in metres, crossing time in seconds). x > 0 means downstream."""
    g = ground_velocity(speed, heading_deg, current)
    if g[1] <= 1e-9:
        raise ValueError("the boat never reaches the far bank (no across motion)")
    t = width / g[1]
    return float(g[0] * t), float(t)


def heading_to_land_opposite(speed, current):
    """Heading (degrees upstream of straight across) that cancels the current.
    Returns None if the current is as fast as the boat or faster."""
    if current >= speed:
        return None
    return float(np.degrees(np.arcsin(current / speed)))


# %% [markdown]
# ## Step 4: see it
# Left: the arrows for a boat at 4 m/s in a 2 m/s current. Right: the paths over a 60 m
# river for three headings.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    v, u = 4.0, 2.0
    fig, ax = plt.subplots(figsize=(5.5, 5))
    b = boat_velocity(v, 0.0)
    c = current_velocity(u)
    g = add(b, c)
    ax.annotate("", xy=b, xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="tab:blue", lw=2.5))
    ax.annotate("", xy=g, xytext=b, arrowprops=dict(arrowstyle="->", color="tab:orange", lw=2.5))
    ax.annotate("", xy=g, xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="k", lw=2.5))
    ax.text(-1.2, 2.0, "boat\n4 m/s", color="tab:blue")
    ax.text(0.2, 4.25, "current 2 m/s", color="tab:orange")
    ax.text(1.3, 1.7, f"ground velocity\n{length(g):.2f} m/s", color="k")
    ax.set_xlim(-1.5, 3.5)
    ax.set_ylim(-0.5, 5)
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.set_xlabel("x: downstream (m/s)")
    ax.set_ylabel("y: across the river (m/s)")
    ax.set_title("Head to tail: boat arrow + current arrow")
    fig.tight_layout()
    fig.savefig(OUT / "head_to_tail.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4.5))
    for h, col in [(0, "tab:red"), (15, "tab:orange"), (heading_to_land_opposite(v, u), "tab:green")]:
        x_land, t = crossing(v, h, u)
        ax2.plot([0, x_land], [0, WIDTH], color=col, lw=2.5,
                 label=f"heading {h:.0f} deg: lands {x_land:.1f} m, {t:.1f} s")
        print(f"heading {h:5.1f} deg -> lands {x_land:6.2f} m downstream after {t:5.2f} s")
    ax2.axhline(0, color="k")
    ax2.axhline(WIDTH, color="k")
    ax2.set_xlabel("distance downstream (m)")
    ax2.set_ylabel("distance across the river (m)")
    ax2.set_title("Boat 4 m/s, current 2 m/s, river 60 m")
    ax2.legend(fontsize=8, loc="lower right")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "river_paths.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
