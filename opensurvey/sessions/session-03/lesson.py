"""Session 3 (Level 3): close a traverse, adjust it, find a blunder, and measure the errors.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: traverse computation, adjustment and error propagation
# **A. Real-world problem.** To fix the corners of a plot, the surveyor walks round it:
# measure the angle at each corner and the distance of each side (a *closed traverse*).
# Because every measurement has small errors, the traverse does not quite return to its start.
# The gap is the *misclosure*. We must (1) measure it, (2) judge if it is acceptably small,
# (3) spread it out sensibly (the *Bowditch* or compass rule), (4) compute the area, and
# (5) discover when a *blunder* (a wrong reading) is hiding behind a tidy adjustment.
#
# **Plan.** Build a known pentagon, simulate field measurements with typical instrument errors,
# adjust, and check every step against the known exact answer.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# A plot with exactly known coordinates (easting, northing in metres), walked clockwise:
# a 200 m x 120 m rectangle with a gable on top. Exact area = 200*120 + 0.5*200*60 = 30000 m^2.
TRUTH = np.array([[0.0, 0.0], [0.0, 120.0], [100.0, 180.0], [200.0, 120.0], [200.0, 0.0]])
TRUE_AREA = 30000.0
# Typical figures for a mid-range total station (they vary by instrument; check a datasheet):
ANGLE_SIGMA_ARCSEC = 20.0   # standard deviation of one measured angle
DIST_MM, DIST_PPM = 5.0, 5.0   # distance standard deviation = 5 mm + 5 ppm of the distance


# %% [markdown]
# ## Step 1: legs, bearings and interior angles of the known polygon
# Leg i runs from corner i to corner i+1 (the last leg returns to corner 1). Bearings are
# clockwise from north. Walking clockwise, the next bearing is: previous bearing + 180 - interior
# angle at the corner. Check by hand at corner 2: the legs are north (0 degrees) then bearing
# 59.04 degrees, so the interior angle is 0 + 180 - 59.04 = 120.96 degrees.

# %%
def legs(pts):
    """Bearings (degrees) and lengths (m) of the closed polygon pts."""
    d = np.roll(pts, -1, axis=0) - pts
    return np.degrees(np.arctan2(d[:, 0], d[:, 1])) % 360.0, np.hypot(d[:, 0], d[:, 1])


def interior_angles(bearings):
    """Interior angle at each corner (degrees) for a clockwise polygon: angle i is between leg i-1 and leg i."""
    return (np.roll(bearings, 1) + 180.0 - bearings) % 360.0


def bearings_from_angles(b0, angles):
    """Bearing of every leg, given the bearing b0 of leg 1 and the interior angles at corners 2..n."""
    b = [b0 % 360.0]
    for k in range(1, len(angles)):
        b.append((b[-1] + 180.0 - angles[k]) % 360.0)
    return np.array(b)


def walk(start, bearings, dists):
    """Coordinates of the n+1 points visited; the last one should be the start again."""
    r = np.radians(bearings)
    steps = np.stack([dists * np.sin(r), dists * np.cos(r)], axis=1)   # departures, latitudes
    return np.vstack([start, start + np.cumsum(steps, axis=0)])


# %% [markdown]
# ## Step 2: misclosure, relative accuracy, and the angle check
# - Linear misclosure vector = (last point) - (start). Its length is the misclosure.
# - Relative accuracy = perimeter / misclosure, quoted as "1 in N". A common quality target
#   for ordinary work is 1 in 5000.
# - Angle check: interior angles of an n-sided polygon must sum to (n - 2) x 180 degrees.

# %%
def misclosure(pts):
    v = pts[-1] - pts[0]
    return v, float(np.hypot(*v))


def relative_accuracy(mis, perimeter):
    """The N in '1 in N'. Infinite for a perfect closure."""
    return np.inf if mis == 0 else perimeter / mis


def angle_misclosure(angles):
    """Sum of measured interior angles minus (n - 2) x 180, in degrees."""
    return float(np.sum(angles) - (len(angles) - 2) * 180.0)


def spread_angle_error(angles):
    """Share the angular misclosure equally between all angles."""
    return np.asarray(angles) - angle_misclosure(angles) / len(angles)


# %% [markdown]
# ## Step 3: the Bowditch (compass) rule
# Leg i has departure dE_i = D_i sin(b_i) and latitude dN_i = D_i cos(b_i). If the total
# misclosure is (eE, eN) and the perimeter is P, leg i gets the correction
#
#     cE_i = - eE D_i / P        cN_i = - eN D_i / P
#
# so the corrections are proportional to leg length and add up to exactly -e. Therefore the
# adjusted traverse closes exactly: sum(dE_i + cE_i) = eE - eE = 0.

# %%
def bowditch(start, bearings, dists):
    """Adjusted points (n+1 of them) and the misclosure vector that was removed."""
    r = np.radians(bearings)
    steps = np.stack([dists * np.sin(r), dists * np.cos(r)], axis=1)
    e = steps.sum(axis=0)
    corr = -np.outer(dists / dists.sum(), e)
    return np.vstack([start, start + np.cumsum(steps + corr, axis=0)]), e


# %% [markdown]
# ## Step 4: area by the coordinate (shoelace) method
# Area = half the absolute value of sum over corners of (E_i N_{i+1} - E_{i+1} N_i).

# %%
def shoelace(pts):
    p = np.asarray(pts, dtype=float)
    if np.allclose(p[0], p[-1]):
        p = p[:-1]
    e, n = p[:, 0], p[:, 1]
    return 0.5 * abs(float(np.dot(e, np.roll(n, -1)) - np.dot(n, np.roll(e, -1))))


def adjust(start, b0, angles, dists):
    """Full pipeline: spread the angle error, walk, Bowditch, area. Returns a dict."""
    angles = np.asarray(angles, dtype=float)
    dists = np.asarray(dists, dtype=float)
    ang_mis = angle_misclosure(angles)
    adj = spread_angle_error(angles)
    raw = walk(start, bearings_from_angles(b0, adj), dists)
    vec, mis = misclosure(raw)
    pts, _ = bowditch(start, bearings_from_angles(b0, adj), dists)
    return {"angle_misclosure_deg": ang_mis, "misclosure_vec": vec, "misclosure": mis,
            "relative": relative_accuracy(mis, float(dists.sum())), "raw": raw, "points": pts,
            "area": shoelace(pts), "perimeter": float(dists.sum())}


# %% [markdown]
# ## Step 5: simulate field work with typical instrument errors
# Measured = true + random error. Angle error has standard deviation 20 arc-seconds (1 arc-second
# = 1/3600 degree); the distance error is 5 mm + 5 ppm of the distance. Seeded for repeatability.

# %%
def distance_sigma(d):
    """Standard deviation (m) of a measured distance d (m): 5 mm + 5 ppm."""
    return DIST_MM * 1e-3 + DIST_PPM * 1e-6 * np.asarray(d, dtype=float)


def simulate_field(pts, rng, angle_arcsec=ANGLE_SIGMA_ARCSEC, dist_scale=1.0):
    b, d = legs(pts)
    a = interior_angles(b)
    ma = a + rng.normal(0.0, angle_arcsec / 3600.0, size=a.shape)
    md = d + rng.normal(0.0, 1.0, size=d.shape) * distance_sigma(d) * dist_scale
    return b[0], ma, md


def monte_carlo(pts=TRUTH, trials=4000, seed=2024, angle_arcsec=ANGLE_SIGMA_ARCSEC, dist_scale=1.0):
    """Repeat the survey many times. Returns arrays: raw misclosure length, relative N,
    area error, and error of the adjusted coordinates of the last corner."""
    rng = np.random.default_rng(seed)
    mis, rel, aerr, perr, uns = [], [], [], [], []
    for _ in range(trials):
        b0, ma, md = simulate_field(pts, rng, angle_arcsec, dist_scale)
        res = adjust(pts[0], b0, ma, md)
        mis.append(res["misclosure"])
        rel.append(res["relative"])
        aerr.append(res["area"] - shoelace(pts))
        perr.append(np.hypot(*(res["points"][-2] - pts[-1])))
        uns.append(misclosure(walk(pts[0], bearings_from_angles(b0, ma), md))[1])
    return {"misclosure": np.array(mis), "relative": np.array(rel), "area_err": np.array(aerr),
            "corner_err": np.array(perr), "raw_unadjusted": np.array(uns)}


def predicted_misclosure_rms(pts=TRUTH, angle_arcsec=ANGLE_SIGMA_ARCSEC, dist_scale=1.0):
    """First-order (small error) prediction of the RMS misclosure when the angles are NOT adjusted.
    Uses the Jacobian of the walk with respect to the n-1 angles and n distances."""
    b, d = legs(pts)
    a = interior_angles(b)
    n = len(d)

    def f(x):
        ang = np.concatenate([[a[0]], x[:n - 1]])
        return misclosure(walk(pts[0], bearings_from_angles(b[0], ang), x[n - 1:]))[0]

    x0 = np.concatenate([a[1:], d])
    h = 1e-6
    J = np.stack([(f(x0 + h * np.eye(len(x0))[i]) - f(x0 - h * np.eye(len(x0))[i])) / (2 * h)
                  for i in range(len(x0))], axis=1)
    var = np.concatenate([np.full(n - 1, (angle_arcsec / 3600.0) ** 2), (distance_sigma(d) * dist_scale) ** 2])
    cov = J @ np.diag(var) @ J.T
    return float(np.sqrt(np.trace(cov)))


def max_angle_sigma(rms_limit, pts=TRUTH):
    """Design helper: the largest angle standard deviation (arc-seconds) whose predicted RMS misclosure
    (metres) stays at or below rms_limit, found by bisection."""
    lo, hi = 0.0, 1000.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if predicted_misclosure_rms(pts, angle_arcsec=mid) > rms_limit:
            hi = mid
        else:
            lo = mid
    return lo


# %% [markdown]
# ## Step 6: curvature and refraction for long sights
# The Earth curves away from a horizontal line of sight, and the air bends the ray slightly back.
# Over K kilometres, the combined correction is c = 0.0675 K^2 metres. Where it comes from:
# the curvature part is d^2 / (2R) (R = 6371 km); refraction removes a fraction k, about 0.14,
# of it, leaving (1 - k) K^2 / (2R). Refraction varies with the weather; 0.14 is a typical value.

# %%
R_EARTH = 6371000.0   # metres, mean radius of the Earth
K_REFRACTION = 0.14   # typical coefficient of refraction (varies)


def sphere_drop(d):
    """Exact height (m) of a horizontal tangent line above the sphere at distance d (m) along the tangent:
    sqrt(R^2 + d^2) - R, written to avoid cancellation."""
    d = np.asarray(d, dtype=float)
    return d * d / (np.sqrt(R_EARTH ** 2 + d * d) + R_EARTH)


def cr_formula(k_km):
    """The standard small-correction formula, metres."""
    return 0.0675 * np.asarray(k_km, dtype=float) ** 2


def cr_physics(k_km, k=K_REFRACTION):
    """Curvature from the sphere geometry, reduced by refraction, metres."""
    return (1.0 - k) * sphere_drop(np.asarray(k_km, dtype=float) * 1000.0)


# %% [markdown]
# ## Step 7: a blunder that the adjustment hides, and how to find it
# A blunder is a wrong reading (not a small random error). Suppose the angle at one corner is
# read 1 degree too large. The traverse then fails to close by a large amount; Bowditch happily
# spreads it and the adjusted figure closes *exactly*, but the corners are wrong. To find the
# corner: an angle blunder at corner k turns every later leg about corner k. So the misclosure
# vector is perpendicular to the line from corner k to the start. The corner whose line to the
# start is most nearly perpendicular to the misclosure is the suspect.

# %%
def locate_angle_blunder(start, b0, angles, dists):
    """Return (index of suspect corner, estimated size of the blunder in degrees) for corners 2..n,
    using the unadjusted angles."""
    raw = walk(start, bearings_from_angles(b0, angles), dists)
    mis = raw[-1] - raw[0]
    best, score = None, 2.0
    for k in range(1, len(angles)):
        v = raw[0] - raw[k]
        c = abs(np.dot(mis, v)) / (np.hypot(*mis) * np.hypot(*v))
        if c < score:
            best, score = k, c
    v = raw[0] - raw[best]
    size = 2.0 * np.degrees(np.arcsin(min(1.0, np.hypot(*mis) / (2.0 * np.hypot(*v)))))
    return best, float(size)


def with_blunder(angles, corner, size_deg):
    a = np.array(angles, dtype=float)
    a[corner] += size_deg
    return a


# %% [markdown]
# ## Step 8: the field data for the mini-project (synthetic)
# A six-corner site walked clockwise from corner 1 at E 5000.000, N 10000.000 m. The bearing of
# leg 1 is known. `FIELD_ANGLES` are the six measured interior angles (degrees), `FIELD_DISTS`
# the six leg lengths (m). One angle was misread. `FIELD_TRUTH` is the answer key (do not peek
# until you have your own coordinates).

# %%
FIELD_START = np.array([5000.0, 10000.0])
FIELD_B0 = 351.8699
FIELD_ANGLES = [109.4402, 123.8647, 131.9041, 114.8573, 119.7432, 121.1976]
FIELD_DISTS = [141.425, 134.536, 140.806, 131.234, 162.797, 152.97]
FIELD_TRUTH = np.array([[5000.0, 10000.0], [4980.0, 10140.0], [5080.0, 10230.0],
                        [5220.0, 10215.0], [5260.0, 10090.0], [5150.0, 9970.0]])


# %% [markdown]
# ## Step 9: see it
# Left: the walked traverse with its misclosure (exaggerated errors, so you can see them).
# Right: the Bowditch corrections move each corner back along the walk.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    b, d = legs(TRUTH)
    print("bearings", b.round(2), "lengths", d.round(3), "perimeter", round(float(d.sum()), 3))
    print("interior angles", interior_angles(b).round(2), "sum", round(float(interior_angles(b).sum()), 6))

    rng = np.random.default_rng(5)
    b0, ma, md = simulate_field(TRUTH, rng, angle_arcsec=20.0 * 60, dist_scale=40.0)   # errors exaggerated for the picture
    res = adjust(TRUTH[0], b0, ma, md)
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    t = np.vstack([TRUTH, TRUTH[0]])
    ax.plot(t[:, 0], t[:, 1], "k:", label="true corners")
    ax.plot(res["raw"][:, 0], res["raw"][:, 1], "o-", color="tab:red", label="walked (unadjusted)")
    ax.plot(res["points"][:, 0], res["points"][:, 1], "s-", color="tab:green", label="after Bowditch")
    ax.annotate("", xy=res["raw"][-1], xytext=res["raw"][0], arrowprops=dict(arrowstyle="->", color="tab:red"))
    ax.set_aspect("equal")
    ax.set_xlabel("easting (m)")
    ax.set_ylabel("northing (m)")
    ax.set_title("Misclosure (red arrow) removed by Bowditch (errors exaggerated)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "bowditch.png", dpi=120)

    mc = monte_carlo()
    print(f"typical errors: RMS raw misclosure {np.sqrt(np.mean(mc['raw_unadjusted'] ** 2)) * 1000:.1f} mm; "
          f"predicted {predicted_misclosure_rms() * 1000:.1f} mm; "
          f"median relative accuracy 1 in {np.median(mc['relative']):.0f}; "
          f"area error std {mc['area_err'].std():.3f} m2")

    sig = np.array([5.0, 10.0, 20.0, 40.0, 80.0, 160.0])
    rms = [np.sqrt(np.mean(monte_carlo(trials=1500, angle_arcsec=s)["raw_unadjusted"] ** 2)) * 1000 for s in sig]
    fig2, ax2 = plt.subplots(figsize=(6.2, 4))
    ax2.loglog(sig, rms, "o-", label="Monte Carlo RMS misclosure")
    ax2.axhline(673.238 / 5000 * 1000, color="red", ls="--", label="1 in 5000 limit (134.6 mm)")
    ax2.set_xlabel("angle standard deviation (arc-seconds)")
    ax2.set_ylabel("RMS misclosure (mm)")
    ax2.set_title("Sensitivity: angle error drives the misclosure")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "sensitivity.png", dpi=120)

    K = np.linspace(0, 3, 61)
    fig3, ax3 = plt.subplots(figsize=(6.2, 4))
    ax3.plot(K, sphere_drop(K * 1000) * 1000, label="curvature only (sphere geometry)")
    ax3.plot(K, cr_formula(K) * 1000, "--", label="0.0675 K^2 (curvature and refraction)")
    ax3.set_xlabel("sight length K (km)")
    ax3.set_ylabel("correction (mm)")
    ax3.set_title("Long sights: the Earth curves away")
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "curvature.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), do the mini-project
# in the README, then run the checkpoint.
