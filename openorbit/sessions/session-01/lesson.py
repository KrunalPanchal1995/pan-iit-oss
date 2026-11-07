"""Session 1 (Level 1): a satellite is falling around the Earth, always missing it.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: falling around the Earth
# **A. Real-world problem.** A satellite has no engine pushing it along, yet it does not drop
# out of the sky. The secret: it *is* falling, but it is moving sideways so fast that the Earth
# curves away beneath it as quickly as it falls. Today you measure that, see why higher orbits
# are slower and take longer, and meet Kepler's three laws as pictures.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
MU = 3.986004418e14      # Earth's gravitational parameter G*M, in m^3/s^2
R_EARTH = 6.371e6        # mean Earth radius, in m


# %% [markdown]
# ## Step 1: gravity gets weaker with distance
# At distance r from the centre of the Earth, gravity pulls with acceleration g(r) = mu / r^2.

# %%
def gravity(r):
    """Gravity acceleration (m/s^2) at distance r (m) from the Earth's centre."""
    return MU / r**2


# %% [markdown]
# ## Step 2: the speed that makes you miss the ground
# Fire a cannonball sideways at speed v. In time t it travels d = v t along a straight line, and
# falls a distance 0.5 g t^2. The ground, meanwhile, curves away by r - sqrt(r^2 - d^2).
# When fall and curve-away are equal, you go round forever. That speed is v = sqrt(mu / r).

# %%
def circular_speed(r):
    """Speed (m/s) of a circular orbit of radius r (m)."""
    return np.sqrt(MU / r)


def free_fall(r, t):
    """Distance (m) an object falls from rest in time t (s) at distance r (m), for small t."""
    return 0.5 * gravity(r) * t**2


def ground_curves_away(r, v, t):
    """Distance (m) that a circle of radius r drops away from a straight line travelled at speed v for t."""
    d = v * t
    return r - np.sqrt(r**2 - d**2)


def period(r):
    """Time (s) for one lap of a circular orbit of radius r (m)."""
    return 2 * np.pi * r / circular_speed(r)


# %% [markdown]
# ## Step 3: Kepler's three laws as pictures
# 1. Orbits are ellipses with the Earth at one focus (a circle is the special case).
# 2. A line from the Earth to the satellite sweeps equal areas in equal times, so the satellite
#    is fast when close and slow when far.
# 3. Orbit time grows with size: T^2 divided by a^3 is the same number for every orbit around
#    the Earth (a = half the long side of the ellipse = radius for a circle).

# %%
def radius_for_period(T):
    """Radius (m) of the circular orbit whose period is T (s): Kepler 3 solved for a."""
    return (MU * (T / (2 * np.pi)) ** 2) ** (1 / 3)


def kepler3_constant(a):
    """T^2 / a^3 (s^2/m^3) for a circular orbit of radius a; should be the same for every a."""
    return period(a) ** 2 / a**3


def apogee_speed(v_perigee, r_perigee, r_apogee):
    """Kepler's second law via angular momentum: r * v is the same at perigee and apogee."""
    return v_perigee * r_perigee / r_apogee


def area_per_second(r, v_sideways):
    """Area (m^2/s) swept by the line from the Earth to the satellite: half of r * v (sideways part)."""
    return 0.5 * r * v_sideways


def altitude_table(alts_km):
    """Rows (altitude km, speed km/s, period min)."""
    rows = []
    for h in alts_km:
        r = R_EARTH + h * 1e3
        rows.append((h, circular_speed(r) / 1e3, period(r) / 60))
    return rows


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    r = R_EARTH + 400e3
    v = circular_speed(r)
    print(f"400 km: v = {v / 1e3:.2f} km/s, period = {period(r) / 60:.1f} min, g = {gravity(r):.2f} m/s^2")
    print(f"in 1 s: falls {free_fall(r, 1):.2f} m, ground curves away {ground_curves_away(r, v, 1):.2f} m")
    rg = 42164e3
    print(f"geostationary radius: v = {circular_speed(rg) / 1e3:.2f} km/s, period = {period(rg):.0f} s")
    print(f"T^2/a^3 at 400 km / at GEO: {kepler3_constant(r) / kepler3_constant(rg):.6f}")
    r100 = radius_for_period(100 * 60)
    print(f"100 minute orbit: altitude {(r100 - R_EARTH) / 1e3:.1f} km, speed {circular_speed(r100) / 1e3:.3f} km/s")
    for row in altitude_table([200, 400, 1000, 20200, 35786]):
        print("alt %6d km  v %.2f km/s  T %.1f min" % row)

    # Figure 1: cannonball fired at different speeds (flat Earth picture is wrong; use a circle)
    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    th = np.linspace(0, 2 * np.pi, 400)
    ax.fill(R_EARTH / 1e3 * np.cos(th), R_EARTH / 1e3 * np.sin(th), color="#9ecae1")
    r0 = R_EARTH + 400e3
    for frac, col in ((0.6, "#d62728"), (0.8, "#ff7f0e"), (1.0, "#2ca02c")):
        vv = frac * circular_speed(r0)
        # two-body motion by a tiny leapfrog just for the picture
        pos = np.array([0.0, r0]); vel = np.array([vv, 0.0]); dt = 5.0; path = [pos.copy()]
        for _ in range(1200):
            vel = vel - 0.5 * dt * MU * pos / np.linalg.norm(pos) ** 3
            pos = pos + dt * vel
            vel = vel - 0.5 * dt * MU * pos / np.linalg.norm(pos) ** 3
            path.append(pos.copy())
            if np.linalg.norm(pos) < R_EARTH:
                break
        path = np.array(path) / 1e3
        ax.plot(path[:, 0], path[:, 1], color=col, label=f"{frac:.0%} of orbital speed")
    ax.set_aspect("equal"); ax.set_xlim(-8000, 8000); ax.set_ylim(-3000, 8000)
    ax.set_xlabel("x (km)"); ax.set_ylabel("y (km)"); ax.legend(fontsize=8, loc="lower right")
    ax.set_title("Fired sideways from 400 km: too slow falls, just right orbits")
    ax.grid(alpha=0.3); fig.tight_layout(); fig.savefig(OUT / "falling_around.png", dpi=120)

    # Figure 2: speed and period against altitude
    h = np.linspace(200, 40000, 300)
    rr = R_EARTH + h * 1e3
    fig2, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.8))
    a1.plot(h, circular_speed(rr) / 1e3); a1.set_xlabel("altitude (km)"); a1.set_ylabel("orbital speed (km/s)")
    a1.set_title("Higher is slower"); a1.grid(alpha=0.3)
    a2.plot(h, period(rr) / 3600); a2.set_xlabel("altitude (km)"); a2.set_ylabel("orbital period (hours)")
    a2.set_title("Higher takes longer"); a2.grid(alpha=0.3)
    fig2.tight_layout(); fig2.savefig(OUT / "speed_period_vs_altitude.png", dpi=120)
