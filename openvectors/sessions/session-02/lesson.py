"""Session 2 (Level 2): components, trigonometry, the dot product, and a ferry design problem.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: components and the dot product
# **A. Real-world problem.** A ferry has speed 4 m/s in still water and must cross a 60 m wide
# river whose current is 2 m/s. Which heading lands it exactly opposite? Which heading gets it
# across fastest, and where does it land then? Both answers come from splitting arrows into
# x and y parts (components) and using sine and cosine.
#
# **Plan.** (1) components and polar form, (2) the dot product, projection and work,
# (3) the crossing equations, (4) the two design answers.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
WIDTH = 60.0     # river width (m)


# %% [markdown]
# ## Step 1: components and polar form
# An arrow of length r at angle phi from the +x axis has components
#
#     vx = r cos(phi),   vy = r sin(phi).
#
# Going back: r = sqrt(vx^2 + vy^2) and phi = atan2(vy, vx). `np.arctan2` (not `arctan`)
# picks the correct quadrant. Adding arrows means adding components.

# %%
def components(r, phi_deg):
    """(vx, vy) of an arrow of length r at angle phi_deg from the +x axis."""
    phi = np.radians(phi_deg)
    return np.array([r * np.cos(phi), r * np.sin(phi)])


def polar(vec):
    """(length, angle in degrees from the +x axis, in the range -180..180) of an arrow."""
    return float(np.hypot(vec[0], vec[1])), float(np.degrees(np.arctan2(vec[1], vec[0])))


# %% [markdown]
# ## Step 2: the dot product, projection and work
# The dot product of a = (ax, ay) and b = (bx, by) is the single number
#
#     a . b = ax bx + ay by = |a| |b| cos(angle between them).
#
# * It is 0 when the arrows are perpendicular.
# * The *projection* (shadow) of a on the direction of b has length (a . b) / |b|.
# * Work done by a constant force F over a displacement d is W = F . d, in joules when F is
#   in newtons and d in metres: only the part of the force along the motion does work.

# %%
def dot(a, b):
    return float(a[0] * b[0] + a[1] * b[1])


def angle_between(a, b):
    """Angle in degrees between two non-zero arrows."""
    c = dot(a, b) / (np.hypot(*a) * np.hypot(*b))
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))


def projection_length(a, b):
    """Signed length of the shadow of a on the direction of b."""
    return dot(a, b) / float(np.hypot(*b))


def work(force, displacement):
    """Work in joules for a force in newtons over a displacement in metres."""
    return dot(force, displacement)


# %% [markdown]
# ## Step 3: the crossing equations
# Boat heading h (degrees upstream of straight across), boat speed v, current u. The ground
# velocity has components
#
#     gx = u - v sin(h)    (along the river)      gy = v cos(h)    (across)
#
# so the crossing time is T = W / gy and the landing point (downstream drift) is gx * T.

# %%
def ground(v, u, h_deg):
    h = np.radians(h_deg)
    return np.array([u - v * np.sin(h), v * np.cos(h)])


def crossing_time(v, u, h_deg, width=WIDTH):
    gy = ground(v, u, h_deg)[1]
    if gy <= 1e-9:
        raise ValueError("no across motion: the boat never reaches the far bank")
    return float(width / gy)


def drift(v, u, h_deg, width=WIDTH):
    """Landing point along the river (m); positive = downstream of the start point."""
    return float(ground(v, u, h_deg)[0] * crossing_time(v, u, h_deg, width))


# %% [markdown]
# ## Step 4: the design answers
# * *Land exactly opposite* needs gx = 0, i.e. sin(h) = u / v. That only exists if u < v.
# * *Cross fastest* needs gy as large as possible: h = 0 (point straight across), whatever
#   the current is. The price is a drift of u W / v downstream.
# * If the current is stronger than the boat, nothing cancels the drift. The smallest drift
#   is then reached at sin(h) = v / u, and equals W sqrt(u^2 - v^2) / v.

# %%
def heading_opposite(v, u):
    """Heading in degrees that lands exactly opposite, or None if u >= v."""
    if u >= v:
        return None
    return float(np.degrees(np.arcsin(u / v)))


def heading_fastest(v, u):
    return 0.0


def smallest_drift(v, u, width=WIDTH):
    """(heading in degrees, drift in metres) with the smallest |drift| when u > v."""
    if u <= v:
        return heading_opposite(v, u), 0.0
    h = float(np.degrees(np.arcsin(v / u)))
    return h, float(width * np.sqrt(u * u - v * v) / v)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    v, u = 4.0, 2.0
    ho = heading_opposite(v, u)
    print(f"land opposite: heading {ho:.1f} deg, time {crossing_time(v, u, ho):.2f} s, drift {drift(v, u, ho):.2f} m")
    print(f"fastest      : heading 0.0 deg, time {crossing_time(v, u, 0):.2f} s, drift {drift(v, u, 0):.2f} m")
    g = ground(v, u, 0)
    F, d = np.array([20.0, 0.0]), np.array([drift(v, u, 0), WIDTH])
    print(f"ground velocity (straight) {g}, length/angle {polar(g)}")
    print(f"wind force {F} N over displacement {d.round(2)} m: work {work(F, d):.1f} J, "
          f"angle between them {angle_between(F, d):.1f} deg")

    hs = np.linspace(-20, 60, 321)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
    a1.plot(hs, [crossing_time(v, u, h) for h in hs], lw=2)
    a1.plot([0], [crossing_time(v, u, 0)], "ro")
    a1.plot([ho], [crossing_time(v, u, ho)], "gs")
    a1.set_xlabel("heading, degrees upstream of straight across")
    a1.set_ylabel("crossing time (s)")
    a1.set_title("Fastest: straight across (red). Opposite: green")
    a1.grid(alpha=0.3)
    a2.plot(hs, [drift(v, u, h) for h in hs], lw=2)
    a2.axhline(0, color="k", lw=1)
    a2.plot([0], [drift(v, u, 0)], "ro")
    a2.plot([ho], [0], "gs")
    a2.set_xlabel("heading, degrees upstream of straight across")
    a2.set_ylabel("landing point, downstream (m)")
    a2.set_title("Drift is zero at asin(u/v) = 30 degrees")
    a2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "time_and_drift.png", dpi=120)

    fig2, ax = plt.subplots(figsize=(5.5, 5))
    b = np.array([-v * np.sin(np.radians(ho)), v * np.cos(np.radians(ho))])
    c = np.array([u, 0.0])
    for start, end, col, lab in [((0, 0), b, "tab:blue", "boat arrow"), (b, b + c, "tab:orange", "current arrow"),
                                 ((0, 0), b + c, "k", "ground arrow")]:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color=col, lw=2.5))
        ax.plot([], [], color=col, lw=2.5, label=lab)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-0.5, 4.5)
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right")
    ax.set_xlabel("x: downstream (m/s)")
    ax.set_ylabel("y: across (m/s)")
    ax.set_title("Heading 30 degrees: ground arrow points straight across")
    fig2.tight_layout()
    fig2.savefig(OUT / "components_30deg.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
