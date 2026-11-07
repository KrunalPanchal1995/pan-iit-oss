"""Session 1 (Level 1): rigid bars joined by pins, one crank turns and the others follow.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: four bars, four pins, one motion
# **A. Real-world problem.** A walking toy, a windscreen wiper and a car's suspension all move
# by rigid bars joined at pins. You turn only ONE bar (the crank), and every other bar follows
# in a fixed way. A point on the middle bar (the coupler) draws a curve. Today you build the
# simplest such machine, the four-bar linkage, and see what one turning bar controls.
#
# **Plan.** (1) place the pins with two circles, (2) check that the bars never change length,
# (3) read the swing of the output bar (the rocker), (4) trace the curve of a coupler point.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
# ground a, crank b, coupler c, rocker d (all in the same length unit); a 3-4-5 friendly example
A_LEN, B_LEN, C_LEN, D_LEN = 4.0, 1.0, 4.0, 5.0


# %% [markdown]
# ## Step 1: the pins
# The frame (ground bar) has length a, with fixed pins O2 = (0, 0) and O4 = (a, 0). The crank
# (length b) turns about O2, so its free end A is at b(cos t, sin t). To locate B, intersect a
# radius-c circle centered at A with a radius-d circle centered at O4. There are usually two
# intersections; branch=+1 selects the point on the left of the directed line from A to O4.
#
# Check by hand at t = 0: A = (1, 0), O4 = (4, 0), so they are 3 units apart. The two circle
# radii are c = 4 and d = 5. The 3-4-5 triangle places the selected intersection directly above
# A, at B = (1, 4).

# %%
def circle_intersections(p0, r0, p1, r1):
    """The two points at distance r0 from p0 and r1 from p1 (left of p0->p1 first).

    Raises ValueError if the circles do not meet. Circles that just touch give one point twice."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    v = p1 - p0
    dist = float(np.hypot(v[0], v[1]))
    if dist == 0.0:
        raise ValueError("the two circle centres coincide")
    x = (r0 * r0 - r1 * r1 + dist * dist) / (2 * dist)
    h2 = r0 * r0 - x * x
    if h2 < -1e-12 * max(r0 * r0, 1.0):
        raise ValueError("the circles do not meet: this linkage cannot be assembled here")
    h = np.sqrt(max(h2, 0.0))
    e = v / dist
    n = np.array([-e[1], e[0]])
    return p0 + x * e + h * n, p0 + x * e - h * n


def four_bar_joints(theta, a=A_LEN, b=B_LEN, c=C_LEN, d=D_LEN, branch=1):
    """Pins O2, A, B, O4 for crank angle theta (radians). branch=+1 or -1 picks the assembly."""
    o2, o4 = np.array([0.0, 0.0]), np.array([a, 0.0])
    pa = np.array([b * np.cos(theta), b * np.sin(theta)])
    first, second = circle_intersections(pa, c, o4, d)
    return o2, pa, (first if branch > 0 else second), o4


def bar_lengths(joints):
    """Lengths of the four bars: ground, crank, coupler, rocker."""
    o2, pa, pb, o4 = joints
    return np.array([np.linalg.norm(o4 - o2), np.linalg.norm(pa - o2),
                     np.linalg.norm(pb - pa), np.linalg.norm(pb - o4)])


# %% [markdown]
# ## Step 2: the rocker angle and a coupler point
# The rocker angle is the direction of the bar from O4 to B, measured from the +x axis.
# A coupler point P sits on the coupler bar, a fraction k of the way from A to B
# (k = 0.5 is the middle; k > 1 is on an extension of the bar beyond B).

# %%
def rocker_angle(theta, **kw):
    """Direction of the rocker from O4 to B, in degrees."""
    _, _, pb, o4 = four_bar_joints(theta, **kw)
    return float(np.degrees(np.arctan2(pb[1] - o4[1], pb[0] - o4[0])))


def coupler_point(theta, k=0.5, **kw):
    _, pa, pb, _ = four_bar_joints(theta, **kw)
    return pa + k * (pb - pa)


def coupler_curve(k=0.5, n=361, **kw):
    """The path of the coupler point over one full turn of the crank (n points)."""
    thetas = np.linspace(0.0, 2 * np.pi, n)
    return np.array([coupler_point(t, k=k, **kw) for t in thetas])


# %% [markdown]
# ## Step 3: how far does the rocker swing?
# The rocker is at its extreme positions when the crank and the coupler lie on one straight
# line. Then B is at distance c + b (crank and coupler folded out) or c - b (folded back)
# from O2. The law of cosines in the triangle O2, O4, B gives the angle at O4, and the swing
# is the difference of the two angles.

# %%
def rocker_swing(a=A_LEN, b=B_LEN, c=C_LEN, d=D_LEN):
    """Swing of the rocker in degrees, from the two collinear (extreme) positions."""
    def corner(r):
        return np.degrees(np.arccos((a * a + d * d - r * r) / (2 * a * d)))
    return float(abs(corner(c + b) - corner(c - b)))


# %% [markdown]
# ## Step 4: why does ONE turning bar fix everything? Count the freedom
# A free bar in a plane has 3 freedoms (x, y and a turning angle). A pin (a revolute joint)
# forces two bars to share a point, which removes 2 freedoms. Fix one bar to the ground (it
# loses all 3). For n bars (ground included) joined by j pins the number of freedoms is
#
#     M = 3 (n - 1) - 2 j        (Gruebler's count for a plane)
#
# Four bars and four pins: M = 3 * 3 - 2 * 4 = 1. One input (the crank angle) fixes the rest.

# %%
def mobility(n_bars, n_pins):
    """Freedoms of a planar linkage with n_bars bars (ground included) and n_pins pins."""
    return 3 * (n_bars - 1) - 2 * n_pins


# %% [markdown]
# ## Step 5: see it
# Left: the linkage in four poses and the curve of the coupler midpoint. Right: the rocker
# angle against the crank angle: one turn of the crank makes the rocker rock to and fro.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5.5))
    curve = coupler_curve(k=0.5)
    ax.plot(curve[:, 0], curve[:, 1], "k--", lw=1, label="path of coupler midpoint")
    for deg, col in ((0, "tab:blue"), (90, "tab:green"), (180, "tab:orange"), (270, "tab:red")):
        o2, pa, pb, o4 = four_bar_joints(np.radians(deg))
        ax.plot([o2[0], pa[0], pb[0], o4[0]], [o2[1], pa[1], pb[1], o4[1]], "o-", color=col, lw=2,
                label=f"crank at {deg} deg")
        print(f"crank {deg:3d} deg -> B at {pb.round(3)}, rocker angle {rocker_angle(np.radians(deg)):.2f} deg")
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.set_xlabel("x (length units)")
    ax.set_ylabel("y (length units)")
    ax.set_title("Four-bar linkage (a, b, c, d) = (4, 1, 4, 5)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "linkage_poses.png", dpi=120)

    deg = np.linspace(0, 360, 361)
    rock = np.array([rocker_angle(np.radians(t)) for t in deg])
    print(f"rocker swing from the sampled curve {rock.max() - rock.min():.2f} deg, "
          f"from the formula {rocker_swing():.2f} deg")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(deg, rock)
    ax2.set_xlabel("crank angle (degrees)")
    ax2.set_ylabel("rocker angle (degrees)")
    ax2.set_title(f"The rocker swings through {rocker_swing():.1f} degrees")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "rocker_vs_crank.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
