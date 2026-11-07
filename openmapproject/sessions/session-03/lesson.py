"""Session 3 (Level 3): measure the distortion of any map projection with its Jacobian.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: measuring distortion with the Jacobian
# **A. Real-world problem.** Which map should a country, an airline or a school atlas use? Not
# the one that "looks nicest", but the one whose distortion suits the job. Distortion at a point
# is measured by the *Jacobian* of the map: the 2 x 2 matrix that says how a tiny square on the
# ground becomes a tiny parallelogram on the paper. Its singular values give the largest and
# smallest stretch (the Tissot ellipse), and its determinant gives the area scale.
# We compute it by finite differences for four projections and validate it against formulas
# and against the area of the sphere, 4 pi R^2.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: four projections (unit sphere, angles in radians, R = 1)
# * equirectangular: x = lon, y = lat
# * Mercator: x = lon, y = ln tan(pi/4 + lat/2)         (keeps angles)
# * sinusoidal: x = lon cos(lat), y = lat                 (keeps areas)
# * Lambert cylindrical equal-area: x = lon, y = sin(lat) (keeps areas)

# %%
def equirectangular(lat, lon):
    return lon, lat + 0 * lon


def mercator(lat, lon):
    return lon, np.log(np.tan(np.pi / 4 + lat / 2)) + 0 * lon


def sinusoidal(lat, lon):
    return lon * np.cos(lat), lat + 0 * lon


def lambert_cyl(lat, lon):
    return lon, np.sin(lat) + 0 * lon


PROJECTIONS = {"equirectangular": equirectangular, "Mercator": mercator,
               "sinusoidal": sinusoidal, "Lambert cylindrical": lambert_cyl}


# %% [markdown]
# ## Step 2: the Jacobian by finite differences
# On the sphere a step `dlat` north is `dlat` long (R = 1) and a step `dlon` east is
# `cos(lat) dlon` long. So the *local* Jacobian, from true ground length to map length, is
#
#     J = [[ dx/dlon / cos(lat),  dx/dlat ],
#          [ dy/dlon / cos(lat),  dy/dlat ]]
#
# We approximate each derivative with a central difference (f(t+h) - f(t-h)) / (2h).

# %%
def jacobian_fd(proj, lat, lon, h=1e-5):
    """2 x 2 local Jacobian of a projection at (lat, lon) in radians (central differences)."""
    if abs(lat) >= np.pi / 2 - 2 * h:
        raise ValueError("the Jacobian is not defined at the poles (cos(lat) = 0)")
    xe, ye = proj(lat, lon + h)
    xw, yw = proj(lat, lon - h)
    xn, yn = proj(lat + h, lon)
    xs, ys = proj(lat - h, lon)
    c = np.cos(lat)
    return np.array([[(xe - xw) / (2 * h) / c, (xn - xs) / (2 * h)],
                     [(ye - yw) / (2 * h) / c, (yn - ys) / (2 * h)]])


def distortion(proj, lat, lon):
    """Scale factors from the Jacobian: largest and smallest stretch, area scale, angle error (deg)."""
    s_big, s_small = np.linalg.svd(jacobian_fd(proj, lat, lon), compute_uv=False)
    area = s_big * s_small
    omega = np.degrees(2 * np.arcsin((s_big - s_small) / (s_big + s_small)))
    return {"s_max": float(s_big), "s_min": float(s_small), "area": float(area), "omega": float(omega)}


# %% [markdown]
# ## Step 3: the formulas to compare with
# For equirectangular, Mercator and Lambert cylindrical the graticule stays perpendicular, so
# the singular values are just the scale along the parallel `h` and along the meridian `k`:
#
#     equirectangular:  h = sec(lat), k = 1          area = sec(lat)
#     Mercator:         h = sec(lat), k = sec(lat)   area = sec(lat)^2
#     Lambert cyl.:     h = sec(lat), k = cos(lat)   area = 1
#     sinusoidal:       area = 1 everywhere (h = 1; the meridians lean, so check area only)

# %%
def analytic_scales(name, lat):
    """(h, k, area): scale along the parallel, along the meridian, and area scale (lat in radians)."""
    sec = 1.0 / np.cos(lat)
    if name == "equirectangular":
        return sec, 1.0, sec
    if name == "Mercator":
        return sec, sec, sec ** 2
    if name == "Lambert cylindrical":
        return sec, np.cos(lat), 1.0
    if name == "sinusoidal":
        return 1.0, None, 1.0
    raise KeyError(name)


# %% [markdown]
# ## Step 4: the area of the sphere
# Add up (area scale) x (true area of each small cell, cos(lat) dlat dlon). For an equal-area map
# this equals the true area 4 pi; for Mercator it grows without limit as you add polar cells.

# %%
def map_area(proj, lat_max_deg=89.0, n_lat=400, n_lon=8):
    """Area of the whole map (lon -180..180, lat -lat_max..lat_max) for R = 1, by a midpoint sum."""
    lm = np.radians(lat_max_deg)
    dlat = 2 * lm / n_lat
    lats = -lm + (np.arange(n_lat) + 0.5) * dlat
    total = 0.0
    for lat in lats:
        total += distortion(proj, lat, 0.0)["area"] * np.cos(lat) * dlat * 2 * np.pi
    return total


# %% [markdown]
# ## Step 5: the shortest path is not the straight line
# A straight line on a Mercator map keeps a constant compass bearing (a rhumb line). The shortest
# route is the great circle, which curves poleward on Mercator.

# %%
def great_circle_distance(lat1, lon1, lat2, lon2):
    """Distance on the unit sphere (haversine), inputs in degrees; multiply by R for km."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = p2 - p1, np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return float(2 * np.arcsin(np.sqrt(a)))


def rhumb_distance(lat1, lon1, lat2, lon2):
    """Length on the unit sphere of the straight line drawn on a Mercator map (constant bearing)."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dl = np.radians(lon2 - lon1)
    dpsi = np.log(np.tan(np.pi / 4 + p2 / 2) / np.tan(np.pi / 4 + p1 / 2))
    q = (p2 - p1) / dpsi if abs(dpsi) > 1e-12 else np.cos(p1)
    return float(np.hypot(p2 - p1, q * dl))


def great_circle_points(lat1, lon1, lat2, lon2, n=101):
    """Latitude and longitude (degrees) of n points along the great circle (spherical interpolation)."""
    a = np.array([np.cos(np.radians(lat1)) * np.cos(np.radians(lon1)), np.cos(np.radians(lat1)) * np.sin(np.radians(lon1)), np.sin(np.radians(lat1))])
    b = np.array([np.cos(np.radians(lat2)) * np.cos(np.radians(lon2)), np.cos(np.radians(lat2)) * np.sin(np.radians(lon2)), np.sin(np.radians(lat2))])
    w = np.arccos(np.clip(a @ b, -1, 1))
    t = np.linspace(0, 1, n)[:, None]
    p = (np.sin((1 - t) * w) * a + np.sin(t * w) * b) / np.sin(w)
    return np.degrees(np.arcsin(p[:, 2])), np.degrees(np.arctan2(p[:, 1], p[:, 0]))


# %% [markdown]
# ## Step 6: choose a projection for a region
# Sample the region on a grid (longitudes measured from the middle of the region, which is the
# best central meridian for the sinusoidal map) and report, per projection, the worst angle error `omega` and the
# spread of the area scale (largest / smallest). Spread 1.0 means areas are comparable.

# %%
def region_report(lat0, lat1, lon0, lon1, n=15):
    """Dict: projection name -> (max omega in degrees, area spread = max area / min area)."""
    lats = np.radians(np.linspace(lat0, lat1, n))
    lons = np.radians(np.linspace(lon0, lon1, n) - (lon0 + lon1) / 2)   # central meridian = middle of the region
    out = {}
    for name, f in PROJECTIONS.items():
        d = [distortion(f, la, lo) for la in lats for lo in lons]
        areas = np.array([v["area"] for v in d])
        out[name] = (max(v["omega"] for v in d), float(areas.max() / areas.min()))
    return out


def choose_projection(report, max_spread=None, max_omega=None):
    """Names that meet the limits, best (smallest angle error) first. None means no limit."""
    ok = [(v[0], n) for n, v in report.items()
          if (max_spread is None or v[1] <= max_spread) and (max_omega is None or v[0] <= max_omega)]
    return [n for _, n in sorted(ok)]


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    # Figure 1: graticules with Tissot ellipses drawn from the Jacobian
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.4))
    theta = np.linspace(0, 2 * np.pi, 80)
    eps = np.radians(7.0)           # each circle has an angular radius of 7 degrees on the ground
    for ax, (name, f) in zip(axs.ravel(), PROJECTIONS.items()):
        for lo in range(-180, 181, 30):
            la = np.radians(np.linspace(-80, 80, 100))
            x, y = f(la, np.radians(lo) * np.ones_like(la))
            ax.plot(x, y, color="lightgray", lw=0.6)
        for la0 in range(-60, 61, 30):
            lo = np.radians(np.linspace(-180, 180, 200))
            x, y = f(np.radians(la0) * np.ones_like(lo), lo)
            ax.plot(x, y, color="lightgray", lw=0.6)
        for la0 in (-60, -30, 0, 30, 60):
            for lo0 in range(-150, 151, 60):
                J = jacobian_fd(f, np.radians(la0), np.radians(lo0))
                cx, cy = f(np.radians(la0), np.radians(lo0))
                ell = J @ np.vstack([np.cos(theta), np.sin(theta)]) * eps
                ax.fill(cx + ell[0], cy + ell[1], color="#0072b2", alpha=0.6, lw=0)
        ax.set_aspect("equal")
        ax.set_title(name, fontsize=10)
        ax.set_xlabel("map x (unit sphere, R = 1)", fontsize=8)
        ax.set_ylabel("map y (R = 1)", fontsize=8)
        ax.tick_params(labelsize=7)
    fig.suptitle("Tissot ellipses: every blue disc is a 7 degree circle on the ground", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "tissot.png", dpi=120)

    # Figure 2: validation of the numerical area scale against the formulas
    fig2, (b1, b2) = plt.subplots(1, 2, figsize=(10, 4))
    lat_deg = np.linspace(0, 80, 81)
    for name in ("equirectangular", "Mercator", "Lambert cylindrical"):
        num = [distortion(PROJECTIONS[name], np.radians(v), 0.4)["area"] for v in lat_deg]
        ana = [analytic_scales(name, np.radians(v))[2] for v in lat_deg]
        b1.plot(lat_deg, ana, "-", label=name + " (formula)")
        b1.plot(lat_deg[::8], np.array(num)[::8], "ko", ms=3)
    b1.plot([], [], "ko", ms=3, label="finite-difference Jacobian")
    b1.set_ylim(0, 12)
    b1.set_xlabel("latitude (degrees)")
    b1.set_ylabel("area scale = map area / true area")
    b1.set_title("Numerical Jacobian matches the formulas")
    b1.grid(alpha=0.3)
    b1.legend(fontsize=7)
    route = (51.5, -0.1, 40.7, -74.0)
    glat, glon = great_circle_points(*route)
    mx, my = mercator(np.radians(glat), np.radians(glon))
    sx, sy = mercator(np.radians(np.array([route[0], route[2]])), np.radians(np.array([route[1], route[3]])))
    b2.plot(np.degrees(mx), np.degrees(my), "-", color="#d55e00", label="great circle (shortest)")
    b2.plot(np.degrees(sx), np.degrees(sy), "-", color="#0072b2", label="straight line (constant bearing)")
    b2.set_xlabel("Mercator x (degrees of longitude)")
    b2.set_ylabel("Mercator y (57.3 x radians, same units as x)")
    b2.set_title("Two routes on a Mercator map")
    b2.grid(alpha=0.3)
    b2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "validation.png", dpi=120)

    print("area of the whole sphere 4 pi =", round(4 * np.pi, 4))
    for name, f in PROJECTIONS.items():
        print(f"{name:20s} map area to +-89 deg: {map_area(f):9.3f}")
    for lat in (0, 30, 60):
        for name, f in PROJECTIONS.items():
            d = distortion(f, np.radians(lat), 0.0)
            print(f"lat {lat:2d} {name:20s} s_max {d['s_max']:.4f} s_min {d['s_min']:.4f} area {d['area']:.4f} omega {d['omega']:.2f}")
    gc, rh = great_circle_distance(*route), rhumb_distance(*route)
    print(f"London - New York: great circle {gc * 6371:.0f} km, straight line on Mercator {rh * 6371:.0f} km")
    for lat in (80, 89, 89.9, 89.99):
        print(f"Mercator area scale at {lat}: {distortion(mercator, np.radians(lat), 0.0)['area']:.1f}")

# %% [markdown]
# ## Mini-project: choose a projection for a country
# Pick a country, write down its latitude and longitude bounds (an atlas gives them; no data
# files are needed), call `region_report`, and justify your choice in 5 lines.
