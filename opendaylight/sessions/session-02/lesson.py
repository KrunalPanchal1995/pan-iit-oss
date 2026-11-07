"""Session 2 (Level 2): sunlight on a window, the overhang, and the solar heat gain.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: sunlight on a window, shading and solar heat gain
# **A. Real-world problem.** A west-facing window in Chennai turns a room into an oven in the
# afternoon, while a south window in Delhi brings welcome winter sun. How much sunlight falls
# on a window of a given orientation, how deep must an overhang (chajja) be to shade it in
# summer but not in winter, and how many watts of solar heat come through the glass?
#
# **Plan.** (1) the angle between the sun and a wall, (2) the vertical shadow angle and the
# overhang rule, (3) clear-sky sunlight (Meinel model), (4) solar heat gain through glass,
# (5) whole-day totals for each facade.
#
# **Model.** Sun position from Session 1 (solar time). Clear sky, direct beam plus a simple
# diffuse part, no ground reflection. The overhang is as long as the window is wide (no side
# leaks). A simplified teaching model, not a design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
TILT = 23.45            # degrees
SOLAR_CONST = 1353.0    # W/m2, value used in the Meinel model
DIFFUSE_C = 0.10        # clear-sky diffuse on a horizontal surface as a share of the beam
SHGC = 0.6              # solar heat gain coefficient of the glazing (no unit)


def declination(n):
    """Solar declination (degrees), Cooper's formula (Session 1)."""
    return TILT * np.sin(np.radians(360.0 * (284.0 + np.asarray(n, float)) / 365.0))


def sun_position(lat, decl, hour):
    """(altitude, azimuth) in degrees, azimuth clockwise from north (Session 1)."""
    phi, d = np.radians(lat), np.radians(decl)
    h = np.radians(15.0 * (np.asarray(hour, float) - 12.0))
    up = np.sin(d) * np.sin(phi) + np.cos(d) * np.cos(phi) * np.cos(h)
    east = -np.cos(d) * np.sin(h)
    north = np.sin(d) * np.cos(phi) - np.cos(d) * np.sin(phi) * np.cos(h)
    return np.degrees(np.arcsin(np.clip(up, -1, 1))), np.degrees(np.arctan2(east, north)) % 360.0


# %% [markdown]
# ## Step 1: the angle between the sun and a wall
# A vertical wall "faces" the compass direction psi (the direction of the outward normal:
# south = 180). With the sun at altitude alpha and azimuth A, the **wall-solar azimuth** is
# gamma = A - psi. The **angle of incidence** theta between the sun ray and the wall normal is
#
#     cos(theta) = cos(alpha) cos(gamma)
#
# If cos(theta) <= 0 the sun is behind the wall and no direct beam reaches the window.

# %%
def wall_solar_azimuth(sun_az, facing):
    """Sun azimuth relative to the wall normal, in -180 to 180 degrees."""
    return (np.asarray(sun_az, float) - facing + 180.0) % 360.0 - 180.0


def cos_incidence(alt, sun_az, facing):
    """cos(angle of incidence) on a vertical wall facing `facing` (degrees); 0 if the sun is behind it."""
    g = np.radians(wall_solar_azimuth(sun_az, facing))
    c = np.cos(np.radians(alt)) * np.cos(g)
    return np.where(np.asarray(alt) > 0, np.maximum(c, 0.0), 0.0)


# %% [markdown]
# ## Step 2: the vertical shadow angle and the overhang
# Look at the wall in section (a vertical cut through the window). The sun ray seen in this
# section makes the **vertical shadow angle** (VSA, also called profile angle) with the ground:
#
#     tan(VSA) = tan(alpha) / cos(gamma)
#
# An overhang of depth P, placed a gap G above a window of height H, throws a shadow that
# reaches P tan(VSA) below the overhang. So the shaded height of the window is
#
#     shaded = clamp( P tan(VSA) - G, 0, H )
#
# and the overhang shades the whole window when P >= (G + H) / tan(VSA).

# %%
def vertical_shadow_angle(alt, sun_az, facing):
    """Vertical shadow angle (degrees) in the section through the wall. 90 if the sun is edge-on."""
    c = np.cos(np.radians(wall_solar_azimuth(sun_az, facing)))
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.tan(np.radians(alt)) / np.where(c > 1e-9, c, np.nan)
    return np.where(c > 1e-9, np.degrees(np.arctan(t)), 90.0)


def sunlit_fraction(alt, sun_az, facing, depth, height, gap=0.0):
    """Fraction (0 to 1) of the window height in direct sun below an overhang of `depth` m."""
    if height <= 0 or depth < 0 or gap < 0:
        raise ValueError("need height > 0, depth >= 0, gap >= 0")
    vsa = vertical_shadow_angle(alt, sun_az, facing)
    shaded = np.clip(depth * np.tan(np.radians(np.minimum(vsa, 89.999))) - gap, 0.0, height)
    lit = 1.0 - shaded / height
    return np.where(cos_incidence(alt, sun_az, facing) > 0, lit, 0.0)


def overhang_for_full_shade(vsa, height, gap=0.0):
    """Smallest overhang depth (m) that shades the whole window for a given VSA (degrees)."""
    return (gap + height) / np.tan(np.radians(vsa))


# %% [markdown]
# ## Step 3: how strong is clear-sky sunlight?
# Sunlight crosses more air when the sun is low. The **air mass** is AM = 1 / sin(alpha). The
# Meinel clear-sky model gives the direct normal irradiance (W/m2 on a surface facing the sun):
#
#     DNI = 1353 x 0.7 ** (AM ** 0.678)
#
# The sky also sends diffuse light. We take the diffuse on a horizontal surface as 0.1 x DNI;
# a vertical wall sees half of the sky, so it gets 0.05 x DNI. (Simple teaching values.)

# %%
def dni(alt):
    """Clear-sky direct normal irradiance (W/m2), Meinel model; 0 when the sun is down."""
    alt = np.asarray(alt, float)
    s = np.sin(np.radians(np.maximum(alt, 1e-6)))
    return np.where(alt > 0, SOLAR_CONST * 0.7 ** ((1.0 / s) ** 0.678), 0.0)


def diffuse_vertical(alt):
    """Diffuse irradiance on a vertical wall (W/m2): half the sky times DIFFUSE_C x DNI."""
    return 0.5 * DIFFUSE_C * dni(alt)


# %% [markdown]
# ## Step 4: solar heat gain through the glass
# Glass lets part of the sunlight through and part of what it absorbs also flows in. The
# **solar heat gain coefficient** (SHGC) is the share that ends up inside as heat. For a window
# of width b and height H:
#
#     Q = SHGC x [ DNI cos(theta) x (sunlit area)  +  diffuse_vertical x (whole area) ]   (W)

# %%
def window_gain(lat, n, hour, facing, width, height, depth=0.0, gap=0.0, shgc=SHGC):
    """Solar heat gain (W) through a vertical window at solar time `hour` on day n."""
    alt, az = sun_position(lat, declination(n), hour)
    beam = dni(alt) * cos_incidence(alt, az, facing)
    lit = sunlit_fraction(alt, az, facing, depth, height, gap)
    return shgc * width * height * (beam * lit + diffuse_vertical(alt))


def daily_gain(lat, n, facing, width, height, depth=0.0, gap=0.0, shgc=SHGC, step=0.1):
    """Solar heat entering in one day (kWh), by adding hourly gains (rectangle rule)."""
    hours = np.arange(step / 2, 24.0, step)
    return float(np.sum(window_gain(lat, n, hours, facing, width, height, depth, gap, shgc)) * step / 1000.0)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    DELHI, CHENNAI = 28.6, 13.0
    b, H, G, P = 2.0, 1.5, 0.3, 0.5          # window 2 m x 1.5 m, gap 0.3 m, overhang 0.5 m

    # worked example numbers
    for n, name in ((355, "21 December"), (172, "21 June")):
        alt, az = sun_position(DELHI, declination(n), 12.0)
        print(f"Delhi {name} noon: alt {float(alt):.2f}, VSA {float(vertical_shadow_angle(alt, az, 180)):.2f}, "
              f"DNI {float(dni(alt)):.0f} W/m2, sunlit {float(sunlit_fraction(alt, az, 180, P, H, G)):.3f}, "
              f"gain {float(window_gain(DELHI, n, 12.0, 180, b, H, P, G)):.0f} W")

    # Figure 1: the overhang in section, summer and winter noon in Delhi
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.6), sharey=True)
    for ax, (n, name) in zip(axes, ((172, "21 June"), (355, "21 December"))):
        alt, az = sun_position(DELHI, declination(n), 12.0)
        vsa = float(vertical_shadow_angle(alt, az, 180))
        lit = float(sunlit_fraction(alt, az, 180, P, H, G))
        sill, head = 0.9, 0.9 + H
        y_edge = head + G - P * np.tan(np.radians(vsa))                         # where the shadow edge meets the wall
        ax.plot([0, 0], [0, 3.4], "k-", lw=3)                                  # wall
        ax.plot([0, 0], [sill, sill + lit * H], color="#e9a23b", lw=8, label="window in sun")
        ax.plot([0, 0], [sill + lit * H, head], color="#4ea8de", lw=8, label="window in shade")
        ax.plot([0, P], [head + G, head + G], "k-", lw=4)                      # overhang
        ax.plot([P + 2.0, P], [head + G + 2.0 * np.tan(np.radians(vsa)), head + G], color="#e9a23b", lw=1.5)
        ax.plot([P, 0], [head + G, max(y_edge, 0.0)], color="#e9a23b", lw=1.5, ls="--")
        ax.set_xlim(-0.3, 2.0)
        ax.set_ylim(0, 4.5)
        ax.set_aspect("equal")
        ax.set_title(f"{name} noon: VSA {vsa:.1f} deg\nsunlit {100 * lit:.0f}% of the window")
        ax.set_xlabel("distance out from the wall (m)")
        ax.grid(alpha=0.3)
    axes[1].legend(fontsize=8, loc="lower right")
    axes[0].set_ylabel("height above floor (m)")
    fig.suptitle("Delhi, south window 1.5 m tall, 0.5 m overhang 0.3 m above the window")
    fig.tight_layout()
    fig.savefig(OUT / "overhang_section.png", dpi=120)

    # Figure 2: daily solar heat gain by facade, Delhi and Chennai, June and December, no overhang
    faces = [("N", 0), ("E", 90), ("S", 180), ("W", 270)]
    fig2, axes2 = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, (lat, city) in zip(axes2, ((DELHI, "Delhi 28.6 N"), (CHENNAI, "Chennai 13 N"))):
        x = np.arange(4)
        june = [daily_gain(lat, 172, f, b, H) for _, f in faces]
        dec = [daily_gain(lat, 355, f, b, H) for _, f in faces]
        ax.bar(x - 0.18, june, 0.36, color="#d9534f", label="21 June")
        ax.bar(x + 0.18, dec, 0.36, color="#2a9d8f", label="21 December")
        ax.set_xticks(x)
        ax.set_xticklabels([f"{k}-facing" for k, _ in faces])
        ax.set_title(f"{city}: 2 m x 1.5 m window, no shading")
        ax.grid(alpha=0.3, axis="y")
        print(city, "June kWh/day:", [round(v, 2) for v in june], "December:", [round(v, 2) for v in dec])
    axes2[0].set_ylabel("solar heat gain per day (kWh)")
    axes2[0].legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "gain_by_facade.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Heat is only half of the story. A window is there for daylight. Session 3 adds the daylight
# factor, runs the room hour by hour for a whole year, checks the simulation, and finds the
# window size that uses the least energy for lighting plus cooling.
