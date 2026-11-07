"""Session 3 (Level 3): Moon phases by simulation, the synodic month, moonrise, why eclipses are rare, a year table.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulating the Moon
# **A. Real-world problem.** A school wants a printed phase calendar for 2026 and a table
# for its own latitude: day length, noon Sun height and Moon phase on chosen dates. You
# will compute them from angles, check the Moon's month from two simpler periods, see why
# the Moon rises about 50 minutes later each night, and answer two questions people ask:
# "why is there no eclipse every month?" and "is the phase the Earth's shadow?".
# (Eclipse prediction itself is a topic for a future repo; here we only count the odds.)

# %%
import datetime as dt
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

SYNODIC = 29.530588861      # mean days from new Moon to new Moon
SIDEREAL_MONTH = 27.321662  # days for the Moon to return to the same star
SIDEREAL_YEAR = 365.25636   # days for the Earth to return to the same star
EPOCH_NEW = 5.09766         # a reference mean new Moon: 6 January 2000, about 14 h (days since J2000)
INCLINATION = 5.145         # tilt of the Moon's orbit to the Earth's orbit, degrees
MOON_DIST_KM = 384400.0
SUN_DIST_KM = 149.598e6
R_EARTH, R_SUN, R_MOON = 6371.0, 695700.0, 1737.4   # radii in km
TILT = 23.44


# %% [markdown]
# ## Step 1: the geometry of the phase
# Put the Earth at the origin, the Sun far along +x and the Moon at distance 384400 km, at
# an elongation D from the Sun. The phase angle i is the angle at the Moon between the
# directions to the Sun and to the Earth. The bright part we see is
#
#     k = (1 + cos i) / 2        (i = 0: full, i = 90: half, i = 180: new)
#
# Because the Sun is 389 times farther than the Moon, i is almost exactly 180 - D, so
# k is almost (1 - cos D) / 2, the formula of Session 1.

# %%
def phase_angle_deg(elong_deg):
    """Angle Sun-Moon-Earth, from the real distances."""
    d = np.radians(elong_deg)
    sun = np.array([SUN_DIST_KM, 0.0])
    moon = MOON_DIST_KM * np.array([np.cos(d), np.sin(d)])
    to_sun, to_earth = sun - moon, -moon
    c = np.dot(to_sun, to_earth) / (np.linalg.norm(to_sun) * np.linalg.norm(to_earth))
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))


def illuminated_fraction(phase_angle):
    """Fraction of the disc that is bright, from the phase angle in degrees."""
    return float((1.0 + np.cos(np.radians(phase_angle))) / 2.0)


# %% [markdown]
# ## Step 2: the synodic month from two simpler periods
# Seen from the stars the Moon needs 27.32 days (sidereal month) to go round, but the Earth
# has meanwhile moved along its orbit, so the Moon must go round further to catch up with the
# Sun. In one day the Moon gains 1/27.32 of a turn, the Sun appears to gain 1/365.256 of a
# turn, so the phase cycle gains the difference:
#
#     1 / T_syn = 1 / T_sid - 1 / T_year

# %%
def synodic_from(t_sid=SIDEREAL_MONTH, t_year=SIDEREAL_YEAR):
    return 1.0 / (1.0 / t_sid - 1.0 / t_year)


def mean_elongation(d):
    """Mean elongation (degrees, 0-360) at day d since J2000: 360 degrees per synodic month."""
    return (360.0 * (np.asarray(d, dtype=float) - EPOCH_NEW) / SYNODIC) % 360.0


# %% [markdown]
# ## Step 3: a phase calendar by simulation
# Step through the year in one-hour steps, compute the elongation each time, and note when it
# passes 0 (new), 90 (first quarter), 180 (full) and 270 (last quarter) degrees. This uses the
# *mean* motion: the real Moon speeds up and slows down on its eccentric orbit, so the
# true phase can differ from the mean by up to about 14 hours.

# %%
PHASES = ["new Moon", "first quarter", "full Moon", "last quarter"]


def days_since_j2000(year, month, day, hour=0.0):
    return (dt.datetime(year, month, day) - dt.datetime(2000, 1, 1, 12)).total_seconds() / 86400.0 + hour / 24.0


def phase_calendar(year):
    """List of (datetime UT, name) of the mean quarter phases in a year."""
    start = days_since_j2000(year, 1, 1)
    stop = days_since_j2000(year + 1, 1, 1)
    t = np.arange(start - 1.0, stop + 1.0, 1.0 / 24.0)
    total = 360.0 * (t - EPOCH_NEW) / SYNODIC          # elongation without wrapping
    k = np.floor(total / 90.0)
    out = []
    for i in np.nonzero(np.diff(k) > 0)[0]:
        frac = (90.0 * k[i + 1] - total[i]) / (total[i + 1] - total[i])
        when = t[i] + frac / 24.0
        if start <= when < stop:
            out.append((dt.datetime(2000, 1, 1, 12) + dt.timedelta(days=float(when)), PHASES[int(k[i + 1]) % 4]))
    return out


# %% [markdown]
# ## Step 4: moonrise 50 minutes later each day
# Take a Moon on the celestial equator for simplicity. At local time T (hours after midnight) the
# Sun's hour angle is 15 (T - 12) degrees, and the Moon's is that minus the elongation D.
# The Moon rises when its hour angle is -90 degrees. While we wait the next day, D grows by
# 12.19 degrees (and keeps growing during the wait, 0.508 degrees per hour). So the delay is
#
#     delay = 12.19 / (15 - 0.508) hours = 0.841 h = 50.5 minutes
#
# which is the same idea as `1/T = 1/T1 - 1/T2` again: 24.84 h = 24 h * 29.53 / 28.53.

# %%
def moonrise_times(d_elong0=0.0, ndays=6, step_min=1.0):
    """Times (hours after the first midnight) at which the model Moon rises."""
    rate = 360.0 / SYNODIC / 24.0            # elongation growth, degrees per hour
    t = np.arange(0.0, 24.0 * ndays, step_min / 60.0)
    hm = (15.0 * (t - 12.0) - (d_elong0 + rate * t) + 90.0) % 360.0   # 0 when hour angle = -90
    # the hour angle increases, so hm climbs towards 360 and wraps to 0 at the moment of moonrise
    wrap = np.nonzero(hm[1:] < hm[:-1] - 180.0)[0]
    rises = []
    for i in wrap:
        a, b = hm[i], hm[i + 1] + 360.0
        rises.append(t[i] + (360.0 - a) / (b - a) * (t[i + 1] - t[i]))
    return np.array(rises)


# %% [markdown]
# ## Step 5: why not an eclipse every month?
# The Moon's orbit is tilted by 5.145 degrees to the Earth's. When the Moon is new or full, its
# ecliptic latitude is  beta = asin( sin(5.145) sin(u) ), where u is the Moon's angle from the
# place where its orbit crosses the Earth's (a node). For the shadow or the Moon's disc to
# touch a place on Earth the latitude must be small, about the sum of the two angular radii
# plus the Moon's parallax (0.267 + 0.259 + 0.951 = 1.48 degrees). If u is random, the share
# of new Moons close enough is  2 asin(1.48 / 5.145 ) / pi.

# %%
def latitude_limit_deg():
    """Largest Moon latitude (degrees) at which some eclipse is still possible, simple estimate."""
    return 0.2666 + 0.2590 + 0.9507


def fraction_near_node(inclination=INCLINATION, limit=None):
    """Analytic share of new (or full) Moons with |latitude| below the limit."""
    limit = latitude_limit_deg() if limit is None else limit
    x = limit / inclination
    return 1.0 if x >= 1.0 else float(2.0 * np.arcsin(x) / np.pi)


def fraction_near_node_mc(n=200000, inclination=INCLINATION, seed=1):
    """The same share by Monte Carlo: random node angle u, count |beta| < limit."""
    u = np.random.default_rng(seed).uniform(0.0, 2 * np.pi, n)
    beta = np.degrees(np.arcsin(np.sin(np.radians(inclination)) * np.sin(u)))
    return float(np.mean(np.abs(beta) < latitude_limit_deg()))


def syzygy_latitudes(year):
    """For each mean new and full Moon of a year: (datetime, name, Moon ecliptic latitude in degrees).
    The Moon's angle from a node advances 13.2293505 degrees a day (mean motion), starting at
    93.272095 degrees on J2000. Positions are mean values, so they can be a degree or two off."""
    out = []
    for when, name in phase_calendar(year):
        if name in ("new Moon", "full Moon"):
            d = (when - dt.datetime(2000, 1, 1, 12)).total_seconds() / 86400.0
            u = np.radians(93.272095 + 13.2293505 * d)
            out.append((when, name, float(np.degrees(np.arcsin(np.sin(np.radians(INCLINATION)) * np.sin(u))))))
    return out


# %% [markdown]
# ## Step 6: a failure case. Is the phase the Earth's shadow?
# If it were, the shadow would have to fall on the Moon at quarter. The Earth's shadow is
# a cone pointing straight away from the Sun; at the Moon's distance its dark core (umbra) has
# radius  R_E - d (R_S - R_E) / D_sun. At quarter the Moon is 384400 km *sideways* from the
# line through the Sun and the Earth, far outside the shadow.

# %%
def umbra_radius_km(distance_km=MOON_DIST_KM):
    return R_EARTH - distance_km * (R_SUN - R_EARTH) / SUN_DIST_KM


def moon_offset_from_shadow_axis_km(elong_deg):
    """Distance from the Moon's centre to the line from the Sun through the Earth (the shadow axis),
    measured sideways, for the Moon on the opposite side (elongation near 180)."""
    return MOON_DIST_KM * abs(np.sin(np.radians(elong_deg)))


def shadow_could_touch(elong_deg):
    return bool(np.cos(np.radians(elong_deg)) < 0
                and moon_offset_from_shadow_axis_km(elong_deg) < umbra_radius_km() + R_MOON)


# %% [markdown]
# ## Step 7: mini-project, a year table for one latitude
# For a chosen latitude, on chosen dates: day length, noon Sun height and Moon phase.

# %%
def sun_declination(d):
    lam = np.radians(280.460 + 0.9856474 * d + 1.915 * np.sin(np.radians(357.528 + 0.9856003 * d))
                     + 0.020 * np.sin(np.radians(2 * (357.528 + 0.9856003 * d))))
    return float(np.degrees(np.arcsin(np.sin(np.radians(TILT)) * np.sin(lam))))


def day_length_hours(lat, decl):
    f = np.radians(np.clip(lat, -89.999, 89.999))
    return float(24.0 * np.arccos(np.clip(-np.tan(f) * np.tan(np.radians(decl)), -1.0, 1.0)) / np.pi)


def phase_label(elong_deg):
    names = ["new", "waxing crescent", "first quarter", "waxing gibbous",
             "full", "waning gibbous", "last quarter", "waning crescent"]
    return names[int(((elong_deg + 22.5) % 360.0) // 45.0) % 8]


def year_table(lat, year, dates):
    """Rows (date, day length in h, noon Sun height in deg, Moon lit fraction, phase name), at 12:00 UT."""
    rows = []
    for (m, dd) in dates:
        d = days_since_j2000(year, m, dd, 12.0)
        decl = sun_declination(d)
        D = float(mean_elongation(d))
        rows.append((dt.date(year, m, dd), day_length_hours(lat, decl), 90.0 - abs(lat - decl),
                     illuminated_fraction(180.0 - D), phase_label(D)))
    return rows


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("phase angle at elongation 0, 90, 180:", [round(phase_angle_deg(x), 2) for x in (0, 90, 180)])
    print("lit fraction at those:", [round(illuminated_fraction(phase_angle_deg(x)), 4) for x in (0, 90, 180)])
    print("synodic month from 27.321662 and 365.25636:", round(synodic_from(), 4))
    cal = phase_calendar(2026)
    for when, name in cal:
        if name == "full Moon":
            print("full Moon (mean):", when.strftime("%Y-%m-%d %H:%M"))
    rises = moonrise_times(0.0, 8)
    print("moonrise delays (minutes):", np.round(np.diff(rises) * 60 - 24 * 60, 1))
    print("eclipse-possible share: analytic", round(fraction_near_node(), 4), "Monte Carlo", round(fraction_near_node_mc(), 4))
    near = [(w.strftime("%m-%d"), n) for w, n, b in syzygy_latitudes(2026) if abs(b) < latitude_limit_deg()]
    print("2026 new/full Moons within the latitude limit:", near)
    print("umbra radius at the Moon (km):", round(umbra_radius_km(), 0), "; Moon sideways offset at quarter (km):",
          round(moon_offset_from_shadow_axis_km(90.0), 0))
    rows = year_table(40.0, 2026, [(m, 1) for m in range(1, 13)] + [(6, 21), (12, 21)])
    for r in rows:
        print(f"{r[0]}  day {r[1]:5.2f} h  noon {r[2]:5.1f} deg  Moon {r[3]:.2f} {r[4]}")

    # figure 1: the phase fraction through the month
    D = np.linspace(0, 360, 361)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(D, [illuminated_fraction(phase_angle_deg(x)) for x in D], label="(1 + cos i) / 2")
    ax.set_xlabel("elongation Sun-Earth-Moon D (degrees)")
    ax.set_ylabel("bright fraction of the disc")
    ax.set_title("Illuminated fraction: 0 at new, 0.5 at quarter, 1 at full")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "phase_fraction.png", dpi=120)

    # figure 2: the calendar for 2026
    fig2, ax2 = plt.subplots(figsize=(9, 3.2))
    t0 = dt.datetime(2026, 1, 1)
    for when, name in cal:
        x = (when - t0).total_seconds() / 86400.0
        ax2.plot([x], [{"new Moon": 0, "first quarter": 0.5, "full Moon": 1, "last quarter": 0.5}[name]], "o",
                 color={"new Moon": "k", "first quarter": "tab:blue", "full Moon": "tab:orange", "last quarter": "tab:green"}[name])
    ax2.set_xlabel("day of 2026 (0 = 1 January)")
    ax2.set_ylabel("bright fraction")
    ax2.set_title("Mean phase calendar 2026: black new, orange full, blue/green quarters")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "calendar_2026.png", dpi=120)

    # figure 3: moonrise time through the month
    fig3, ax3 = plt.subplots(figsize=(6.5, 4))
    r = moonrise_times(0.0, 28)
    ax3.plot(np.arange(len(r)), r % 24.0, "o-", ms=3)
    ax3.set_xlabel("day after new Moon")
    ax3.set_ylabel("time of moonrise (hours after midnight)")
    ax3.set_title("Moonrise slips later by about 50 minutes a day")
    ax3.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "moonrise.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
