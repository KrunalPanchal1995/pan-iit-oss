"""Session 1 (Level 1): position from distances to known points.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: where am I, if I know my distance to known points?
# **A. Real-world problem.** A phone does not "see" where it is. All it can learn is how far
# away some known points are (a radio signal tells it the distance). One distance says "you are
# on a circle". Two circles meet at two points. A third circle picks one. This is
# *trilateration*, the idea behind GPS. Today we do it on a flat toy map, in kilometres.
#
# **Plan.** (1) distance to a point, (2) where two circles meet, (3) let a third circle decide,
# (4) see what a ranging error does.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# three known points ("beacons") on a flat toy map, in km. Illustrative only, not real transmitters.
BEACONS = np.array([[0.0, 40.0], [120.0, 40.0], [60.0, 95.0]])


# %% [markdown]
# ## Step 1: a distance puts you on a circle
# If a beacon at B says "you are r km away", you are somewhere on the circle of radius r
# centred on B. The distance between two points is `sqrt(dx^2 + dy^2)`.

# %%
def distance(p, q):
    """Straight-line distance between two points (km)."""
    return float(np.hypot(p[0] - q[0], p[1] - q[1]))


def ranges_from(point, beacons=BEACONS):
    """The three distances a receiver at `point` would measure (km)."""
    return np.array([distance(point, b) for b in beacons])


# %% [markdown]
# ## Step 2: two circles meet at two points
# Circle 1 has centre c1 and radius r1; circle 2 has centre c2 and radius r2; d is the distance
# between the centres. Walk a = (d^2 + r1^2 - r2^2) / (2 d) from c1 towards c2, then go
# h = sqrt(r1^2 - a^2) to the left and to the right. That gives two points. If h is zero
# the circles just touch (one point); if r1^2 < a^2 they never meet.

# %%
def circle_intersections(c1, r1, c2, r2):
    """Points where two circles meet: an array with 0, 1 or 2 rows of (x, y) in km."""
    c1, c2 = np.asarray(c1, float), np.asarray(c2, float)
    d = distance(c1, c2)
    if d == 0.0:
        return np.empty((0, 2))               # same centre: no useful intersection
    a = (d * d + r1 * r1 - r2 * r2) / (2 * d)
    h2 = r1 * r1 - a * a
    if h2 < -1e-9:
        return np.empty((0, 2))               # circles do not meet
    h = np.sqrt(max(h2, 0.0))
    u = (c2 - c1) / d                         # unit vector from c1 to c2
    mid = c1 + a * u
    left = np.array([-u[1], u[0]])
    if h < 1e-9:
        return mid[None, :]
    return np.array([mid + h * left, mid - h * left])


# %% [markdown]
# ## Step 3: the third circle decides
# Of the two candidates, keep the one whose distance to beacon 3 matches the measured r3.
# `miss` is how far that match is off (km); with perfect ranges it is zero.

# %%
def locate_2d(ranges, beacons=BEACONS):
    """Return (point, miss): the candidate that best fits the third circle, and its misfit (km)."""
    cands = circle_intersections(beacons[0], ranges[0], beacons[1], ranges[1])
    if len(cands) == 0:
        return None, float("inf")
    misfits = [abs(distance(c, beacons[2]) - ranges[2]) for c in cands]
    k = int(np.argmin(misfits))
    return cands[k], float(misfits[k])


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    me = np.array([45.0, 25.0])
    r = ranges_from(me)
    print("true position", me, " ranges (km):", np.round(r, 3))
    cands = circle_intersections(BEACONS[0], r[0], BEACONS[1], r[1])
    print("two circles meet at", np.round(cands, 3).tolist())
    for c in cands:
        print("  candidate", np.round(c, 3), "distance to beacon 3 =", round(distance(c, BEACONS[2]), 3), "km; measured", round(r[2], 3))
    fix, miss = locate_2d(r)
    print("third circle picks", np.round(fix, 3), "misfit", round(miss, 6), "km")
    noisy = r + np.array([0.0, 0.0, 2.0])
    fix2, miss2 = locate_2d(noisy)
    print("with +2 km error on range 3: misfit", round(miss2, 3), "km (the circles no longer meet at one point)")

    th = np.linspace(0, 2 * np.pi, 400)
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.4), sharey=True)
    for n, ax in enumerate(axs, start=2):
        for i in range(n):
            ax.plot(BEACONS[i, 0] + r[i] * np.cos(th), BEACONS[i, 1] + r[i] * np.sin(th), lw=1.4, label=f"circle {i + 1}")
            ax.plot(*BEACONS[i], "ks")
            ax.annotate(f"B{i + 1}", BEACONS[i] + [2, 3])
        pts = cands if n == 2 else fix[None, :]
        ax.plot(pts[:, 0], pts[:, 1], "ro", ms=7)
        ax.set_title(f"{n} circles: {len(pts)} point(s)")
        ax.set_xlim(-10, 135)
        ax.set_ylim(-20, 105)
        ax.set_aspect("equal")
        ax.grid(alpha=0.3)
        ax.set_xlabel("x (km)")
        ax.legend(fontsize=8, loc="lower center")
    axs[0].set_ylabel("y (km)")
    fig.tight_layout()
    fig.savefig(OUT / "circles_meet.png", dpi=120)

    xs = np.linspace(0, 120, 200)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for i in range(3):
        ax2.plot(xs, [distance((x, me[1]), BEACONS[i]) for x in xs], label=f"distance to B{i + 1}")
    ax2.axvline(me[0], color="gray", ls=":")
    ax2.set_xlabel("receiver x (km), with y fixed at 25 km")
    ax2.set_ylabel("distance to beacon (km)")
    ax2.set_title("Each position gives its own set of three distances")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "distances_vs_x.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Real satellites are in 3D and far away, so circles become spheres, and the distances are not
# measured with a ruler but with clocks. That is Session 2.
