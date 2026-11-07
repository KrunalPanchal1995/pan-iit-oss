"""Session 1 (Level 1): day and night from the spin, seasons from the tilt, Moon phases from the lit half.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: why do we have day, night, seasons and Moon phases?
# **A. Real-world problem.** It is hot in June and cold in December where you live, yet in
# early January the Earth is *closest* to the Sun. In Australia it is summer at Christmas.
# The Moon changes from a thin crescent to a full disc and back. All of this comes from three
# simple ideas about geometry. Today you test each one with numbers.
#
# **Plan.** (1) a spinning ball with a Sun on one side gives day and night, (2) a tilted axis
# changes the Sun's noon height through the year, (3) the distance is a small effect and does
# the wrong thing, (4) the Moon is always half lit; we only see part of that half.
# (For the sun path in more detail, see the repo `opendaylight`.)

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

TILT = 23.4          # tilt of the Earth's axis from the orbit normal, degrees
A_MKM = 149.6        # mean Earth-Sun distance, million km
ECC = 0.0167         # how much the orbit differs from a circle (no unit)
PERI_DAY = 4         # day of the year (1 January = 1) of closest approach
MONTH = 29.53        # days from new Moon to new Moon


# %% [markdown]
# ## Step 1: day and night from the spin
# Picture the Sun far away to the right, so its light arrives as parallel rays. A place on
# the Earth is in daylight when its "up" direction (the surface normal) points towards the
# Sun, which means the dot product of the normal with the Sun direction is positive.
# As the Earth spins, the hour angle h (15 degrees for every hour after noon) moves the place
# round a circle of latitude.

# %%
def sun_direction(decl):
    """Unit vector towards the Sun. x points to the Sun on the equator, z to the north pole.
    decl is the latitude (degrees) where the Sun is overhead."""
    d = np.radians(decl)
    return np.array([np.cos(d), 0.0, np.sin(d)])


def surface_normal(lat, hour_angle):
    """Unit vector pointing 'up' at a place (hour angle 0 = local noon)."""
    f, h = np.radians(lat), np.radians(hour_angle)
    return np.array([np.cos(f) * np.cos(h), np.cos(f) * np.sin(h), np.sin(f)])


def is_daylight(lat, hour_angle, decl):
    """True if the Sun is above the horizon: normal . sun direction > 0."""
    return bool(np.dot(surface_normal(lat, hour_angle), sun_direction(decl)) > 0)


def daylight_hours(lat, decl, samples=7200):
    """Count the share of the 24 hours (one spin) during which the place is lit."""
    hours = np.linspace(-12.0, 12.0, samples, endpoint=False)
    lit = [is_daylight(lat, 15.0 * h, decl) for h in hours]
    return 24.0 * float(np.mean(lit))


# %% [markdown]
# ## Step 2: the tilt makes the seasons
# The Earth's axis is tilted by 23.4 degrees from the line at right angles to its orbit, and
# it keeps pointing the same way in space all year. So the latitude where the Sun is
# overhead (the declination d) swings between +23.4 and -23.4 degrees. A simple model of that
# swing: sin(d) = sin(tilt) * sin(2 pi (n - 80) / 365.25), where n is the day of the year
# and day 80 is about the March equinox. At noon the Sun's height above the horizon is
#
#     height = 90 - |latitude - d|        (degrees, for places where this is positive)

# %%
def declination(n, tilt=TILT):
    """Latitude (degrees) where the Sun is overhead on day n of the year."""
    return float(np.degrees(np.arcsin(np.sin(np.radians(tilt)) * np.sin(2 * np.pi * (n - 80) / 365.25))))


def noon_height(lat, decl):
    """Height of the Sun above the horizon at local noon, degrees."""
    return 90.0 - abs(lat - decl)


# %% [markdown]
# ## Step 3: the distance is the wrong suspect
# The orbit is a very slightly squashed circle. A simple model of the distance:
# r = 149.6 * (1 - 0.0167 * cos(2 pi (n - 4) / 365.25)) million km. It is smallest around
# 4 January, when the northern hemisphere is in winter. If distance made the seasons,
# winter would be warm. Also, the whole Earth is at one distance on one day, but the two
# hemispheres have opposite seasons: distance cannot be the cause.

# %%
def distance_mkm(n):
    """Earth-Sun distance in million km on day n."""
    return A_MKM * (1.0 - ECC * np.cos(2 * np.pi * (np.asarray(n, dtype=float) - PERI_DAY) / 365.25))


# %% [markdown]
# ## Step 4: Moon phases
# The Moon is a ball lit by the Sun, so one half is always bright. We see a different part of
# that half as the Moon goes round us. Let D be the elongation: the angle at the Earth from
# the Sun to the Moon (0 at new Moon, 90 at first quarter, 180 at full Moon). The Moon's
# direction of light, in the frame where we look along the z axis, is (sin D, 0, -cos D), and
# a point on the Moon with normal n is bright when n . light > 0. A simple clock: D grows
# 360 degrees in 29.53 days.

# %%
def moon_elongation(age_days):
    """Angle Sun-Earth-Moon in degrees after age_days days past new Moon."""
    return 360.0 * (age_days % MONTH) / MONTH


def lit_fraction_simple(age_days):
    """Fraction of the Moon's disc that looks bright: (1 - cos D) / 2."""
    return float((1.0 - np.cos(np.radians(moon_elongation(age_days)))) / 2.0)


def phase_name(age_days):
    """One of eight names for the age."""
    names = ["new", "waxing crescent", "first quarter", "waxing gibbous",
             "full", "waning gibbous", "last quarter", "waning crescent"]
    return names[int(((moon_elongation(age_days) + 22.5) % 360.0) // 45.0) % 8]


def moon_image(elong_deg, n=121):
    """n x n picture of the Moon disc: 1 = bright, 0 = dark, nan outside the disc.
    Waxing phases (0 < D < 180) are bright on the right, as seen from the north."""
    y, x = np.mgrid[1:-1:n * 1j, -1:1:n * 1j]
    r2 = x ** 2 + y ** 2
    z = np.sqrt(np.clip(1 - r2, 0, None))
    d = np.radians(elong_deg)
    light = np.array([np.sin(d), 0.0, -np.cos(d)])
    bright = (x * light[0] + y * light[1] + z * light[2]) > 0
    img = np.where(bright, 1.0, 0.0)
    img[r2 > 1] = np.nan
    return img


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    days = np.arange(1, 366)

    print("day length at 40 N (hours) with no tilt, June, December:",
          round(daylight_hours(40, declination(172, 0.0)), 2),
          round(daylight_hours(40, declination(172)), 2),
          round(daylight_hours(40, declination(355)), 2))
    print("noon Sun height at 40 N in June and December:",
          round(noon_height(40, declination(172)), 1), round(noon_height(40, declination(355)), 1))
    print("Earth-Sun distance on 4 January and 4 July (million km):",
          round(float(distance_mkm(4)), 1), round(float(distance_mkm(185)), 1))
    print("noon height on 4 January at 40 N and 40 S:",
          round(noon_height(40, declination(4)), 1), round(noon_height(-40, declination(4)), 1))
    print("Moon lit fraction at ages 0, 7.4, 14.8 days:",
          [round(lit_fraction_simple(a), 2) for a in (0, 7.4, 14.8)])

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(days, [noon_height(40, declination(n)) for n in days], label="40 N (north)")
    ax[0].plot(days, [noon_height(-40, declination(n)) for n in days], label="40 S (south)")
    ax[0].set_xlabel("day of the year (1 = 1 January)")
    ax[0].set_ylabel("Sun height at noon (degrees)")
    ax[0].set_title("Seasons are opposite in the two hemispheres")
    ax[0].grid(alpha=0.3)
    ax[0].legend()
    ax[1].plot(days, distance_mkm(days), color="tab:red")
    ax[1].set_xlabel("day of the year (1 = 1 January)")
    ax[1].set_ylabel("Earth-Sun distance (million km)")
    ax[1].set_title("Closest in early January")
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "seasons_vs_distance.png", dpi=120)

    fig2, axs = plt.subplots(1, 8, figsize=(12, 2.0))
    for a, age in zip(axs, np.arange(8) * MONTH / 8):
        a.imshow(moon_image(moon_elongation(age)), cmap="gray", vmin=-0.3, vmax=1.0)
        a.set_title(phase_name(age), fontsize=7)
        a.axis("off")
    fig2.suptitle("The same half-lit Moon, seen from different angles", fontsize=9)
    fig2.savefig(OUT / "moon_phases.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
