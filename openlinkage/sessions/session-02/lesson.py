"""Session 2 (Level 2): the four-bar equations: Grashof, position, transmission angle, design.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the four-bar linkage as equations
# **A. Real-world problem.** A workshop wants a crank that turns round and round to rock an
# output arm (the rocker) through exactly 40 degrees. Which bar lengths do we choose? Three
# questions decide it: (1) can the crank turn a full circle at all (Grashof's rule), (2) where
# is every pin for a given crank angle (the position problem), and (3) does the linkage push
# the rocker well or does it jam (the transmission angle)?

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: Grashof's rule
# Name the bars: ground a, crank b, coupler c, rocker d. Let s be the shortest bar, l the
# longest, and p, q the other two. Grashof's rule: if  s + l <= p + q  then the shortest bar
# can make a full turn relative to its neighbours. The kind of motion depends on WHERE the
# shortest bar is: crank (b) gives a crank-rocker, ground (a) a double-crank, coupler (c) a
# double-rocker. If s + l > p + q no bar turns fully (triple-rocker). Equality is a
# change-point linkage that can flip at a straight-line position.

# %%
def grashof_class(a, b, c, d, tol=1e-12):
    """Return (satisfies Grashof's rule, kind of linkage) for bars ground a, crank b, coupler c, rocker d."""
    bars = [a, b, c, d]
    srt = sorted(bars)
    s, l, pq = srt[0], srt[3], srt[1] + srt[2]
    margin = pq - (s + l)                       # >= 0 means Grashof
    if abs(margin) <= tol:
        return True, "change-point"
    if margin < 0:
        return False, "triple-rocker"
    kind = {1: "crank-rocker", 0: "double-crank", 2: "double-rocker", 3: "crank-rocker (bar d is the crank)"}[bars.index(s)]
    return True, kind


# %% [markdown]
# ## Step 2: the position problem (two ways)
# **Circle-circle:** pin B is at distance c from A and d from O4 (Session 1).
# **Loop closure:** walking round the loop O2 -> A -> B -> O4 -> O2 returns to the start:
#
#     b e(t2) + c e(t3) - d e(t4) - (a, 0) = (0, 0),     e(t) = (cos t, sin t)
#
# Two equations, two unknown angles t3 (coupler) and t4 (rocker). Newton's method solves
# them from a guess. Both methods must agree.

# %%
def circle_intersections(p0, r0, p1, r1):
    """The two points at distance r0 from p0 and r1 from p1 (left of p0->p1 first)."""
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


def four_bar_joints(theta, a, b, c, d, branch=1):
    """Pins O2, A, B, O4 for crank angle theta (radians)."""
    o4 = np.array([a, 0.0])
    pa = np.array([b * np.cos(theta), b * np.sin(theta)])
    first, second = circle_intersections(pa, c, o4, d)
    return np.array([0.0, 0.0]), pa, (first if branch > 0 else second), o4


def loop_residual(theta2, theta3, theta4, a, b, c, d):
    """Loop-closure error vector b e(t2) + c e(t3) - d e(t4) - (a, 0); zero when the loop closes."""
    return np.array([b * np.cos(theta2) + c * np.cos(theta3) - d * np.cos(theta4) - a,
                     b * np.sin(theta2) + c * np.sin(theta3) - d * np.sin(theta4)])


def solve_loop_newton(theta2, guess, a, b, c, d, iters=30):
    """Newton's method on the loop equations; guess = (t3, t4). Returns (t3, t4)."""
    t3, t4 = guess
    for _ in range(iters):
        f = loop_residual(theta2, t3, t4, a, b, c, d)
        jac = np.array([[-c * np.sin(t3), d * np.sin(t4)],
                        [c * np.cos(t3), -d * np.cos(t4)]])
        step = np.linalg.solve(jac, -f)
        t3, t4 = t3 + step[0], t4 + step[1]
        if np.hypot(*step) < 1e-15:
            break
    return t3, t4


def crank_turns_fully(a, b, c, d, n=720):
    """True if the pins can be placed for every one of n crank angles around a full turn."""
    for t in np.linspace(0.0, 2 * np.pi, n, endpoint=False):
        try:
            four_bar_joints(t, a, b, c, d)
        except ValueError:
            return False
    return True


# %% [markdown]
# ## Step 3: the transmission angle
# At pin B the coupler pushes on the rocker. The transmission angle mu is the angle between
# the coupler and the rocker there. At mu = 90 degrees all of the push turns the rocker. Near
# 0 or 180 degrees most of the push squeezes the pin and the linkage can jam. A common
# design guideline keeps mu between about 40 and 140 degrees (a rule of thumb, not a law).
# With D the distance from A to O4:   cos(mu) = (c^2 + d^2 - D^2) / (2 c d).

# %%
def transmission_angle(joints):
    """Angle in degrees between the coupler and the rocker at pin B."""
    _, pa, pb, o4 = joints
    u, w = pa - pb, o4 - pb
    cosmu = np.dot(u, w) / (np.linalg.norm(u) * np.linalg.norm(w))
    return float(np.degrees(np.arccos(np.clip(cosmu, -1.0, 1.0))))


def transmission_range(a, b, c, d, n=720):
    """(smallest, largest) transmission angle over a full crank turn."""
    mus = [transmission_angle(four_bar_joints(t, a, b, c, d)) for t in np.linspace(0, 2 * np.pi, n, endpoint=False)]
    return min(mus), max(mus)


# %% [markdown]
# ## Step 4: swing of the rocker and the design problem
# The rocker reaches its extremes when crank and coupler are in one line, so |O2 B| = c + b or
# c - b. The law of cosines gives the rocker angle at each extreme (measured from the ground
# line at O4), and the swing is their difference. To DESIGN, fix a, c, d and search for the
# crank length b that gives the wanted swing (the swing grows with b, so bisection works).

# %%
def rocker_swing(a, b, c, d):
    """Swing of the rocker in degrees from the two collinear positions of crank and coupler."""
    def corner(r):
        return np.degrees(np.arccos(np.clip((a * a + d * d - r * r) / (2 * a * d), -1.0, 1.0)))
    return float(abs(corner(c + b) - corner(c - b)))


def design_crank(a, c, d, target_deg, lo=1e-6, hi=None, iters=100):
    """Crank length b (bisection) so that the rocker swings through target_deg degrees."""
    hi = c - 1e-6 if hi is None else hi
    if rocker_swing(a, hi, c, d) < target_deg or rocker_swing(a, lo, c, d) > target_deg:
        raise ValueError("no crank length gives this swing")
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if rocker_swing(a, mid, c, d) < target_deg:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# %% [markdown]
# ## Step 5: see it
# Left: transmission angle against crank angle for two rocker lengths that both swing 40
# degrees; the guideline band is shaded. Right: the five example linkages checked by brute force.

# %%
EXAMPLES = [("crank-rocker", (4, 1, 4, 5)), ("double-crank", (1, 3, 3.5, 3)), ("double-rocker", (4, 3, 1, 3.5)),
            ("triple-rocker", (3, 4, 5, 7)), ("change-point", (2, 1, 2, 1))]

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for name, bars in EXAMPLES:
        ok, kind = grashof_class(*bars)
        srt = sorted(bars)
        print(f"{str(bars):18s} s+l = {srt[0] + srt[3]:4.1f}, p+q = {srt[1] + srt[2]:4.1f} -> Grashof {ok}, "
              f"{kind}; crank turns fully (brute force): {crank_turns_fully(*bars)}")
    a, c = 4.0, 4.0
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.axhspan(40, 140, color="tab:green", alpha=0.12, label="40 to 140 degrees guideline")
    ts = np.linspace(0, 360, 361)
    for d, col in ((5.0, "tab:red"), (3.5, "tab:blue")):
        b = design_crank(a, c, d, 40.0)
        mus = [transmission_angle(four_bar_joints(np.radians(t), a, b, c, d)) for t in ts]
        lo, hi = transmission_range(a, b, c, d)
        print(f"rocker d = {d}: crank b = {b:.4f} gives a 40 degree swing; mu from {lo:.2f} to {hi:.2f} degrees")
        ax.plot(ts, mus, color=col, label=f"d = {d}, b = {b:.3f}")
    ax.set_xlabel("crank angle (degrees)")
    ax.set_ylabel("transmission angle (degrees)")
    ax.set_ylim(0, 180)
    ax.set_title("Same 40 degree swing, different transmission angle")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "transmission_angle.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(5.6, 5.0))
    for deg, col in ((0, "tab:blue"), (90, "tab:green"), (180, "tab:orange"), (270, "tab:red")):
        o2, pa, pb, o4 = four_bar_joints(np.radians(deg), 4.0, 1.0, 4.0, 5.0)
        ax2.plot([o2[0], pa[0], pb[0], o4[0]], [o2[1], pa[1], pb[1], o4[1]], "o-", color=col, label=f"{deg} deg")
    ax2.set_aspect("equal")
    ax2.grid(alpha=0.3)
    ax2.set_xlabel("x (length units)")
    ax2.set_ylabel("y (length units)")
    ax2.set_title("Crank-rocker (4, 1, 4, 5) in four poses")
    ax2.legend(fontsize=8, title="crank angle")
    fig2.tight_layout()
    fig2.savefig(OUT / "crank_rocker_poses.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
