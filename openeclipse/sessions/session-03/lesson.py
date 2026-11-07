"""Session 3 (Level 3): predicting eclipses from mean motions, and the Saros.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: predicting eclipses from mean motions, and the Saros
# **SAFETY.** Never look at the Sun without certified eclipse glasses, even in a partial
# eclipse. This session is calculation only.
#
# **A. Real-world problem.** Ancient astronomers predicted eclipses without computers. They
# noticed that after 18 years and about 11 days the Sun, Moon and Moon's node return to nearly
# the same arrangement, so eclipses repeat. Today we build a small prediction engine from
# the Moon's *mean motions* (steady averages) plus a few of the largest wobbles, check
# it against published eclipse times, and discover the cycle (the **Saros**) ourselves.
#
# **Educational approximation.** This model is accurate to hours in time, not minutes. For
# real dates, times and maps always use published tables (for example the NASA eclipse
# website by Fred Espenak).

# %%
import datetime as dt
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

SYNODIC = 29.530589          # days, new moon to new moon
DRACONIC = 27.212221         # days, node to the same node
ANOMALISTIC = 27.554550      # days, perigee to perigee
ANOM_YEAR = 365.2596         # days, the Sun's anomaly period
JD_K0 = 2451550.09766        # a new moon: 2000 January 6, about 18:14 UT (k = 0)
M0, MP0, F0 = 2.5534, 201.5643, 160.7108   # degrees at k = 0 (Sun anomaly, Moon anomaly, Moon argument of latitude)
R_SUN, R_MOON, R_EARTH = 696000.0, 1737.0, 6378.0
AU = 149597870.7
INCL = 5.145


# %% [markdown]
# ## Step 1: three clocks
# At the k-th new moon after 2000 January 6, three angles have advanced by a fixed amount
# per month:
# - M, the Sun's anomaly (where Earth is on its orbit), +360 * SYNODIC / ANOM_YEAR per month;
# - M', the Moon's anomaly (where the Moon is between perigee and apogee),
#   +360 * SYNODIC / ANOMALISTIC (mod 360);
# - F, the Moon's argument of latitude (angle from the ascending node),
#   +360 * SYNODIC / DRACONIC (mod 360).
# If F is near 0 or 180 degrees, the new moon is near a node: an eclipse is possible.

# %%
def clocks(k):
    """(M, M', F) in degrees for the k-th mean new moon."""
    M = (M0 + k * 360.0 * SYNODIC / ANOM_YEAR) % 360
    Mp = (MP0 + k * 360.0 * SYNODIC / ANOMALISTIC) % 360
    F = (F0 + k * 360.0 * SYNODIC / DRACONIC) % 360
    return M, Mp, F


def node_distance(F):
    """Angle (degrees, 0 to 90) from the nearest node, for argument of latitude F."""
    d = F % 180.0
    return float(min(d, 180.0 - d))


# %% [markdown]
# ## Step 2: when exactly is new moon?
# The mean time is JD_K0 + k SYNODIC. The real time differs by up to about half a day,
# mostly because the Moon speeds up near perigee and the Earth speeds up near perihelion. We
# add the seven largest corrections (in days) from the standard series:
# -0.4072 sin M', +0.1724 sin M, +0.0161 sin 2M', +0.0104 sin 2F, +0.0074 sin(M'-M),
# -0.0051 sin(M'+M), +0.0021 sin 2M.

# %%
def new_moon_mean_jd(k):
    return JD_K0 + k * SYNODIC


def new_moon_jd(k):
    M, Mp, F = (np.radians(a) for a in clocks(k))
    corr = (-0.40720 * np.sin(Mp) + 0.17241 * np.sin(M) + 0.01608 * np.sin(2 * Mp)
            + 0.01039 * np.sin(2 * F) + 0.00739 * np.sin(Mp - M)
            - 0.00514 * np.sin(Mp + M) + 0.00208 * np.sin(2 * M))
    return float(new_moon_mean_jd(k) + corr)


def jd_to_datetime(jd):
    return dt.datetime(2000, 1, 1, 12) + dt.timedelta(days=jd - 2451545.0)


def datetime_to_jd(t):
    return 2451545.0 + (t - dt.datetime(2000, 1, 1, 12)).total_seconds() / 86400.0


# %% [markdown]
# ## Step 3: the Moon's height above the ecliptic and its distance
# Latitude (degrees) from the largest terms: 5.1282 sin F + 0.2806 sin(M'+F) +
# 0.2777 sin(M'-F) - 0.1732 sin F + 0.0554 sin(F-M') - 0.0463 sin(M'+F) + 0.0326 sin F
# (these use that the Sun-Moon elongation D is 0 at new moon). Distance (km) from the largest terms at D = 0. The time correction also moves F,
# M and M' forward by their mean rates.

# %%
def state_at_new_moon(k):
    """Dictionary of angles at the corrected new moon time."""
    jd = new_moon_jd(k)
    shift = jd - new_moon_mean_jd(k)
    M, Mp, F = clocks(k)
    M = (M + shift * 360.0 / ANOM_YEAR) % 360
    Mp = (Mp + shift * 360.0 / ANOMALISTIC) % 360
    F = (F + shift * 360.0 / DRACONIC) % 360
    f, mp = np.radians(F), np.radians(Mp)
    beta = (5.1282 * np.sin(f) + 0.2806 * np.sin(mp + f) + 0.2777 * np.sin(mp - f)
            - 0.1732 * np.sin(f) + 0.0554 * np.sin(f - mp) - 0.0463 * np.sin(mp + f)
            + 0.0326 * np.sin(f))
    d_moon = (385000.56 - 20905.355 * np.cos(mp) - 3699.111 * np.cos(mp) - 2955.968
              + 246.158 * np.cos(2 * mp) - 569.925 * np.cos(2 * mp) - 170.733 * np.cos(mp)
              + 108.743 - 204.586 * np.cos(np.radians(M)))
    d_sun = AU * (1.00014 - 0.01671 * np.cos(np.radians(M)) - 0.00014 * np.cos(2 * np.radians(M)))
    return {"k": k, "jd": jd, "M": M, "Mp": Mp, "F": F, "beta": float(beta),
            "d_moon": float(d_moon), "d_sun": float(d_sun)}


# %% [markdown]
# ## Step 4: from geometry to a prediction
# Using Session 2's ideas, with gamma = (distance of the shadow axis from the Earth's centre)
# in Earth radii = d sin(beta) / R_EARTH:
# - partial eclipse somewhere if gamma < 1 + (penumbra radius at the Earth) / R_EARTH;
# - central (total, annular or hybrid) if gamma < 1;
# - total if the umbra's tip reaches past the Moon-Earth distance (L > d), annular if it stops
#   short of the nearest ground (L < d - R_EARTH), hybrid in between.
# The size of a partial eclipse (magnitude) is the fraction of the Sun's diameter covered at
# the best place on Earth.

# %%
def umbra_length(d_sun, r_sun=R_SUN, r_moon=R_MOON):
    return d_sun * r_moon / (r_sun - r_moon)


def penumbra_radius_at_earth(d_moon, d_sun):
    return R_MOON + d_moon * (R_SUN + R_MOON) / d_sun


def predict(k):
    """Predicted eclipse (a dict) for the k-th new moon, or None if no solar eclipse."""
    s = state_at_new_moon(k)
    d, ds = s["d_moon"], s["d_sun"]
    gamma = d * np.sin(np.radians(abs(s["beta"]))) / R_EARTH
    pen = penumbra_radius_at_earth(d, ds) / R_EARTH
    if gamma >= 1.0 + pen:
        return None
    rs = np.degrees(np.arctan(R_SUN / ds))
    rm = np.degrees(np.arctan(R_MOON / d))
    L = umbra_length(ds)
    if gamma < 1.0:
        kind = "total" if L >= d else ("annular" if L < d - R_EARTH else "hybrid")
        mag = float(rm / rs)
    else:
        kind = "partial"
        beta_c = np.degrees(np.arcsin(R_EARTH / d))
        offset = max(abs(s["beta"]) - beta_c, 0.0)
        mag = float((rs + rm - offset) / (2 * rs))
    out = dict(s)
    out.update({"gamma": float(gamma), "kind": kind, "magnitude": mag,
                "date": jd_to_datetime(s["jd"])})
    return out


def k_range(start, end):
    """Index range of new moons between two datetimes."""
    k0 = int(np.floor((datetime_to_jd(start) - JD_K0) / SYNODIC)) - 1
    k1 = int(np.ceil((datetime_to_jd(end) - JD_K0) / SYNODIC)) + 1
    return range(k0, k1 + 1)


def eclipses_between(start, end):
    return [e for e in (predict(k) for k in k_range(start, end)) if e and start <= e["date"] <= end]


# %% [markdown]
# ## Step 5: compare with published eclipses
# Published times of greatest eclipse (UT, from NASA tables, rounded to the minute) for
# thirteen solar eclipses, with the published kind and the published |gamma| (how far the
# shadow axis passes from the Earth's centre, in Earth radii). We predict each eclipse from
# the nearest new moon and measure the errors.

# %%
PUBLISHED = [
    (dt.datetime(2017, 8, 21, 18, 25), "total", 0.4367),
    (dt.datetime(2019, 7, 2, 19, 23), "total", 0.6455),
    (dt.datetime(2019, 12, 26, 5, 18), "annular", 0.4135),
    (dt.datetime(2020, 6, 21, 6, 41), "annular", 0.1209),
    (dt.datetime(2020, 12, 14, 16, 14), "total", 0.2939),
    (dt.datetime(2021, 6, 10, 10, 43), "annular", 0.9152),
    (dt.datetime(2021, 12, 4, 7, 34), "total", 0.9526),
    (dt.datetime(2023, 4, 20, 4, 17), "hybrid", 0.3952),
    (dt.datetime(2023, 10, 14, 18, 0), "annular", 0.3753),
    (dt.datetime(2024, 4, 8, 18, 17), "total", 0.3431),
    (dt.datetime(2024, 10, 2, 18, 46), "annular", 0.3509),
    (dt.datetime(2026, 2, 17, 12, 12), "annular", 0.9743),
    (dt.datetime(2026, 8, 12, 17, 46), "total", 0.8977),
]


def nearest_k(when):
    return int(round((datetime_to_jd(when) - JD_K0) / SYNODIC))


def timing_errors_hours(use_corrections=True):
    """Predicted new-moon time minus published greatest-eclipse time, in hours."""
    errs = []
    for when, _, _ in PUBLISHED:
        k = nearest_k(when)
        jd = new_moon_jd(k) if use_corrections else new_moon_mean_jd(k)
        errs.append((jd - datetime_to_jd(when)) * 24.0)
    return np.array(errs)


def gamma_errors():
    """Predicted |gamma| minus published |gamma| for the thirteen eclipses."""
    out = []
    for when, _, g in PUBLISHED:
        s = state_at_new_moon(nearest_k(when))
        out.append(s["d_moon"] * np.sin(np.radians(abs(s["beta"]))) / R_EARTH - g)
    return np.array(out)


def kinds_match():
    n = 0
    for when, kind, _ in PUBLISHED:
        e = predict(nearest_k(when))
        n += int(e is not None and e["kind"] == kind)
    return n


# %% [markdown]
# ## Step 6: where the model fails
# Two of the thirteen kinds are wrong. A hybrid eclipse (total at the middle of the path,
# annular at the ends) is called total, and one annular eclipse with gamma very close to 1
# is called partial. A tiny error in the Moon's latitude flips a verdict near a boundary. A
# partial eclipse with a small magnitude is the most fragile: one degree of latitude error
# changes its magnitude by 1 / (2 rs), about 1.9.

# %%
def magnitude_change_per_degree(rs_deg=0.2666):
    return 1.0 / (2.0 * rs_deg)


# %% [markdown]
# ## Step 7: the Saros
# 223 synodic months, 242 draconic months and 239 anomalistic months are nearly equal.
# After that long the Moon is in the same phase, at the same distance and at the same
# distance from the node: the eclipse repeats. The tiny mismatch (a fraction of a day)
# slowly moves the eclipse across the node, so each series lasts many repeats.

# %%
def saros_days():
    return 223 * SYNODIC


def saros_mismatches():
    """(draconic mismatch, anomalistic mismatch) in days relative to 223 synodic months."""
    return 242 * DRACONIC - 223 * SYNODIC, 239 * ANOMALISTIC - 223 * SYNODIC


def saros_calendar():
    """Days beyond 18 calendar years (with 4 leap days) : (whole days, hours)."""
    extra = saros_days() - (18 * 365 + 4)
    return int(extra), (extra - int(extra)) * 24.0


def saros_longitude_shift_deg():
    """Westward shift of the eclipse track: the leftover fraction of a day times 360."""
    return (saros_days() % 1.0) * 360.0


def saros_node_drift_deg():
    """How far F changes in one Saros (degrees): the series creeps across the node."""
    return float(360.0 * (223 * SYNODIC / DRACONIC - 242))


def saros_partner(k):
    """The predicted eclipse one Saros (223 new moons) later."""
    return predict(k + 223)


def count_eclipses(k_first, n_months):
    return sum(predict(k) is not None for k in range(k_first, k_first + n_months))


def saros_series_length(limit_deg):
    """Number of eclipses in a series: the node distance sweeps through 2 limit at this drift."""
    return int(2 * limit_deg / abs(saros_node_drift_deg()))


# %% [markdown]
# ## Step 8: see it
# Top: node distance of every new moon over three years, with the eclipse limit.
# Bottom: one Saros series, member by member.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    e1 = timing_errors_hours(True)
    e0 = timing_errors_hours(False)
    print(f"timing error with corrections: max {np.abs(e1).max():.1f} h; mean-only: max {np.abs(e0).max():.1f} h")
    print(f"kinds matched: {kinds_match()} of {len(PUBLISHED)}")
    print("Saros days", round(saros_days(), 4), "mismatch", [round(x, 3) for x in saros_mismatches()],
          "calendar", saros_calendar(), "shift", round(saros_longitude_shift_deg(), 1),
          "drift", round(saros_node_drift_deg(), 3), "series", saros_series_length(16.7))
    found = eclipses_between(dt.datetime(2027, 1, 1), dt.datetime(2029, 12, 31, 23, 59))
    for e in found:
        print(e["date"].strftime("%Y-%m-%d %H:%M"), e["kind"], f"gamma {e['gamma']:.2f} mag {e['magnitude']:.2f}")

    k = np.arange(0, 38)
    nd = [node_distance(clocks(i)[2]) for i in k]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.bar(k, nd, color=["tab:red" if x < 16.7 else "lightgray" for x in nd])
    ax.axhline(16.7, color="k", ls="--", label="approximate limit 16.7 degrees")
    ax.set_xlabel("new moon number (months after 6 Jan 2000)")
    ax.set_ylabel("distance from the node (degrees)")
    ax.set_title("Only new moons near a node (red) can give an eclipse")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "node_distance.png", dpi=120)

    n = np.arange(0, 80)
    drift = saros_node_drift_deg()
    pos = -40 * abs(drift) + n * abs(drift)
    fig2, ax2 = plt.subplots(figsize=(7, 3.6))
    ax2.plot(n, pos, "o-", ms=3)
    ax2.axhline(16.7, color="k", ls="--")
    ax2.axhline(-16.7, color="k", ls="--")
    ax2.set_xlabel("member number in a Saros series")
    ax2.set_ylabel("Moon's distance past the node (degrees)")
    ax2.set_title("A Saros series creeps across the node")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "saros_series.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), run the
# checkpoint, and then try the mini-project.
