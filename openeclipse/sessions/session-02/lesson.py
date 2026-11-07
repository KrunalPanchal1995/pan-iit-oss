"""Session 2 (Level 2): shadow cones and the eclipse limit.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: shadow cones and the eclipse limit
# **SAFETY.** Never look at the Sun without certified eclipse glasses, even during a partial
# eclipse. Everything below is calculation only.
#
# **A. Real-world problem.** Why is a total solar eclipse such a rare sight at any one place?
# The Moon's dark shadow is a thin cone whose tip only just reaches the Earth, and the Moon
# passes between the Sun and the Earth only when it is close to the plane of the Earth's
# orbit. Today we compute the cone, the width of the dark track, and how near a "node" the
# Moon must be.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R_SUN = 696000.0         # km
R_MOON = 1737.0          # km
R_EARTH = 6378.0         # km, equatorial radius
D_SUN = 1.496e8          # km, Sun-Moon distance is taken equal to this (error is under 0.3 percent)
D_MOON = 384400.0        # km, mean
D_MOON_PERIGEE = 356500.0    # km, a close Moon
D_MOON_APOGEE = 406700.0     # km, a far Moon
INCLINATION = 5.145      # degrees, tilt of the Moon's orbit against the ecliptic
SYNODIC = 29.530589      # days, new moon to new moon
DRACONIC_YEAR = 346.62   # days, the Sun returns to the same node
TROPICAL_YEAR = 365.2422   # days


# %% [markdown]
# ## Step 1: angular sizes (check the "coincidence")
# Sun: diameter 1.3927e6 km at 1.496e8 km. Moon: diameter 3474 km at 384400 km.
# The angle across a disc is 2 arctan(radius / distance).

# %%
def angular_diameter_deg(diameter_km, distance_km):
    return float(np.degrees(2 * np.arctan(diameter_km / 2 / distance_km)))


# %% [markdown]
# ## Step 2: the umbra (dark cone) by similar triangles
# Draw the Sun (radius R) and Moon (radius r) with a line from the top of the Sun to the
# top of the Moon, continued until it meets the axis at the tip, a distance L behind the
# Moon. The small triangle (tip to Moon) and the big triangle (tip to Sun) are similar:
# r / L = R / (L + D), so r (L + D) = R L and
#
#     L = D r / (R - r)        (D = Sun-Moon distance, L measured from the Moon)
#
# Beyond the tip, the cone opens again: that region is the *antumbra*, where an observer
# sees a ring of Sun (annular eclipse). The *penumbra* is the wider cone from the other pair
# of tangent lines: its radius grows as r + s (R + r) / D at distance s behind the Moon.

# %%
def umbra_length(sun_radius=R_SUN, moon_radius=R_MOON, sun_moon_distance=D_SUN):
    return float(sun_moon_distance * moon_radius / (sun_radius - moon_radius))


def umbra_radius_at(s, sun_radius=R_SUN, moon_radius=R_MOON, sun_moon_distance=D_SUN):
    """Signed radius (km) of the dark shadow at distance s behind the Moon.
    Positive: inside the umbra (total). Negative: beyond the tip, the antumbra (annular);
    the magnitude is the radius of the antumbra circle."""
    L = umbra_length(sun_radius, moon_radius, sun_moon_distance)
    return float(moon_radius * (L - s) / L)


def penumbra_radius_at(s, sun_radius=R_SUN, moon_radius=R_MOON, sun_moon_distance=D_SUN):
    return float(moon_radius + s * (sun_radius + moon_radius) / sun_moon_distance)


# %% [markdown]
# ## Step 3: total or annular? the width of the path
# The ground nearest the Moon is at distance s = d - R_EARTH (the sub-lunar point).
# If L is longer than s the tip is beyond the ground: total. Otherwise annular.
# The dark circle on the ground has radius |umbra_radius_at(s)|, so the path is about
# twice that wide (the real path is somewhat wider when the Sun is low, because the ground
# is tilted against the shadow; this model ignores that).

# %%
def ground_distance(moon_distance):
    return moon_distance - R_EARTH


def eclipse_kind_overhead(moon_distance, sun_moon_distance=D_SUN):
    r = umbra_radius_at(ground_distance(moon_distance), sun_moon_distance=sun_moon_distance)
    return "total" if r > 0 else "annular"


def path_width_km(moon_distance, sun_moon_distance=D_SUN):
    return float(2 * abs(umbra_radius_at(ground_distance(moon_distance), sun_moon_distance=sun_moon_distance)))


def critical_total_distance(sun_moon_distance=D_SUN):
    """Largest Earth-Moon distance (km) for which the tip reaches the sub-lunar ground."""
    return umbra_length(sun_moon_distance=sun_moon_distance) + R_EARTH


def totality_minutes(moon_distance, equator_rotation_kms=0.465):
    """Rough duration (minutes) of totality at the equator: path width / shadow speed over ground."""
    v = 2 * np.pi * moon_distance / (27.321661 * 86400.0) - equator_rotation_kms
    return float(path_width_km(moon_distance) / v / 60.0)


def earth_umbra_radius_at_moon(moon_distance=D_MOON, sun_moon_distance=D_SUN):
    """Radius (km) of the Earth's dark shadow where the Moon crosses it (lunar eclipse)."""
    return float(R_EARTH - moon_distance * (R_SUN - R_EARTH) / sun_moon_distance)


# %% [markdown]
# ## Step 4: the eclipse limit (why not every month?)
# The Moon's orbit is tilted by i = 5.145 degrees. Seen from the Earth the Moon's ecliptic
# latitude is  sin(beta) = sin(i) sin(u), where u is the angle along the orbit measured from
# the ascending node (the point where the Moon crosses the ecliptic going north).
# At new moon the Moon is in the Sun's direction, so the Sun-Moon separation equals |beta|.
#
# A partial eclipse is visible somewhere if the shadow's axis passes within R_EARTH plus the
# penumbra radius of the Earth's centre. In angles this is
#
#     |beta| < pi + s_sun + s_moon        (pi = parallax of the Moon = arcsin(R_EARTH / d))
#
# (s = angular radii of the Sun and the Moon). A *central* eclipse (the axis hits the Earth's
# disc) needs only |beta| < pi. Solving sin(beta) = sin(i) sin(u) for u:
#
#     u_limit = arcsin( sin(beta_limit) / sin(i) )

# %%
def parallax_deg(moon_distance):
    return float(np.degrees(np.arcsin(R_EARTH / moon_distance)))


def beta_limit_partial(moon_distance, sun_distance=D_SUN):
    s_sun = np.degrees(np.arctan(R_SUN / sun_distance))
    s_moon = np.degrees(np.arctan(R_MOON / moon_distance))
    return float(parallax_deg(moon_distance) + s_sun + s_moon)


def beta_limit_central(moon_distance):
    return parallax_deg(moon_distance)


def node_limit_deg(beta_limit, inclination=INCLINATION):
    """Largest angle from the node (degrees) at which the Moon can still be within beta_limit."""
    ratio = np.sin(np.radians(beta_limit)) / np.sin(np.radians(inclination))
    if ratio >= 1.0:          # the orbit never gets that far from the ecliptic: every angle qualifies
        return 90.0
    return float(np.degrees(np.arcsin(ratio)))


def limit_range():
    """(largest partial limit, certain partial limit, largest central limit), degrees from the node.
    Largest: Moon at perigee 356400 km, Sun at perihelion 1.471e8 km, orbit tilt 5.0 degrees.
    Certain: Moon at apogee 406700 km, Sun at aphelion 1.521e8 km, tilt 5.3 degrees."""
    big = node_limit_deg(beta_limit_partial(356400.0, 1.471e8), 5.0)
    sure = node_limit_deg(beta_limit_partial(406700.0, 1.521e8), 5.3)
    central = node_limit_deg(beta_limit_central(356400.0), 5.0)
    return big, sure, central


def node_limit_numeric(beta_limit, inclination=INCLINATION):
    """Same limit by brute force: move a Moon along its tilted orbit, build 3-D unit vectors,
    put the Sun at the Moon's ecliptic longitude (new moon) and bisect on the separation."""
    inc = np.radians(inclination)

    def separation(u):
        moon = np.array([np.cos(u), np.cos(inc) * np.sin(u), np.sin(inc) * np.sin(u)])
        lon = np.arctan2(moon[1], moon[0])
        sun = np.array([np.cos(lon), np.sin(lon), 0.0])
        return np.degrees(np.arccos(np.clip(moon @ sun, -1.0, 1.0)))

    lo, hi = 0.0, np.pi / 2
    for _ in range(60):
        mid = (lo + hi) / 2
        if separation(mid) < beta_limit:
            lo = mid
        else:
            hi = mid
    return float(np.degrees(lo))


# %% [markdown]
# ## Step 5: eclipse seasons (a design problem)
# The nodes drift slowly, so the Sun returns to the same node every 346.62 days (the
# draconic year), not every 365.24 days. The Sun passes a node twice per draconic year:
# eclipse seasons are 346.62 / 2 = 173.31 days apart. The Sun moves along the ecliptic,
# relative to the node, at 360 / 346.62 degrees per day, so a season in which the Sun stays
# within +/- limit of a node lasts 2 limit / (that rate) days.

# %%
def season_spacing_days():
    return DRACONIC_YEAR / 2.0


def sun_node_rate_deg_per_day():
    return 360.0 / DRACONIC_YEAR


def season_length_days(limit_deg):
    return float(2 * limit_deg / sun_node_rate_deg_per_day())


def seasons_per_tropical_year():
    return TROPICAL_YEAR / season_spacing_days()


def seasons_drift_days_per_year():
    """How many days earlier each year's eclipse seasons arrive."""
    return TROPICAL_YEAR - DRACONIC_YEAR


# %% [markdown]
# ## Step 6: see it
# Left: signed shadow radius on the ground against the Moon's distance. Right: the limit.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"Sun {angular_diameter_deg(1.3927e6, 1.496e8):.3f} deg, Moon {angular_diameter_deg(3474, 384400):.3f} deg")
    L = umbra_length()
    print(f"umbra length L = {L:.0f} km; mean ground distance {ground_distance(D_MOON):.0f} km")
    print(f"total if Earth-Moon distance below {critical_total_distance():.0f} km")
    for name, d in (("perigee", D_MOON_PERIGEE), ("mean", D_MOON), ("apogee", D_MOON_APOGEE)):
        print(f"{name:8s} d={d:.0f}: {eclipse_kind_overhead(d):8s} path width {path_width_km(d):6.1f} km")
    print(f"penumbra radius at the Earth {penumbra_radius_at(D_MOON):.0f} km")
    print(f"limits (mean Moon): partial {node_limit_deg(beta_limit_partial(D_MOON)):.1f} deg, "
          f"central {node_limit_deg(beta_limit_central(D_MOON)):.1f} deg")

    d = np.linspace(354000, 410000, 200)
    r = [umbra_radius_at(ground_distance(x)) for x in d]
    fig, ax = plt.subplots(figsize=(6.4, 4))
    ax.plot(d / 1000, r, color="tab:blue")
    ax.axhline(0, color="gray", lw=0.8)
    ax.axvline(critical_total_distance() / 1000, color="tab:red", ls=":")
    ax.set_xlabel("Earth-Moon distance (thousand km)")
    ax.set_ylabel("shadow radius on the ground (km); negative = ring")
    ax.set_title("Total (above 0) or annular (below 0)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "umbra_on_ground.png", dpi=120)

    u = np.linspace(-30, 30, 400)
    beta = np.degrees(np.arcsin(np.sin(np.radians(INCLINATION)) * np.sin(np.radians(u))))
    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    ax2.plot(u, beta, color="tab:blue", label="Moon's ecliptic latitude")
    bp, bc = beta_limit_partial(D_MOON), beta_limit_central(D_MOON)
    for b, name, c in ((bp, "partial limit", "tab:orange"), (bc, "central limit", "tab:green")):
        ax2.axhline(b, color=c, ls="--")
        ax2.axhline(-b, color=c, ls="--", label=name)
    ax2.axvspan(-node_limit_deg(bp), node_limit_deg(bp), color="gold", alpha=0.15)
    ax2.set_xlabel("angle from the node (degrees)")
    ax2.set_ylabel("Moon's ecliptic latitude (degrees)")
    ax2.set_title("An eclipse needs the Moon near a node")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "eclipse_limit.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
