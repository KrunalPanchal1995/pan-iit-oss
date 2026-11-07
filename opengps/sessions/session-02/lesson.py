"""Session 2 (Level 2): pseudoranges, linear algebra and the size of timing errors.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: distance = speed of light x travel time
# **A. Real-world problem.** A GPS satellite cannot throw a tape measure to your phone. It sends
# a radio signal stamped with the time it left. The phone notes the time it arrived. Radio
# travels at the speed of light c, so distance = c x travel time. But c is huge, so a clock error
# of one millionth of a second is a distance error of about 300 m. How do we turn such
# distances into a position, and how good must the clocks be?
#
# **Honest labels.** The satellite positions below are *toy* positions chosen for teaching.
# They are not real orbits. The Earth is a sphere of radius 6371 km.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

C = 299_792_458.0          # speed of light in vacuum (m/s), exact by definition of the metre
R_EARTH = 6_371_000.0      # mean Earth radius (m)
R_ORBIT = 26_560_000.0     # distance of the toy satellites from the Earth's centre (m), close to GPS orbit size


# %% [markdown]
# ## Step 1: time to distance, and back
# A *pseudorange* is "c x (arrival time - send time)" as the receiver's clock sees it. It is
# called *pseudo* because the clocks are not perfect, so it is not exactly the true distance.

# %%
def range_from_time(t_seconds):
    """Distance (m) travelled by a radio signal in t seconds."""
    return C * t_seconds


def time_error_to_range_error(dt_seconds):
    """Range error (m) caused by a timing error dt (s)."""
    return C * dt_seconds


def clock_accuracy_for(range_error_m):
    """Largest timing error (s) that keeps the range error within range_error_m."""
    return range_error_m / C


# %% [markdown]
# ## Step 2: subtract the equations to make them linear
# Each satellite i at position s_i gives one equation |x - s_i| = r_i, which is quadratic in x.
# Subtracting the equation of satellite 1 from satellite i cancels the |x|^2 term:
#
#     2 (s_i - s_1) . x = |s_i|^2 - |s_1|^2 - r_i^2 + r_1^2
#
# That is a straight line (2D) or plane (3D). Stack these as A x = b and solve.

# %%
def linear_system(sats, ranges):
    """Build A and b of the subtracted equations (rows = satellites 2..n)."""
    sats, ranges = np.asarray(sats, float), np.asarray(ranges, float)
    A = 2.0 * (sats[1:] - sats[0])
    b = (sats[1:] ** 2).sum(axis=1) - (sats[0] ** 2).sum() - ranges[1:] ** 2 + ranges[0] ** 2
    return A, b


def linear_fix(sats, ranges):
    """Position from exact-or-noisy ranges by the subtraction trick (least squares if over-determined)."""
    A, b = linear_system(sats, ranges)
    x, *_ = np.linalg.lstsq(A, b, rcond=None)
    return x


# %% [markdown]
# ## Step 3: toy satellites in 3D, and why three are not enough
# `toy_sats` places satellites at chosen directions (azimuth, elevation) as seen by a receiver on
# the Earth's surface, then puts each one at distance R_ORBIT from the Earth's centre.

# %%
def receiver_on_earth(lat_deg, lon_deg):
    la, lo = np.radians(lat_deg), np.radians(lon_deg)
    return R_EARTH * np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def local_axes(rec):
    """East, north and up unit vectors at the receiver."""
    up = rec / np.linalg.norm(rec)
    east = np.cross([0.0, 0.0, 1.0], up)
    east /= np.linalg.norm(east)
    return east, np.cross(up, east), up


def toy_sats(rec, az_el_deg, radius=R_ORBIT):
    """Toy satellite positions (m) in directions (azimuth, elevation) in degrees from the receiver."""
    e, n, u = local_axes(rec)
    out = []
    for az, el in az_el_deg:
        a, h = np.radians(az), np.radians(el)
        d = np.cos(h) * np.sin(a) * e + np.cos(h) * np.cos(a) * n + np.sin(h) * u
        # solve |rec + t d| = radius for the positive t
        bq = rec @ d
        t = -bq + np.sqrt(bq * bq - rec @ rec + radius * radius)
        out.append(rec + t * d)
    return np.array(out)


def three_sphere_points(sats3, ranges3):
    """The (up to) two points at the given distances from three satellites."""
    A, b = linear_system(sats3, ranges3)            # 2 equations, 3 unknowns
    x0, *_ = np.linalg.lstsq(A, b, rcond=None)      # one solution of the two planes
    n = np.cross(A[0], A[1])
    n /= np.linalg.norm(n)                          # direction along the line where the planes meet
    w = x0 - sats3[0]
    bq = w @ n
    disc = bq * bq - (w @ w - ranges3[0] ** 2)
    if disc < 0:
        return np.empty((0, 3))
    s = np.sqrt(disc)
    return np.array([x0 + (-bq + s) * n, x0 + (-bq - s) * n])


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("1 microsecond of timing error =", round(time_error_to_range_error(1e-6), 2), "m of range error")
    print("clock accuracy for a 10 m range error:", round(clock_accuracy_for(10.0) * 1e9, 2), "ns")
    print("travel time from a satellite straight overhead:", round((R_ORBIT - R_EARTH) / C * 1e3, 2), "ms")

    rec = receiver_on_earth(19.0, 73.0)
    azel = [(20, 60), (110, 35), (200, 50), (290, 25)]
    sats = toy_sats(rec, azel)
    r = np.linalg.norm(sats - rec, axis=1)
    print("toy ranges (km):", np.round(r / 1e3, 1))
    fix = linear_fix(sats, r)
    print("4 exact ranges -> position error (m):", float(np.linalg.norm(fix - rec)))
    pts = three_sphere_points(sats[:3], r[:3])
    for p in pts:
        print("3 satellites: a solution at distance from Earth's centre =", round(np.linalg.norm(p) / 1e3, 1), "km; error",
              round(float(np.linalg.norm(p - rec)) / 1e3, 1), "km")

    r_bad = r.copy()
    r_bad[0] += time_error_to_range_error(1e-6)
    print("1 us error on one range -> position error (m):", round(float(np.linalg.norm(linear_fix(sats, r_bad) - rec)), 1))
    r_off = r + time_error_to_range_error(1e-3)
    print("receiver clock 1 ms fast on all ranges -> position error (km):", round(float(np.linalg.norm(linear_fix(sats, r_off) - rec)) / 1e3, 1))

    dts = np.linspace(0, 1e-6, 21)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(dts * 1e6, time_error_to_range_error(dts), "o-", ms=3, label="range error = c x dt")
    errs = []
    for dt in dts:
        rr = r.copy()
        rr[0] += time_error_to_range_error(dt)
        errs.append(np.linalg.norm(linear_fix(sats, rr) - rec))
    ax.plot(dts * 1e6, errs, "s-", ms=3, label="position error (toy geometry)")
    ax.set_xlabel("timing error on one satellite (microseconds)")
    ax.set_ylabel("error (m)")
    ax.set_title("1 microsecond is about 300 m of range")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "timing_error.png", dpi=120)

    # two points where three spheres meet: one on the Earth, one far away
    fig2 = plt.figure(figsize=(6, 5))
    ax3 = fig2.add_subplot(projection="3d")
    u, v = np.meshgrid(np.linspace(0, 2 * np.pi, 30), np.linspace(0, np.pi, 16))
    ax3.plot_wireframe(R_EARTH * np.cos(u) * np.sin(v) / 1e6, R_EARTH * np.sin(u) * np.sin(v) / 1e6,
                       R_EARTH * np.cos(v) / 1e6, color="0.8", lw=0.4)
    ax3.scatter(*(sats[:3].T / 1e6), c="k", marker="s", label="3 toy satellites")
    ax3.scatter(*(pts.T / 1e6), c="r", s=40, label="the two solutions")
    ax3.set_xlabel("x (1000 km)")
    ax3.set_ylabel("y (1000 km)")
    ax3.set_zlabel("z (1000 km)")
    ax3.set_title("Three spheres meet at two points")
    ax3.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "three_spheres.png", dpi=120)

# %% [markdown]
# ## Where this stops
# We assumed the receiver's clock is perfect. A phone clock is a cheap quartz crystal and is off by
# far more than 1 microsecond. Session 3 treats the clock error as one more unknown.
