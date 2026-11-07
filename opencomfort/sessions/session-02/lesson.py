"""Session 2 (Level 2): size a sunshade from the sun's position, and compute air flow through windows.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the sun's path, the overhang, and the breeze
# **A. Real-world problem.** In Session 1 we simply *assumed* that a shade blocks 80 percent
# of the sun and that open windows give 10 air changes per hour. A builder needs real numbers:
# how deep must the concrete sunshade (chajja) over a window be, and how much air will two
# open windows actually move on a breezy evening? Both answers come from geometry and a few
# textbook formulas.
#
# **Plan.** (1) where the sun is (altitude and azimuth), (2) how much sun reaches a wall,
# (3) the shadow of an overhang, (4) wind-driven cross ventilation, (5) stack (buoyancy)
# ventilation, (6) back to air changes per hour.
#
# **Model.** Clear sky, solar time, flat ground, a long horizontal overhang. Simplified
# teaching formulas; not a design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81                    # m/s2
CHENNAI_LAT = 13.08         # degrees north
WALL_AZ = {"north": 0.0, "east": 90.0, "south": 180.0, "west": 270.0}   # direction the wall faces, clockwise from north


# %% [markdown]
# ## Step 1: where is the sun?
# Three angles fix the sun's position for a place at latitude phi:
#
# * **declination** delta: how far north of the equator the sun is overhead today,
#   `delta = 23.45 sin(360 (284 + n) / 365)` degrees, n = day of the year (1 to 365)
# * **hour angle** omega = 15 (t - 12) degrees, t = solar time in hours (noon = 0)
# * **altitude** alpha above the horizon: `sin(alpha) = sin(phi) sin(delta) + cos(phi) cos(delta) cos(omega)`
#
# The **azimuth** (compass direction, clockwise from north) follows from the same angles.
# In Chennai (13 N) the sun in May passes *north* of overhead at noon, so a south window
# gets almost no direct sun then. Surprising, but true for anywhere in the tropics.

# %%
def declination(day):
    """Solar declination (degrees) for day of year 1..365 (Cooper's formula)."""
    if not (1 <= day <= 366):
        raise ValueError("day of year must be 1 to 366")
    return 23.45 * np.sin(np.radians(360.0 * (284 + day) / 365.0))


def sun_position(lat, day, solar_hour):
    """(altitude, azimuth) in degrees. Azimuth clockwise from north (90 = east, 270 = west)."""
    d, phi = np.radians(declination(day)), np.radians(lat)
    w = np.radians(15.0 * (np.asarray(solar_hour, float) - 12.0))
    sin_alt = np.sin(phi) * np.sin(d) + np.cos(phi) * np.cos(d) * np.cos(w)
    alt = np.arcsin(np.clip(sin_alt, -1, 1))
    # components of the sun direction: east, north, up
    east = -np.cos(d) * np.sin(w)
    north = np.cos(phi) * np.sin(d) - np.sin(phi) * np.cos(d) * np.cos(w)
    az = np.degrees(np.arctan2(east, north)) % 360.0
    return np.degrees(alt), az


# %% [markdown]
# ## Step 2: how much sun hits the wall?
# On a clear day the beam (direct) sunshine on a surface facing the sun is roughly
# `I_DN = A exp(-B / sin(alpha))`: the lower the sun, the more air it shines through.
# We use the illustrative clear-sky constants A = 1100 W/m2 and B = 0.18.
#
# A vertical wall facing azimuth `psi` gets `I_DN cos(theta)` with
# `cos(theta) = cos(alpha) cos(gamma)`, where `gamma = sun azimuth - psi` is the
# wall-solar azimuth. If cos(theta) < 0 the sun is behind the wall.
# The wall also gets diffuse light from the sky and the ground; we take
# `I_diffuse = 0.5 I_DN (C + rho_g (sin(alpha) + C))` with C = 0.12 and ground reflectance 0.2.

# %%
def beam_normal(alt_deg, a=1100.0, b=0.18):
    """Clear-sky beam irradiance on a surface facing the sun (W/m2); 0 below the horizon."""
    s = np.sin(np.radians(np.asarray(alt_deg, float)))
    return np.where(s > 0.01, a * np.exp(-b / np.maximum(s, 0.01)), 0.0)


def wall_solar_azimuth(sun_az, wall_az):
    """Angle between the sun's compass direction and the wall's outward normal, -180..180 degrees."""
    return (np.asarray(sun_az, float) - wall_az + 180.0) % 360.0 - 180.0


def cos_incidence_vertical(alt_deg, sun_az, wall_az):
    """cos(theta) of the beam on a vertical wall; negative means the sun is behind the wall."""
    a, g = np.radians(alt_deg), np.radians(wall_solar_azimuth(sun_az, wall_az))
    return np.cos(a) * np.cos(g)


def diffuse_vertical(alt_deg, c=0.12, rho_g=0.2):
    """Sky plus ground-reflected irradiance on a vertical wall (W/m2), clear sky."""
    idn = beam_normal(alt_deg)
    s = np.maximum(np.sin(np.radians(np.asarray(alt_deg, float))), 0.0)
    return 0.5 * idn * (c + rho_g * (s + c))


# %% [markdown]
# ## Step 3: the shadow of an overhang
# Look at the wall from the side. The sun's rays make the **profile angle** Omega with the
# horizontal, where `tan(Omega) = tan(alpha) / cos(gamma)`. An overhang that sticks out a
# depth D, mounted a gap G above the window top, throws a shadow that reaches
# `D tan(Omega)` down the wall. On a window of height H the shaded fraction is
#
#     f = clip((D tan(Omega) - G) / H, 0, 1)
#
# (for an overhang much wider than the window). A high sun (large Omega) is easy to block
# with a short overhang; a low sun from the west in the late afternoon is very hard to block.

# %%
def profile_angle(alt_deg, sun_az, wall_az):
    """Vertical shadow angle (degrees) seen in section through the wall. 90 if sun is overhead-on."""
    c = np.cos(np.radians(wall_solar_azimuth(sun_az, wall_az)))
    t = np.tan(np.radians(alt_deg))
    with np.errstate(divide="ignore", invalid="ignore"):
        omega = np.degrees(np.arctan2(t, c))
    return omega


def overhang_shaded_fraction(depth, gap, height, alt_deg, sun_az, wall_az):
    """Fraction (0..1) of the window height in the overhang's shadow. 1 when the sun is behind the wall."""
    if depth < 0 or gap < 0 or height <= 0:
        raise ValueError("need depth >= 0, gap >= 0, height > 0")
    om = np.radians(profile_angle(alt_deg, sun_az, wall_az))
    behind = cos_incidence_vertical(alt_deg, sun_az, wall_az) <= 0
    f = np.clip((depth * np.tan(np.clip(om, 0, np.radians(89.999))) - gap) / height, 0.0, 1.0)
    return np.where(behind, 1.0, f)


def depth_for_full_shade(gap, height, alt_deg, sun_az, wall_az):
    """Overhang depth (m) that just shades the whole window height at this sun position."""
    om = np.radians(profile_angle(alt_deg, sun_az, wall_az))
    if not (0 < om < np.pi / 2):
        raise ValueError("sun is behind the wall or below the horizon")
    return (gap + height) / np.tan(om)


def window_irradiance(alt_deg, sun_az, wall_az, depth=0.0, gap=0.3, height=1.5):
    """Sun on the window glass (W/m2): unshaded beam part plus diffuse (overhang blocks only beam)."""
    alt_deg = np.asarray(alt_deg, float)
    cos_t = np.maximum(cos_incidence_vertical(alt_deg, sun_az, wall_az), 0.0)
    f = overhang_shaded_fraction(depth, gap, height, alt_deg, sun_az, wall_az)
    up = alt_deg > 0
    return np.where(up, beam_normal(alt_deg) * cos_t * (1.0 - f) + diffuse_vertical(alt_deg), 0.0)


# %% [markdown]
# ## Step 4: wind-driven cross ventilation
# Wind pushes on the windward wall (pressure coefficient about +0.5) and sucks on the
# leeward wall (about -0.3). With openings on both sides, air flows through. The volume flow is
#
#     Q = Cd A_eff U sqrt(dCp)          1 / A_eff^2 = 1 / A1^2 + 1 / A2^2
#
# Cd about 0.6 is the discharge coefficient of an opening, U the wind speed (m/s) at roof
# height, dCp the difference of pressure coefficients. Two openings in series behave like one
# smaller opening A_eff. With only one window (single-sided) the flow is much weaker; a
# rule of thumb is Q = 0.025 A U.

# %%
def effective_area(a1, a2):
    """Effective area (m2) of two openings in series."""
    if a1 <= 0 or a2 <= 0:
        raise ValueError("opening areas must be positive")
    return 1.0 / np.sqrt(1.0 / a1 ** 2 + 1.0 / a2 ** 2)


def cross_vent_flow(a1, a2, wind, dcp=0.8, cd=0.6):
    """Wind-driven cross ventilation flow (m3/s)."""
    if wind < 0 or dcp < 0:
        raise ValueError("wind speed and dCp must not be negative")
    return cd * effective_area(a1, a2) * wind * np.sqrt(dcp)


def single_sided_flow(area, wind):
    """Single-sided ventilation rule of thumb (m3/s): 0.025 A U."""
    return 0.025 * area * wind


# %% [markdown]
# ## Step 5: stack ventilation (warm air rises)
# Warm indoor air is lighter than cooler outdoor air. With a low opening and a high opening a
# vertical distance h apart, the indoor air column pushes air out at the top and draws it in
# at the bottom:
#
#     Q = Cd A_eff sqrt(2 g h dT / T_mean)      (T in kelvin)
#
# Stack flow needs indoor warmer than outdoor, so it helps most at night. Wind and stack
# combine roughly as Q = sqrt(Q_wind^2 + Q_stack^2).

# %%
def stack_flow(a_low, a_high, height, t_in_c, t_out_c, cd=0.6):
    """Buoyancy-driven flow (m3/s) through a low and a high opening `height` metres apart."""
    if height < 0:
        raise ValueError("height must not be negative")
    dt = abs(t_in_c - t_out_c)
    t_mean = 0.5 * (t_in_c + t_out_c) + 273.15
    return cd * effective_area(a_low, a_high) * np.sqrt(2.0 * G * height * dt / t_mean)


def combined_flow(q_wind, q_stack):
    """Wind and stack flows added in quadrature (m3/s)."""
    return float(np.hypot(q_wind, q_stack))


def ach_from_flow(q, volume):
    """Air changes per hour from flow (m3/s) and room volume (m3)."""
    if volume <= 0:
        raise ValueError("volume must be positive")
    return 3600.0 * q / volume


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    day = 105   # 15 April
    print(f"declination on day {day}: {declination(day):.2f} degrees")
    alt, az = sun_position(CHENNAI_LAT, day, 15.0)
    print(f"Chennai, 15 April, 3 pm solar time: altitude {alt:.1f}, azimuth {az:.1f}")
    for wall in ("west", "south"):
        om = profile_angle(alt, az, WALL_AZ[wall])
        print(f"  {wall} window: wall-solar azimuth {wall_solar_azimuth(az, WALL_AZ[wall]):.1f}, profile angle {om:.1f}")
    print(f"  overhang depth to fully shade a 1.5 m west window (gap 0.3 m): {depth_for_full_shade(0.3, 1.5, alt, az, WALL_AZ['west']):.2f} m")

    # Figure 1: sun on a west and a south window over the day, with and without a 0.6 m overhang
    hours = np.linspace(6, 18, 241)
    alt_h, az_h = sun_position(CHENNAI_LAT, day, hours)
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    for wall, col in (("west", "#d9534f"), ("south", "#2a9d8f")):
        for depth, ls in ((0.0, "-"), (0.6, "--")):
            irr = window_irradiance(alt_h, az_h, WALL_AZ[wall], depth=depth)
            daily = np.trapezoid(irr, hours) if hasattr(np, "trapezoid") else np.trapz(irr, hours)
            ax.plot(hours, irr, color=col, ls=ls, lw=2, label=f"{wall}, overhang {depth:.1f} m ({daily / 1000:.2f} kWh/m2 per day)")
            print(f"{wall:5s} window, overhang {depth:.1f} m: daily sun on glass {daily / 1000:.2f} kWh/m2")
    ax.set_xlabel("solar time (h)")
    ax.set_ylabel("sun on the window glass (W/m2)")
    ax.set_title("Chennai, 15 April: a west window gets the low afternoon sun")
    ax.set_xlim(6, 18)
    ax.set_ylim(0, 800)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "window_sun.png", dpi=120)

    # Figure 2: shaded fraction against overhang depth, and air changes against wind speed
    fig2, (axa, axb) = plt.subplots(1, 2, figsize=(10, 4.2))
    depths = np.linspace(0, 1.5, 151)
    for hour, col in ((12.0, "#264653"), (14.0, "#2a9d8f"), (15.0, "#e9a23b"), (16.0, "#d9534f")):
        a_, z_ = sun_position(CHENNAI_LAT, day, hour)
        f = [overhang_shaded_fraction(d, 0.3, 1.5, a_, z_, WALL_AZ["west"]) for d in depths]
        axa.plot(depths, f, color=col, lw=2, label=f"{hour:.0f}:00, profile angle {profile_angle(a_, z_, WALL_AZ['west']):.0f} deg")
    axa.set_xlabel("overhang depth D (m)")
    axa.set_ylabel("shaded fraction of the window (no unit)")
    axa.set_title("West window, 1.5 m high, gap 0.3 m")
    axa.set_ylim(0, 1.05)
    axa.grid(alpha=0.3)
    axa.legend(fontsize=8)
    u = np.linspace(0, 5, 101)
    vol = 48.0
    axb.plot(u, [ach_from_flow(cross_vent_flow(0.5, 0.5, x), vol) for x in u], color="#2a9d8f", lw=2, label="cross ventilation, two 0.5 m2 openings")
    axb.plot(u, [ach_from_flow(single_sided_flow(1.0, x), vol) for x in u], color="#d9534f", lw=2, label="single-sided, one 1.0 m2 opening")
    qs = stack_flow(0.5, 0.5, 2.0, 32.0, 28.0)
    axb.axhline(ach_from_flow(qs, vol), color="#e9a23b", ls="--", label=f"stack only, h = 2 m, dT = 4 K ({ach_from_flow(qs, vol):.1f} ACH)")
    axb.set_xlabel("wind speed U (m/s)")
    axb.set_ylabel("air changes per hour, ACH (1/h)")
    axb.set_title("48 m3 room: cross ventilation wins")
    axb.grid(alpha=0.3)
    axb.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "shade_and_flow.png", dpi=120)

    q = cross_vent_flow(0.5, 0.5, 1.5)
    print(f"cross ventilation, 2 x 0.5 m2, U = 1.5 m/s: Q = {q:.4f} m3/s = {ach_from_flow(q, vol):.1f} ACH")
    print(f"single-sided, 1.0 m2, U = 1.5 m/s: {ach_from_flow(single_sided_flow(1.0, 1.5), vol):.1f} ACH")
    print(f"stack, 2 x 0.5 m2, h = 2 m, 32 C in, 28 C out: Q = {qs:.4f} m3/s = {ach_from_flow(qs, vol):.1f} ACH")

# %% [markdown]
# ## Where this stops
# Each number here is a snapshot for one hour. A real room has heavy walls and a floor that
# soak up heat by day and give it back at night. Session 3 steps through a whole day, hour by
# hour, with this sunshine and this air flow, and finds the design that keeps the room cool.
