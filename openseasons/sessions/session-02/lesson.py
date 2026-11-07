"""Session 2 (Level 2): vectors for the tilted axis, the subsolar latitude, day length, distance, sidereal day.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the tilted axis as a vector
# **A. Real-world problem.** A solar-farm planner needs, for any latitude and date, the
# length of the day, the noon Sun height and how much sunlight reaches the ground, and must
# explain why the 6.9 percent swing in Earth-Sun distance does not decide the seasons. Today
# you build these from three-dimensional vectors and check each one by an independent route.
# The sun path through the day is in the repo `opendaylight`; here the new idea is the
# **dot product of the Sun direction with the spin axis**.

# %%
import datetime as dt
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

TILT = 23.44             # tilt of the spin axis from the orbit normal, degrees
AU_MKM = 149.598         # one astronomical unit, million km
SOLAR_CONSTANT = 1361.0  # sunlight at 1 AU, watts per square metre
TROPICAL_YEAR = 365.2422  # days from equinox to equinox


# %% [markdown]
# ## Step 1: where is the Sun in the sky of the Earth?
# We use days counted from the year 2000 (noon on 1 January 2000 is day 0), as astronomers do.
# Low-precision formulas for the Sun (accurate to about 0.01 degrees in longitude):
# the mean anomaly g = 357.528 + 0.9856003 d, the mean longitude L = 280.460 + 0.9856474 d,
# the Sun's ecliptic longitude lam = L + 1.915 sin g + 0.020 sin 2g, and the distance
# r = 1.00014 - 0.01671 cos g - 0.00014 cos 2g (in AU). The "ecliptic longitude" is the
# direction of the Sun along the orbit plane: 0 degrees at the March equinox, 90 at the
# June solstice, 180 at the September equinox, 270 at the December solstice.

# %%
def days_since_j2000(year, month, day, hour=0.0):
    """Days since noon UT on 1 January 2000."""
    return (dt.datetime(year, month, day) - dt.datetime(2000, 1, 1, 12)).total_seconds() / 86400.0 + hour / 24.0


def sun_longitude(d):
    """Ecliptic longitude of the Sun in degrees (0 to 360) at day d since J2000."""
    d = np.asarray(d, dtype=float)
    g = np.radians(357.528 + 0.9856003 * d)
    return (280.460 + 0.9856474 * d + 1.915 * np.sin(g) + 0.020 * np.sin(2 * g)) % 360.0


def sun_distance_au(d):
    """Earth-Sun distance in AU at day d since J2000."""
    g = np.radians(357.528 + 0.9856003 * np.asarray(d, dtype=float))
    return 1.00014 - 0.01671 * np.cos(g) - 0.00014 * np.cos(2 * g)


# %% [markdown]
# ## Step 2: the subsolar latitude equals the declination (dot product)
# Use axes: x towards the March-equinox direction, y 90 degrees further along the orbit plane,
# z perpendicular to the orbit plane. The spin axis keeps pointing one way in space,
# tilted by T from z: a = (0, sin T, cos T). The direction from the Earth to the Sun is
# s = (cos lam, sin lam, 0). The latitude where the Sun is overhead (the subsolar latitude)
# is the latitude of the point whose "up" direction equals s. Latitude is measured from the
# equator, so sin(latitude) = (up direction) . a. For the subsolar point, up = s:
#
#     sin(d) = s . a = sin T sin(lam)
#
# This is the declination d. It is the same as the formula of `opendaylight` up to the
# accuracy of that simpler model, and now you see where it comes from.

# %%
def spin_axis(tilt=TILT):
    t = np.radians(tilt)
    return np.array([0.0, np.sin(t), np.cos(t)])


def sun_vector(lam):
    l = np.radians(lam)
    return np.array([np.cos(l), np.sin(l), 0.0])


def declination_from_vectors(lam, tilt=TILT):
    """Subsolar latitude in degrees: arcsin of (Sun direction . spin axis)."""
    return float(np.degrees(np.arcsin(np.clip(np.dot(sun_vector(lam), spin_axis(tilt)), -1.0, 1.0))))


def declination_formula(n):
    """The simpler day-of-year formula d = 23.45 sin(360/365 (284 + n)) used in `opendaylight`."""
    return float(23.45 * np.sin(np.radians(360.0 / 365.0 * (284.0 + n))))


# %% [markdown]
# ## Step 3: day length, noon height
# A place at latitude phi has "up" vector n(h) = (cos phi cos h, cos phi sin h, sin phi) in a frame
# where the Sun is at (cos d, 0, sin d); h is the hour angle (15 degrees per hour). It is
# daytime when n . sun > 0:  cos phi cos d cos h + sin phi sin d > 0. The edge of daylight is
# cos(H0) = -tan(phi) tan(d). The day lasts 2 H0 / 15 hours. If the right side is >= 1 the Sun
# never rises (polar night); if <= -1 it never sets (polar day). Noon is h = 0, where the dot
# product is cos(phi - d), so the noon height is 90 - |phi - d|. (Geometric day: the Sun as
# a point, no air bending the light, so real days are a few minutes longer.)

# %%
def day_length_hours(lat, decl):
    """Hours of daylight from the sunrise equation (geometric)."""
    f = np.radians(np.clip(lat, -89.999, 89.999))
    d = np.radians(decl)
    c = -np.tan(f) * np.tan(d)
    return float(24.0 * np.arccos(np.clip(c, -1.0, 1.0)) / np.pi)


def day_length_by_vectors(lat, decl, samples=14400):
    """The same day length by brute force: the share of a circle of latitude with n . sun > 0."""
    f, d = np.radians(lat), np.radians(decl)
    h = np.linspace(0.0, 2 * np.pi, samples, endpoint=False)
    dot = np.cos(f) * np.cos(d) * np.cos(h) + np.sin(f) * np.sin(d)
    return 24.0 * float(np.mean(dot > 0))


def noon_height(lat, decl):
    """Sun height at local noon, degrees (negative: the Sun stays below the horizon)."""
    return 90.0 - abs(lat - decl)


def noon_height_by_vectors(lat, decl, samples=14401):
    """The highest Sun height over a day, found from the dot product: arcsin(max n . sun)."""
    f, d = np.radians(lat), np.radians(decl)
    h = np.linspace(-np.pi, np.pi, samples)
    dot = np.cos(f) * np.cos(d) * np.cos(h) + np.sin(f) * np.sin(d)
    return float(np.degrees(np.arcsin(dot.max())))


# %% [markdown]
# ## Step 4: distance and sunlight; why it is not the cause of seasons
# Sunlight arriving at a surface facing the Sun falls as 1 / r^2 (the same power spread over
# the area of a sphere 4 pi r^2). The mean daily sunlight on flat ground (watts per square
# metre, averaged over 24 hours) is
#
#     Q = S0 / (pi r^2) * ( H0 sin(phi) sin(d) + cos(phi) cos(d) sin(H0) )
#
# with r in AU and H0 in radians. The distance enters as 1/r^2 for every place on Earth at
# once; the bracket depends on latitude and season. Opposite hemispheres have opposite
# brackets, so distance cannot make one hemisphere warm and the other cold.

# %%
def daily_insolation(lat, decl, r_au):
    """Mean daily sunlight on a horizontal surface at the top of the atmosphere, W/m^2."""
    f = np.radians(np.clip(lat, -89.999, 89.999))
    d = np.radians(decl)
    h0 = np.arccos(np.clip(-np.tan(f) * np.tan(d), -1.0, 1.0))
    bracket = h0 * np.sin(f) * np.sin(d) + np.cos(f) * np.cos(d) * np.sin(h0)
    return float(SOLAR_CONSTANT / (np.pi * r_au ** 2) * bracket)


def irradiance_ratio(r_near, r_far):
    """Sunlight at the near distance divided by sunlight at the far distance (inverse square)."""
    return (r_far / r_near) ** 2


# %% [markdown]
# ## Step 5: the sidereal day and the solar day
# In one day the Earth turns 360 degrees relative to the stars (a sidereal day) but also
# moves 360 / 365.2422 = 0.9856 degrees along its orbit, so the Sun has not come back to
# the same direction yet; the Earth must turn that extra angle. The Earth turns 360 degrees in
# one sidereal day (86164 s), so one degree takes about 239.3 s and the extra is
# 0.9856 * 239.3 = 235.9 s, almost 4 minutes (3 min 56 s).
# Exactly: 1 / T_solar = 1 / T_sidereal - 1 / T_year (in days).

# %%
def extra_rotation_seconds(year_days=TROPICAL_YEAR):
    """Seconds of spin needed per day to make up the orbital motion."""
    return 360.0 / year_days * sidereal_day_seconds(year_days) / 360.0


def sidereal_day_seconds(year_days=TROPICAL_YEAR):
    """Length of the sidereal day from 1/T_sid = 1/T_solar + 1/T_year (T_solar = 86400 s)."""
    return 86400.0 / (1.0 + 1.0 / year_days)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    d2026 = days_since_j2000(2026, 1, 1) + np.arange(365)
    lam = sun_longitude(d2026)
    dec = np.array([declination_from_vectors(x) for x in lam])
    old = np.array([declination_formula(n) for n in range(1, 366)])
    r = sun_distance_au(d2026)
    print("peak declination (deg) and day of year:", round(dec.max(), 2), int(np.argmax(dec)) + 1)
    print("largest gap between the vector declination and the simple formula (deg):", round(np.abs(dec - old).max(), 2))
    print("distance range (million km):", round(r.min() * AU_MKM, 1), round(r.max() * AU_MKM, 1),
          "closest on day", int(np.argmin(r)) + 1)
    print("sunlight ratio perihelion / aphelion:", round(irradiance_ratio(r.min(), r.max()), 4))
    print("polar day at 67 N in June (h):", round(day_length_hours(67, 23.44), 2),
          "and 66 N:", round(day_length_hours(66, 23.44), 2))
    print("sidereal day (s), extra spin (s):", round(sidereal_day_seconds(), 1), round(extra_rotation_seconds(), 1))

    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(np.arange(1, 366), dec, label="from s . a (vectors)")
    ax.plot(np.arange(1, 366), old, "--", label="simple formula")
    ax.set_xlabel("day of 2026 (1 = 1 January)")
    ax.set_ylabel("subsolar latitude (degrees)")
    ax.set_title("Declination: peak 23.44 degrees at the June solstice")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "declination.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    for lat in (0, 30, 50, 65, -50):
        ax2.plot(np.arange(1, 366), [day_length_hours(lat, x) for x in dec], label=f"latitude {lat}")
    ax2.set_xlabel("day of 2026 (1 = 1 January)")
    ax2.set_ylabel("length of the day (hours)")
    ax2.set_title("Day length: 12 h everywhere at the equinoxes")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "day_length.png", dpi=120)

    fig3, ax3 = plt.subplots(figsize=(6.5, 4))
    for lat in (45, -45):
        ax3.plot(np.arange(1, 366), [daily_insolation(lat, x, y) for x, y in zip(dec, r)], label=f"latitude {lat}")
    ax3.set_xlabel("day of 2026 (1 = 1 January)")
    ax3.set_ylabel("mean daily sunlight (W/m^2)")
    ax3.set_title("Same distance, opposite seasons")
    ax3.grid(alpha=0.3)
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(OUT / "insolation.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
