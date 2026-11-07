"""Session 1 (Level 1): where is the sun? The sun path, shadows and day length.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: where is the sun? Sun path, shadows and day length
# **A. Real-world problem.** Before you can place a window you must know where the sun will be.
# In Chennai the noon sun is high all year, and on two days it is straight overhead (Zero
# Shadow Day). In Delhi the winter sun is low and shines deep into south-facing rooms. Where
# exactly is the sun at a given hour, how long is the shadow of a pole, and how long is the day?
#
# **Plan.** (1) the sun's declination through the year, (2) the noon sun altitude,
# (3) the sun's altitude and azimuth at any hour, (4) shadows and day length.
#
# **Model.** Sun angles from the standard textbook formulas, in solar time (12:00 = sun due
# south or due north). We ignore the equation of time, refraction and the time-zone offset.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
TILT = 23.45      # tilt of the Earth's axis (degrees)


# %% [markdown]
# ## Step 1: the declination, the sun's "latitude"
# The Earth's axis is tilted by 23.45 degrees. Through the year the sun is overhead at noon
# somewhere between the Tropic of Cancer (23.45 N, about 21 June) and the Tropic of Capricorn
# (23.45 S, about 21 December). That latitude is the **declination** delta. Cooper's formula,
# with n the day of the year (1 = 1 January):
#
#     delta = 23.45 sin( 360 (284 + n) / 365 )   degrees
#
# It is 0 at the equinoxes (n = 81, about 22 March) and +23.45 on n = 172 (21 June).

# %%
def declination(n):
    """Solar declination (degrees) on day of the year n (1 to 365), Cooper's formula."""
    n = np.asarray(n, float)
    return TILT * np.sin(np.radians(360.0 * (284.0 + n) / 365.0))


# %% [markdown]
# ## Step 2: the noon sun altitude
# The **altitude** is the angle of the sun above the horizon. At solar noon the sun is in the
# north-south plane, and the angle from the zenith (straight up) to the sun is simply the
# difference between your latitude phi and the declination:
#
#     noon altitude = 90 - |phi - delta|
#
# If delta > phi (possible only in the tropics) the noon sun is to the **north**.

# %%
def noon_altitude(lat, decl):
    """Altitude of the sun at solar noon (degrees). lat and decl in degrees, north positive."""
    return 90.0 - np.abs(np.asarray(lat, float) - np.asarray(decl, float))


# %% [markdown]
# ## Step 3: altitude and azimuth at any hour
# The sun turns 15 degrees per hour round the Earth's axis. The **hour angle** is
# H = 15 (solar hour - 12): negative in the morning, positive in the afternoon. Turning the
# sun direction into east, north and up components gives
#
#     up    = sin(delta) sin(phi) + cos(delta) cos(phi) cos(H)    = sin(altitude)
#     east  = -cos(delta) sin(H)
#     north = sin(delta) cos(phi) - cos(delta) sin(phi) cos(H)
#
# and the **azimuth** (compass bearing of the sun, clockwise from north: N 0, E 90, S 180,
# W 270) is atan2(east, north).

# %%
def sun_position(lat, decl, hour):
    """(altitude, azimuth) in degrees at solar time `hour` (0 to 24). Azimuth from north, clockwise."""
    phi, d = np.radians(lat), np.radians(decl)
    h = np.radians(15.0 * (np.asarray(hour, float) - 12.0))
    up = np.sin(d) * np.sin(phi) + np.cos(d) * np.cos(phi) * np.cos(h)
    east = -np.cos(d) * np.sin(h)
    north = np.sin(d) * np.cos(phi) - np.cos(d) * np.sin(phi) * np.cos(h)
    alt = np.degrees(np.arcsin(np.clip(up, -1.0, 1.0)))
    az = np.degrees(np.arctan2(east, north)) % 360.0
    return alt, az


# %% [markdown]
# ## Step 4: shadows and day length
# A vertical pole of height h casts a shadow of length L = h / tan(altitude), pointing away
# from the sun (azimuth + 180). At sunrise and sunset the altitude is 0, which gives
#
#     cos(H0) = -tan(phi) tan(delta)        day length = 2 H0 / 15 hours
#
# Near the poles the right-hand side can go beyond -1 or +1: then the sun never sets (24 h)
# or never rises (0 h).

# %%
def shadow_length(height, altitude):
    """Shadow length (m) of a vertical pole of `height` (m) for a sun altitude in degrees."""
    altitude = float(altitude)
    if altitude <= 0.0:
        raise ValueError("the sun is below the horizon: no shadow")
    return height / np.tan(np.radians(altitude))


def day_length(lat, decl):
    """Hours from sunrise to sunset (sun centre on a flat horizon, no refraction)."""
    c = -np.tan(np.radians(lat)) * np.tan(np.radians(decl))
    return 2.0 * np.degrees(np.arccos(np.clip(c, -1.0, 1.0))) / 15.0


def sunrise_hour(lat, decl):
    """Solar time of sunrise (hours)."""
    return 12.0 - day_length(lat, decl) / 2.0


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    CHENNAI, DELHI = 13.0, 28.6

    days = {"21 June (n = 172)": 172, "22 March (n = 81)": 81, "21 December (n = 355)": 355}
    for name, n in days.items():
        d = float(declination(n))
        print(f"{name}: declination {d:+.2f} deg, Chennai noon altitude {float(noon_altitude(CHENNAI, d)):.2f} deg, "
              f"day length {float(day_length(CHENNAI, d)):.2f} h")

    # Figure 1: the sun path in Chennai on three days (altitude against azimuth)
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    colours = ["#d9534f", "#e9a23b", "#2a9d8f"]
    for (name, n), col in zip(days.items(), colours):
        d = float(declination(n))
        t0 = float(sunrise_hour(CHENNAI, d))
        hours = np.linspace(t0, 24.0 - t0, 200)
        alt, az = sun_position(CHENNAI, d, hours)
        az = np.where(np.abs(np.diff(az, prepend=az[0])) > 180, np.nan, az)   # break the line where it wraps past north
        ax.plot(az, alt, color=col, label=name)
        for hr in range(7, 18):
            a, z = sun_position(CHENNAI, d, hr)
            if a > 0:
                ax.plot(z, a, "o", color=col, ms=3)
                if n == 355:
                    ax.annotate(f"{hr}h", (z, a), textcoords="offset points", xytext=(0, -12), ha="center", fontsize=7)
    ax.set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])
    ax.set_xticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])
    ax.set_xlim(0, 360)
    ax.set_ylim(0, 90)
    ax.set_xlabel("azimuth (compass direction of the sun)")
    ax.set_ylabel("altitude above horizon (degrees)")
    ax.set_title("Sun path at Chennai (13 N): dots every hour, solar time")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "sun_paths.png", dpi=120)

    # Figure 2: noon altitude and noon shadow of a 1 m pole through the year
    n = np.arange(1, 366)
    fig2, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
    for lat, name, col in ((CHENNAI, "Chennai 13 N", "#2a9d8f"), (DELHI, "Delhi 28.6 N", "#264653")):
        d = declination(n)
        alt = noon_altitude(lat, d)
        a1.plot(n, alt, color=col, label=name)
        # signed noon shadow: + points north (sun to the south), - points south (sun to the north)
        sign = np.where(lat > d, 1.0, -1.0)
        a2.plot(n, sign / np.tan(np.radians(alt)), color=col, label=name)
    a1.axhline(90, color="k", lw=0.8, ls="--")
    a1.set_xlabel("day of the year n")
    a1.set_ylabel("noon sun altitude (degrees)")
    a1.set_title("Noon sun altitude through the year")
    a1.legend(fontsize=8)
    a1.grid(alpha=0.3)
    a2.axhline(0, color="k", lw=0.8)
    a2.set_xlabel("day of the year n")
    a2.set_ylabel("noon shadow of a 1 m pole (m)\n+ points north, - points south")
    a2.set_title("Zero Shadow Days: where the curve crosses 0")
    a2.legend(fontsize=8)
    a2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "noon_shadow.png", dpi=120)

    zero = [int(k) for k in n if abs(float(noon_altitude(CHENNAI, declination(k))) - 90.0) < 0.25]
    print("Chennai days with the noon sun within 0.25 deg of overhead:", zero)

# %% [markdown]
# ## Where this stops
# We now know where the sun is. Session 2 turns these two angles into the angle the sunlight
# makes with a window, the shadow of an overhang, and the solar heat that comes through glass.
