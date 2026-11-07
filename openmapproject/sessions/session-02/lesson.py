"""Session 2 (Level 2): the sphere in coordinates, the Mercator projection and area exaggeration.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the sphere as equations, and the Mercator projection
# **A. Real-world problem.** Sailors need a map on which a steady compass course is a straight
# line. Gerardus Mercator solved this in 1569, but his map makes countries near the poles look
# far bigger than they are. Can we measure that exaggeration exactly, and decide which latitude
# range a Mercator map is still honest for?

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
R_EARTH = 6371.0   # km


# %% [markdown]
# ## Step 1: the sphere in coordinates
# A point at latitude `phi` and longitude `lam` (radians) on a sphere of radius R is
#
#     X = R cos(phi) cos(lam),   Y = R cos(phi) sin(lam),   Z = R sin(phi)

# %%
def sphere_xyz(lat_deg, lon_deg, R=R_EARTH):
    phi, lam = np.radians(lat_deg), np.radians(lon_deg)
    return np.stack([R * np.cos(phi) * np.cos(lam), R * np.cos(phi) * np.sin(lam), R * np.sin(phi) + 0 * lam], axis=-1)


# %% [markdown]
# ## Step 2: the Mercator projection
#     x = R * lam,        y = R * ln( tan( pi/4 + phi/2 ) )
# It is built so that, at every point, a small step east and a small step north are enlarged by
# the same factor `sec(phi) = 1 / cos(phi)`. Equal enlargement in all directions keeps angles and
# shapes of small things (it is *conformal*) but it inflates their area by `sec(phi)^2`.

# %%
def mercator(lat_deg, lon_deg, R=R_EARTH):
    """Mercator map position (x, y) in km. The poles map to y = +-infinity."""
    lat, lon = np.broadcast_arrays(np.asarray(lat_deg, dtype=float), np.asarray(lon_deg, dtype=float))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        y = R * np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))
    y = np.where(np.abs(lat) >= 90, np.copysign(np.inf, lat), y)
    return R * np.radians(lon), y


def mercator_inverse(x, y, R=R_EARTH):
    """Latitude and longitude in degrees from Mercator x, y in km."""
    return np.degrees(2 * np.arctan(np.exp(y / R)) - np.pi / 2), np.degrees(x / R)


def mercator_scale(lat_deg):
    """Local scale factor of Mercator, the same east-west and north-south: sec(lat)."""
    return 1.0 / np.cos(np.radians(lat_deg))


def mercator_area_scale(lat_deg):
    """Area on the map divided by true area: sec(lat) squared."""
    return mercator_scale(lat_deg) ** 2


# %% [markdown]
# ## Step 3: real area versus apparent area
# A box with edges at latitudes `phi1 < phi2` and longitudes `lam1 < lam2` has true area
# `R^2 (lam2 - lam1)(sin phi2 - sin phi1)`. On the Mercator map the same box is a rectangle of
# area `R^2 (lam2 - lam1)(psi2 - psi1)`, where `psi = ln(tan(pi/4 + phi/2))`.

# %%
def box_area_sphere(lat1, lat2, lon1, lon2, R=R_EARTH):
    return R ** 2 * np.radians(lon2 - lon1) * (np.sin(np.radians(lat2)) - np.sin(np.radians(lat1)))


def box_area_mercator(lat1, lat2, lon1, lon2, R=R_EARTH):
    _, y1 = mercator(lat1, 0.0, R)
    _, y2 = mercator(lat2, 0.0, R)
    return R * np.radians(lon2 - lon1) * (y2 - y1)


# Two crude boxes (not coastlines!): one around Greenland and one around Africa.
GREENLAND_BOX = (60.0, 83.0, -73.0, -12.0)      # lat1, lat2, lon1, lon2
AFRICA_BOX = (-35.0, 37.0, -17.0, 51.0)


def box_ratio_report():
    """True and apparent (Mercator) area of the two boxes and their ratio."""
    out = {}
    for name, b in (("greenland", GREENLAND_BOX), ("africa", AFRICA_BOX)):
        out[name] = (box_area_sphere(*b), box_area_mercator(*b))
    true_ratio = out["africa"][0] / out["greenland"][0]
    apparent_ratio = out["africa"][1] / out["greenland"][1]
    return out, true_ratio, apparent_ratio


# %% [markdown]
# ## Step 4: a design problem
# Which latitude limit keeps the Mercator area exaggeration below a chosen value `k`?
# Solve `sec(phi)^2 = k`, i.e. `phi = arccos(1 / sqrt(k))`.

# %%
def max_lat_for_exaggeration(k):
    if k < 1:
        raise ValueError("exaggeration factor k must be at least 1")
    return float(np.degrees(np.arccos(1.0 / np.sqrt(k))))


# The map property you need decides the projection family (general guidance, not a rule book).
NEEDS = {
    "navigation by constant compass course (sea chart)": "conformal (angles kept): Mercator",
    "aviation chart of one region": "conformal (angles kept), e.g. a Lambert conformal conic",
    "world map of population density per square km": "equal-area (areas kept)",
    "map of the polar region": "azimuthal, centred on the pole",
}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    lons = np.arange(-180, 181, 30)
    lats = np.arange(-80, 81, 20)
    fine = np.linspace(-80, 80, 321)
    flon = np.linspace(-180, 180, 361)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [1, 1.25]})
    for lo in lons:
        x, y = mercator(fine, lo)
        a1.plot(x / 1000, y / 1000, color="gray", lw=0.6)
    for la in lats:
        x, y = mercator(la, flon)
        a1.plot(x / 1000, y * np.ones_like(x) / 1000, color="gray", lw=0.6)
    for (name, b), col in zip((("box around Greenland", GREENLAND_BOX), ("box around Africa", AFRICA_BOX)), ("#d55e00", "#0072b2")):
        la1, la2, lo1, lo2 = b
        xs = np.array([lo1, lo2, lo2, lo1, lo1])
        ys = np.array([la1, la1, la2, la2, la1])
        mx, my = mercator(ys, xs)
        a1.fill(mx / 1000, my / 1000, color=col, alpha=0.5, label=name)
    a1.set_aspect("equal")
    a1.set_xlabel("Mercator x (thousand km)")
    a1.set_ylabel("Mercator y (thousand km)")
    a1.set_title("Mercator map with two boxes")
    a1.legend(fontsize=8, loc="lower left")
    la = np.linspace(0, 80, 161)
    a2.plot(la, mercator_area_scale(la), color="#d55e00", label="Mercator area scale = sec^2(lat)")
    a2.plot(la, mercator_scale(la), color="#0072b2", label="Mercator length scale = sec(lat)")
    a2.axhline(1, color="gray", ls=":")
    a2.set_ylim(0, 35)
    a2.set_xlabel("latitude (degrees)")
    a2.set_ylabel("map / true (no unit)")
    a2.set_title("How much Mercator inflates lengths and areas")
    a2.grid(alpha=0.3)
    a2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "mercator_exaggeration.png", dpi=120)

    rep, tr, ar = box_ratio_report()
    for k, (t, a) in rep.items():
        print(f"{k:10s} box: true area {t / 1e6:6.2f} million km2, Mercator map area {a / 1e6:7.2f} million km2")
    print(f"Africa box / Greenland box: true {tr:.2f}, on the Mercator map {ar:.2f}")
    for k in (1.5, 2, 4, 10):
        print(f"area exaggeration stays below {k}: latitude up to {max_lat_for_exaggeration(k):.1f} degrees")

# %% [markdown]
# ## Where this stops
# Mercator is one trade-off. Session 3 builds a general tool (the Jacobian) that measures the
# distortion of any projection at any point, and compares four of them.
