"""Session 2 (Level 2): speeds, distance from S-P, and an epicentre from three stations.

Educational only. This is not an earthquake warning or prediction tool:
earthquakes cannot be predicted.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: three circles pin down the epicentre
# **A. Real-world problem.** One station tells you only HOW FAR the quake was, not in which
# direction. Where exactly was the epicentre (the point on the ground above the source)?
#
# **Plan.** (1) where do vp and vs come from, (2) distance from the S-P time, (3) travel-time
# curves, (4) three circles meet at the epicentre (trilateration), (5) why two stations are not enough.
# We work on a flat map in kilometres. Opengps uses the same idea with satellites; openemwave
# and openoscillator cover waves and vibrations in general.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

VP, VS = 6.0, 3.5   # APPROXIMATE typical crust speeds, km/s

# a made-up network (km) and a made-up quake, so we know the right answer
STATIONS = np.array([[0.0, 0.0], [100.0, 0.0], [40.0, 90.0]])
QUAKE = np.array([60.0, 35.0])


# %% [markdown]
# ## Step 1: why vs is smaller than vp
# In a uniform elastic solid the speeds depend on how the material resists squeezing and
# shearing. The ratio depends only on Poisson's ratio nu:  vp / vs = sqrt(2 (1 - nu) / (1 - 2 nu)).
# For nu = 0.25 this is sqrt(3) = 1.732. Our 6.0 / 3.5 = 1.714 is close: real rock is not
# an ideal solid, so we keep the speeds as approximate.

# %%
def vp_vs_ratio(nu):
    """vp / vs for a uniform elastic solid with Poisson's ratio nu (0 <= nu < 0.5)."""
    nu = float(nu)
    if not 0.0 <= nu < 0.5:
        raise ValueError("Poisson's ratio must be in [0, 0.5)")
    return float(np.sqrt(2.0 * (1.0 - nu) / (1.0 - 2.0 * nu)))


# %% [markdown]
# ## Step 2: distance from the S-P time, and travel-time curves
# P arrives at tp = t0 + d / vp and S at ts = t0 + d / vs. Subtract: the unknown origin time
# t0 cancels, so  d = (ts - tp) * vp * vs / (vp - vs).

# %%
def distance_sp(ts, tp, vp=VP, vs=VS):
    """Distance (km) from the S and P arrival times (s) at one station."""
    return (np.asarray(ts, dtype=float) - np.asarray(tp, dtype=float)) * vp * vs / (vp - vs)


def travel_time_curves(d, vp=VP, vs=VS):
    """P and S travel times (s) at distances d (km): two straight lines through the origin."""
    d = np.asarray(d, dtype=float)
    return d / vp, d / vs


# %% [markdown]
# ## Step 3: three circles
# Each station gives a circle of radius r_i around it. Writing the circle equation
# (x - xi)^2 + (y - yi)^2 = ri^2 for each station and subtracting the first from the others
# cancels x^2 + y^2 and leaves STRAIGHT lines in x and y:
#     2 (xi - x1) x + 2 (yi - y1) y = r1^2 - ri^2 + xi^2 + yi^2 - x1^2 - y1^2.
# Two such lines meet in one point.

# %%
def trilaterate(stations, radii):
    """Epicentre (x, y) from >= 3 stations and their distances (km), by solving the linear system."""
    s = np.asarray(stations, dtype=float)
    r = np.asarray(radii, dtype=float)
    A = 2.0 * (s[1:] - s[0])
    b = r[0] ** 2 - r[1:] ** 2 + np.sum(s[1:] ** 2, axis=1) - np.sum(s[0] ** 2)
    if np.linalg.matrix_rank(A) < 2:
        raise ValueError("stations are on one line: the epicentre is not determined")
    return np.linalg.lstsq(A, b, rcond=None)[0]


def circle_intersections(c1, r1, c2, r2):
    """The 0, 1 or 2 points where two circles meet (list of (x, y))."""
    c1, c2 = np.asarray(c1, dtype=float), np.asarray(c2, dtype=float)
    d = float(np.linalg.norm(c2 - c1))
    if d == 0.0 or d > r1 + r2 or d < abs(r1 - r2):
        return []
    a = (r1 ** 2 - r2 ** 2 + d ** 2) / (2.0 * d)
    h2 = r1 ** 2 - a ** 2
    mid = c1 + a * (c2 - c1) / d
    if h2 <= 1e-12:
        return [(float(mid[0]), float(mid[1]))]
    h = np.sqrt(h2)
    perp = np.array([-(c2 - c1)[1], (c2 - c1)[0]]) / d
    p1, p2 = mid + h * perp, mid - h * perp
    return [(float(p1[0]), float(p1[1])), (float(p2[0]), float(p2[1]))]


def station_distances(stations, quake):
    """True distance (km) from the quake to each station."""
    return np.linalg.norm(np.asarray(stations, dtype=float) - np.asarray(quake, dtype=float), axis=1)


# %% [markdown]
# ## Step 4: see it
# Left: the three circles all pass through the epicentre. Right: the travel-time lines;
# the vertical distance between them is the S-P gap.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"vp/vs for nu = 0.25: {vp_vs_ratio(0.25):.3f}; our 6.0/3.5 = {VP / VS:.3f}")
    d_true = station_distances(STATIONS, QUAKE)
    tp, ts = travel_time_curves(d_true)
    print("true distances (km):", d_true.round(2))
    print("S-P gaps (s):", (ts - tp).round(2))
    est = trilaterate(STATIONS, distance_sp(ts, tp))
    print("recovered epicentre (km):", est.round(3), " true:", QUAKE)
    pts = circle_intersections(STATIONS[0], d_true[0], STATIONS[1], d_true[1])
    print("two stations give two points:", [tuple(round(c, 2) for c in p) for p in pts])

    fig, ax = plt.subplots(figsize=(5.6, 5.4))
    th = np.linspace(0, 2 * np.pi, 200)
    for (sx, sy), r, name in zip(STATIONS, d_true, "ABC"):
        ax.plot(sx + r * np.cos(th), sy + r * np.sin(th), lw=1, alpha=0.7)
        ax.plot([sx], [sy], "^", color="k")
        ax.annotate(f"station {name}", (sx, sy), textcoords="offset points", xytext=(5, 6))
    ax.plot(*QUAKE, "r*", ms=16, label="epicentre (true)")
    ax.plot(*pts[1], "x", color="gray", ms=10, label="mirror point from A and B only")
    ax.set_xlim(-30, 150)
    ax.set_ylim(-60, 150)
    ax.set_aspect("equal")
    ax.set_xlabel("east (km)")
    ax.set_ylabel("north (km)")
    ax.set_title("Three circles meet at the epicentre")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "three_circles.png", dpi=120)

    dd = np.linspace(0, 200, 41)
    p_t, s_t = travel_time_curves(dd)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(dd, p_t, label="P wave (6.0 km/s)")
    ax2.plot(dd, s_t, label="S wave (3.5 km/s)")
    ax2.fill_between(dd, p_t, s_t, alpha=0.15, label="S-P gap")
    ax2.set_xlabel("distance to the quake (km)")
    ax2.set_ylabel("travel time (s)")
    ax2.set_title("Travel-time curves: the gap grows with distance")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "travel_times.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
