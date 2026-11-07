"""Session 1 (Level 1): why a flat map of a sphere must distort.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: why a flat map of a round Earth must distort
# **A. Real-world problem.** Peel an orange in one piece and try to press the peel flat on a
# table. It tears, or it must be stretched. The Earth is a ball, and every flat map is a pressed
# peel. In this session you measure how much the simplest map (the equirectangular map, latitude
# and longitude drawn as a plain grid) stretches the world at different latitudes.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
R_EARTH = 6371.0   # mean radius of the Earth in km (a sphere is our simplified model)


# %% [markdown]
# ## Step 1: latitude, longitude and the equirectangular map
# *Latitude* is the angle north (+) or south (-) of the equator, from -90 to +90 degrees.
# *Longitude* is the angle east (+) or west (-) of a reference meridian, from -180 to +180.
# The equirectangular map simply uses them as grid coordinates:
#
#     x = R * longitude,      y = R * latitude        (angles in radians, x and y in km)

# %%
def equirect(lat_deg, lon_deg, R=R_EARTH):
    """Map position (x, y) in km of a point given by latitude and longitude in degrees."""
    return R * np.radians(lon_deg), R * np.radians(lat_deg)


# %% [markdown]
# ## Step 2: how long is a circle of latitude?
# On the ball, the circle at latitude `lat` is smaller than the equator: its radius is
# `R cos(lat)`. On the map every such circle is drawn with the same length as the equator.

# %%
def parallel_length_sphere(lat_deg, R=R_EARTH):
    """True length in km of the full circle of latitude."""
    return 2 * np.pi * R * np.cos(np.radians(lat_deg))


def parallel_length_map(lat_deg, R=R_EARTH):
    """Length in km that the same circle has on the equirectangular map (the map width)."""
    return 2 * np.pi * R


def ew_stretch(lat_deg):
    """East-west stretch of the equirectangular map: map length / true length = 1 / cos(lat)."""
    lat = abs(float(lat_deg))
    if lat >= 90:
        return float("inf")      # a pole is a single point, drawn as a whole line
    return 1.0 / np.cos(np.radians(lat))


def gap_fraction(lat_deg):
    """Share of a map row that is 'made-up' (stretched) material: 1 - cos(lat)."""
    return 1.0 - np.cos(np.radians(lat_deg))


# %% [markdown]
# ## Step 3: a patch of the world
# A patch that is `span` degrees wide in longitude has true east-west width
# `R cos(lat) * span` but is drawn `R * span` wide. North-south it is drawn at true size, so
# **area on the map = area on the ball x 1 / cos(lat)**.

# %%
def patch_width_true(lat_deg, span_deg, R=R_EARTH):
    return R * np.cos(np.radians(lat_deg)) * np.radians(span_deg)


def patch_width_map(span_deg, R=R_EARTH):
    return R * np.radians(span_deg)


def area_stretch(lat_deg):
    """Area on the map divided by true area for the equirectangular map."""
    return ew_stretch(lat_deg)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    # Figure 1: the orange peel.  12 gores of 30 degrees; each is only cos(lat) wide.
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6.2))
    lat = np.linspace(-90, 90, 181)
    for k in range(12):
        lo = -180 + 30 * k
        c = lo + 15
        half = 15 * np.cos(np.radians(lat))
        a1.fill_betweenx(lat, c - half, c + half, color="#e69f00", alpha=0.75, lw=0.5, ec="white")
        a2.fill_betweenx(lat, lo, lo + 30, color="#e69f00", alpha=0.75, lw=0.5, ec="white")
    a1.set_title("Peel the ball into 12 strips: each strip is only cos(latitude) wide (gaps appear)")
    a2.set_title("Press them into a plain grid: the gaps must be filled by stretching")
    for ax in (a1, a2):
        ax.set_ylabel("latitude (degrees)")
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        ax.set_aspect("equal")
    a2.set_xlabel("longitude (degrees)")
    fig.tight_layout()
    fig.savefig(OUT / "orange_peel.png", dpi=120)

    # Figure 2: stretch against latitude
    lats = np.linspace(0, 80, 161)
    fig2, ax = plt.subplots(figsize=(6, 4))
    ax.plot(lats, [ew_stretch(v) for v in lats], color="#0072b2", label="east-west stretch = area stretch")
    ax.axhline(1, color="gray", ls=":", label="true size")
    ax.plot([60], [ew_stretch(60)], "ro")
    ax.annotate("60 degrees: x2", (60, 2), textcoords="offset points", xytext=(-80, 12))
    ax.set_xlabel("latitude (degrees)")
    ax.set_ylabel("map size / true size (no unit)")
    ax.set_title("Equirectangular map: stretch grows toward the poles")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "stretch_vs_latitude.png", dpi=120)
    for v in (0, 30, 60, 80):
        print(f"latitude {v:2d}: circle of latitude {parallel_length_sphere(v):9.1f} km on the ball, "
              f"{parallel_length_map(v):9.1f} km on the map, stretch {ew_stretch(v):.3f}")

# %% [markdown]
# ## Where this stops
# Stretching only east-west is one choice. Other maps stretch differently (Session 2 gives
# Mercator) and Session 3 measures every kind of distortion with one tool, the Jacobian.
