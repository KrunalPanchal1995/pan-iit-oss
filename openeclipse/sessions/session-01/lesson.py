"""Session 1 (Level 1): two discs in the sky, one shadow on the ground.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: two discs in the sky, one shadow on the ground
# **SAFETY FIRST.** Looking at the Sun, even when most of it is covered by the Moon, can
# permanently damage your eyes. Only ever watch a solar eclipse through certified eclipse
# glasses (ISO 12312-2) or with a projection method taught by a qualified astronomer.
# This repo is about the maths. You do not need to look at the Sun to do any of it.
#
# **A. Real-world problem.** Once or twice a year, somewhere on Earth, the daytime sky goes
# dark for a few minutes. The Sun is about 400 times wider than the Moon, so why can the
# Moon hide it completely? And why does it happen only along a thin track on the ground?
#
# **Plan.** (1) measure how big the Sun and Moon look, (2) decide partial / total / annular
# from how well the two discs line up, (3) find how close the Moon must be for a total
# eclipse, (4) estimate how fast the Moon's shadow crosses the ground.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R_SUN = 696000.0        # km, radius of the Sun
R_MOON = 1737.0         # km, radius of the Moon
D_SUN = 1.496e8         # km, mean Earth-Sun distance
D_MOON = 384400.0       # km, mean Earth-Moon distance
SIDEREAL_MONTH = 27.321661   # days, the Moon's orbit round the Earth against the stars
R_EARTH = 6378.0        # km, equatorial radius of the Earth


# %% [markdown]
# ## Step 1: how big does a ball look?
# A ball of radius r at distance d covers an angle (its *angular radius*) with
# tan(angle) = r / d. For small angles the angle in radians is about r / d.
# Check with the Sun: 696000 / 149600000 = 0.00465 radians = 0.2666 degrees. The full disc
# is twice that: about 0.53 degrees. The Moon: 1737 / 384400 = 0.00452 radians = 0.259 degrees.
# The two discs look almost the same size. That is a coincidence of nature, and it is why
# eclipses are so striking.

# %%
def angular_radius_deg(radius_km, distance_km):
    """Angle (degrees) from the centre of a ball to its edge, as seen from distance_km away."""
    return float(np.degrees(np.arctan(radius_km / distance_km)))


def sky_radii(moon_distance=D_MOON, sun_distance=D_SUN):
    """(angular radius of the Sun, angular radius of the Moon) in degrees."""
    return angular_radius_deg(R_SUN, sun_distance), angular_radius_deg(R_MOON, moon_distance)


# %% [markdown]
# ## Step 2: line up the discs
# Let `sep` be the distance (in degrees of sky) between the centres of the two discs and
# `rs`, `rm` their angular radii. Then:
#
# - `sep >= rs + rm`: the discs do not even touch: **no eclipse**.
# - the Moon is bigger (rm >= rs) and `sep <= rm - rs`: the Sun is completely hidden:
#   **total**.
# - the Moon is smaller (rs > rm) and `sep <= rs - rm`: a ring of Sun is left: **annular**.
# - anything in between: **partial**.

# %%
def classify_sky(sep, rs, rm):
    if sep >= rs + rm:
        return "none"
    if rm >= rs and sep <= rm - rs:
        return "total"
    if rs > rm and sep <= rs - rm:
        return "annular"
    return "partial"


def covered_fraction(sep, rs, rm):
    """Fraction of the Sun's disc area hidden by the Moon's disc (overlap of two circles)."""
    if sep >= rs + rm:
        return 0.0
    if sep <= abs(rs - rm):
        return float(min(rm, rs) ** 2 / rs ** 2)
    a1 = np.arccos((sep ** 2 + rs ** 2 - rm ** 2) / (2 * sep * rs))
    a2 = np.arccos((sep ** 2 + rm ** 2 - rs ** 2) / (2 * sep * rm))
    lens = (rs ** 2 * (a1 - np.sin(2 * a1) / 2)) + (rm ** 2 * (a2 - np.sin(2 * a2) / 2))
    return float(lens / (np.pi * rs ** 2))


# %% [markdown]
# ## Step 3: how close must the Moon be?
# The Moon hides the whole Sun only if its disc is at least as big: rm >= rs, that is
# R_MOON / d >= tan(rs). So the Moon must be nearer than d = R_MOON / tan(rs).
# The Moon's distance changes during its orbit (about 356000 to 407000 km), so some
# eclipses are total and some are annular.

# %%
def critical_moon_distance(rs_deg=None):
    """Moon distance (km) at which the two discs have exactly the same size."""
    if rs_deg is None:
        rs_deg = angular_radius_deg(R_SUN, D_SUN)
    return float(R_MOON / np.tan(np.radians(rs_deg)))


# %% [markdown]
# ## Step 4: the shadow sweeps the ground
# The Moon orbits at speed v = 2 pi d / T. The tip of its shadow moves over the Earth at
# about that speed, minus the speed of the ground turning beneath it (up to 0.465 km/s at the
# equator). A shadow spot 200 km wide therefore passes over a place in a few minutes only.

# %%
def moon_speed_kms(distance_km=D_MOON):
    return float(2 * np.pi * distance_km / (SIDEREAL_MONTH * 86400.0))


def ground_speed_kms(distance_km=D_MOON, equator_rotation_kms=0.465):
    """Shadow speed over the ground at the equator (ground moves the same way as the Moon)."""
    return moon_speed_kms(distance_km) - equator_rotation_kms


# %% [markdown]
# ## Step 5: see it
# Top: the geometry from the side (not to scale). Bottom: four sky pictures.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    rs, rm = sky_radii()
    print(f"Sun angular diameter {2 * rs:.3f} deg, Moon angular diameter {2 * rm:.3f} deg")
    print(f"Sun / Moon diameter ratio {R_SUN / R_MOON:.1f}; distance ratio {D_SUN / D_MOON:.1f}")
    print(f"discs equal when the Moon is at {critical_moon_distance():.0f} km")
    print(f"Moon speed {moon_speed_kms():.3f} km/s, shadow speed at the equator {ground_speed_kms():.3f} km/s")

    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(-2.2, 2.2)
    ax.add_patch(plt.Circle((0.9, 0), 0.9, color="gold"))
    ax.add_patch(plt.Circle((6.6, 0), 0.22, color="gray"))
    ax.add_patch(plt.Circle((9.1, 0), 0.7, color="tab:blue", alpha=0.7))
    ax.fill([6.6, 8.9, 8.9, 6.6], [0.22, 0.02, -0.02, -0.22], color="k", alpha=0.5, label="dark shadow (umbra)")
    ax.fill([6.6, 9.1, 9.1, 6.6], [0.22, 0.7, -0.7, -0.22], color="k", alpha=0.12, label="partial shadow (penumbra)")
    ax.text(0.9, -1.35, "Sun", ha="center")
    ax.text(6.6, -0.6, "Moon", ha="center")
    ax.text(9.1, -1.1, "Earth", ha="center")
    ax.set_title("Solar eclipse from the side (sizes and distances not to scale)")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "eclipse_geometry.png", dpi=120)

    fig2, axs = plt.subplots(1, 4, figsize=(9, 2.6))
    cases = [("no eclipse", 0.8, D_MOON), ("partial", 0.3, D_MOON),
             ("annular", 0.0, 400000.0), ("total", 0.0, 360000.0)]
    for a, (name, sep, dist) in zip(axs, cases):
        rs_, rm_ = sky_radii(dist)
        a.add_patch(plt.Circle((0, 0), rs_, color="gold"))
        a.add_patch(plt.Circle((sep, 0), rm_, color="#2b2b3a", alpha=0.9))
        a.set_xlim(-0.6, 1.0)
        a.set_ylim(-0.4, 0.4)
        a.set_aspect("equal")
        a.set_xticks([])
        a.set_yticks([])
        a.set_title(f"{name}\n{covered_fraction(sep, rs_, rm_):.0%} covered", fontsize=9)
    fig2.suptitle("Four sky pictures (width of picture: 1.6 degrees)", fontsize=10)
    fig2.tight_layout()
    fig2.savefig(OUT / "sky_cases.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. Remember: never look at the Sun without certified eclipse glasses.
