"""Session 2 (Level 2): transit depth, limb darkening, duration, period and the noise needed.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the mathematics of a transit
# **A. Real-world problem.** Session 1 said depth = (Rp/Rs)^2 and drew a flat box. Two real
# questions follow. (1) How big is the dip for Jupiter and for Earth around the Sun, and what
# does a real star's dip look like? (2) How accurate must a telescope be to see an Earth-size
# planet at all?
#
# **Plan.** (1) depth from radii, (2) exact overlap of two circles, (3) limb darkening by
# numerical integration, (4) duration and impact parameter from Kepler's third law,
# (5) period from the spacing of transits, (6) the noise needed to see an Earth.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R_SUN_KM = 695700.0
R_JUP_KM = 71492.0
R_EARTH_KM = 6371.0
G_M_SUN = 1.32712440018e20      # G times the Sun's mass, m^3 / s^2
DAY = 86400.0                   # seconds in a day
U1, U2 = 0.40, 0.25             # illustrative quadratic limb-darkening coefficients for a Sun-like star


# %% [markdown]
# ## Step 1: depth from radii
# Planet radius Rp and star radius Rs give the radius ratio k = Rp / Rs and the depth k^2.

# %%
def radius_ratio(rp_km, rs_km=R_SUN_KM):
    return rp_km / rs_km


def depth(k):
    return k ** 2


# %% [markdown]
# ## Step 2: the exact flat-star transit (overlap of two circles)
# Put the star (radius 1) at the origin. The planet (radius k) has its centre a distance z from
# the star's centre, in units of the stellar radius. If the star were uniformly bright, the
# flux is 1 minus the overlapping area divided by pi. The overlap of two circles is a lens-shaped
# area with a known formula.

# %%
def overlap_area(z, k):
    """Overlap area of the unit star disk and a planet disk of radius k with centre distance z."""
    z = np.abs(np.atleast_1d(np.asarray(z, dtype=float)))
    area = np.zeros_like(z)
    inside = z <= 1.0 - k
    area[inside] = np.pi * k ** 2
    part = (z > 1.0 - k) & (z < 1.0 + k)
    zz = z[part]
    c1 = np.clip((zz ** 2 + k ** 2 - 1.0) / (2 * zz * k), -1, 1)
    c2 = np.clip((zz ** 2 + 1.0 - k ** 2) / (2 * zz), -1, 1)
    root = np.sqrt(np.maximum((-zz + k + 1) * (zz + k - 1) * (zz - k + 1) * (zz + k + 1), 0.0))
    area[part] = k ** 2 * np.arccos(c1) + np.arccos(c2) - 0.5 * root
    return area


def uniform_flux(z, k):
    return 1.0 - overlap_area(z, k) / np.pi


# %% [markdown]
# ## Step 3: limb darkening and a numerical integral
# A star's edge (limb) is dimmer than its centre. With mu = cos(angle from the line of sight)
# = sqrt(1 - r^2) at radius r on the disk (r = 1 is the edge), the quadratic law is
#
#     I(mu) / I(1) = 1 - u1 (1 - mu) - u2 (1 - mu)^2
#
# The star's total light is the integral of I over its disk, and a transit removes the part of
# that integral under the planet. We evaluate it on a fine grid of small squares:
# `disk_integral` covers the whole stellar disk once (for the total), and `ld_flux` covers only
# the planet's shadow (the only place light is blocked).

# %%
def ld_intensity(mu, u1=U1, u2=U2):
    return 1.0 - u1 * (1.0 - mu) - u2 * (1.0 - mu) ** 2


def disk_integral(u1=U1, u2=U2, n=801):
    """Total light of the star, integrating I over a grid of n x n squares covering the stellar disk."""
    g = (np.arange(n) + 0.5) / n * 2.0 - 1.0
    x, y = np.meshgrid(g, g)
    r2 = x ** 2 + y ** 2
    inside = r2 < 1.0
    mu = np.sqrt(1.0 - r2[inside])
    return float(np.sum(ld_intensity(mu, u1, u2)) * (2.0 / n) ** 2)


def total_light_exact(u1=U1, u2=U2):
    """The same integral worked out by hand: pi * (1 - u1/3 - u2/6)."""
    return np.pi * (1.0 - u1 / 3.0 - u2 / 6.0)


def ld_flux(z, k, u1=U1, u2=U2, n=161):
    """Limb-darkened relative flux at planet-star centre distances z (array), by grid integration."""
    z = np.atleast_1d(np.asarray(z, dtype=float))
    g = (np.arange(n) + 0.5) / n * 2.0 - 1.0
    dx, dy = np.meshgrid(g * k, g * k)
    on_planet = (dx ** 2 + dy ** 2) < k ** 2
    dx, dy = dx[on_planet], dy[on_planet]
    cell = (2.0 * k / n) ** 2
    total = total_light_exact(u1, u2)
    out = np.empty_like(z)
    for i, zi in enumerate(z):
        r2 = (zi + dx) ** 2 + dy ** 2
        lit = r2 < 1.0
        out[i] = 1.0 - np.sum(ld_intensity(np.sqrt(1.0 - r2[lit]), u1, u2)) * cell / total
    return out


# %% [markdown]
# ## Step 4: when, and for how long? (Kepler's third law)
# For a circular orbit of period P around a star of mass M, Kepler's third law gives the orbit
# radius a = (G M P^2 / (4 pi^2))^(1/3). Seen edge-on-ish, the planet's centre projects to a
# distance z(t) from the star's centre (in stellar radii):
#
#     z = sqrt( (a/Rs)^2 sin^2(phi) + b^2 cos^2(phi) ),   phi = 2 pi (t - t0) / P,
#
# where b = (a/Rs) cos(i) is the **impact parameter**: how far from the star's centre the
# planet's path crosses, in stellar radii (0 = through the centre, 1 = grazing the edge).
# The transit lasts while z < 1 + k.

# %%
def a_metres(period_days, m_sun=1.0):
    return (G_M_SUN * m_sun * (period_days * DAY) ** 2 / (4 * np.pi ** 2)) ** (1.0 / 3.0)


def a_over_rs(period_days, m_sun=1.0, r_sun=1.0):
    return a_metres(period_days, m_sun) / (r_sun * R_SUN_KM * 1000.0)


def impact_parameter(a_rs, inc_deg):
    return a_rs * np.cos(np.radians(inc_deg))


def inclination_deg(a_rs, b):
    return float(np.degrees(np.arccos(b / a_rs)))


def separation(t, period, t0, a_rs, b):
    """Projected centre-to-centre distance z (stellar radii); planet behind the star gives 1000."""
    phi = 2 * np.pi * (np.asarray(t, dtype=float) - t0) / period
    z = np.sqrt((a_rs * np.sin(phi)) ** 2 + (b * np.cos(phi)) ** 2)
    return np.where(np.cos(phi) > 0, z, 1000.0)


def duration_approx(period, a_rs, k, b):
    """T = (P / pi) (Rs / a) sqrt((1 + k)^2 - b^2) in days (0 if there is no transit)."""
    s = (1.0 + k) ** 2 - b ** 2
    return float(period / np.pi / a_rs * np.sqrt(s)) if s > 0 else 0.0


def duration_exact(period, a_rs, k, b):
    """Exact first-to-last contact time for a circular orbit, in days."""
    s = (1.0 + k) ** 2 - b ** 2
    if s <= 0:
        return 0.0
    sin_i = np.sqrt(1.0 - (b / a_rs) ** 2)
    return float(period / np.pi * np.arcsin(np.sqrt(s) / (a_rs * sin_i)))


def duration_numeric(period, a_rs, k, b, n=400001):
    """Time the light curve spends below 1, found on a very fine time grid, in days."""
    t = np.linspace(-0.25 * period, 0.25 * period, n)
    below = uniform_flux(separation(t, period, 0.0, a_rs, b), k) < 1.0 - 1e-12
    return float(t[below].max() - t[below].min()) if below.any() else 0.0


# %% [markdown]
# ## Step 5: the period from the spacing of transits
# Transit number n happens at t_n = t0 + n P. A straight-line fit of measured mid-times against
# n gives the slope P and the intercept t0. Many transits average down the timing errors.

# %%
def fit_period(epochs, mid_times):
    """Least-squares line mid_time = t0 + P * epoch. Returns (P, t0)."""
    p, t0 = np.polyfit(np.asarray(epochs, dtype=float), np.asarray(mid_times, dtype=float), 1)
    return float(p), float(t0)


# %% [markdown]
# ## Step 6: design problem. How quiet must the telescope be?
# Suppose each measurement has random noise sigma (a fraction of the star's brightness). One
# transit of depth d contains n points, so over N transits we have n_in = n N points inside.
# Averaging them gives a depth uncertainty sigma / sqrt(n_in), so
#
#     SNR = d sqrt(n_in) / sigma     =>     sigma_max = d sqrt(n_in) / SNR.
#
# (Simplified: the baseline outside the transit is assumed perfectly known.)

# %%
def points_per_transit(duration_days, cadence_days):
    return int(np.floor(duration_days / cadence_days))


def snr(depth_value, sigma, n_in):
    return depth_value * np.sqrt(n_in) / sigma


def sigma_needed(depth_value, n_in, snr_target=7.0):
    return depth_value * np.sqrt(n_in) / snr_target


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # depths
    kj, ke = radius_ratio(R_JUP_KM), radius_ratio(R_EARTH_KM)
    print(f"Jupiter: k = {kj:.5f}, depth = {depth(kj):.5f} ({depth(kj):.2%})")
    print(f"Earth:   k = {ke:.5f}, depth = {depth(ke):.3e} ({depth(ke) * 1e6:.1f} ppm)")

    # grid integral checks
    print(f"star total light: grid {disk_integral():.5f}, hand {total_light_exact():.5f}")
    kk = 0.1
    z0 = np.array([0.0])
    print(f"flat star, planet at centre: depth via overlap {1 - uniform_flux(z0, kk)[0]:.5f}, k^2 = {kk ** 2:.5f}")
    print(f"limb-darkened, planet at centre: depth {1 - ld_flux(z0, kk)[0]:.5f} (flat star: {kk ** 2:.5f})")
    zs = np.linspace(0.0, 1.3, 14)
    print(f"largest |grid - exact overlap| with u1 = u2 = 0: {np.max(np.abs(ld_flux(zs, kk, 0.0, 0.0) - uniform_flux(zs, kk))):.2e}")

    # light curve: box, flat star, limb darkened
    P, M, Rs = 3.0, 1.0, 1.0
    aR = a_over_rs(P, M, Rs)
    b = 0.3
    t = np.linspace(-0.12, 0.12, 241)
    z = separation(t, P, 0.0, aR, b)
    f_flat = uniform_flux(z, kk)
    f_ld = ld_flux(z, kk)
    T_num = duration_numeric(P, aR, kk, b)
    print(f"P = {P} d, a = {a_metres(P) / 1.496e11:.4f} AU = {aR:.2f} Rs; duration: approx {duration_approx(P, aR, kk, b) * 24:.3f} h, "
          f"exact {duration_exact(P, aR, kk, b) * 24:.3f} h, numeric {T_num * 24:.3f} h")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(t * 24, np.where(np.abs(t) < T_num / 2, 1 - kk ** 2, 1.0), "--", color="0.5", label="box: depth k^2")
    ax.plot(t * 24, f_flat, color="tab:blue", label="flat star (exact overlap)")
    ax.plot(t * 24, f_ld, color="tab:red", label="limb-darkened star (grid integral)")
    ax.set_xlabel("time from mid-transit (hours)")
    ax.set_ylabel("relative flux")
    ax.set_title("Same planet, three models (k = 0.1, b = 0.3, P = 3 d)")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "limb_darkening_transit.png", dpi=110)

    # depth vs radius ratio with Jupiter and Earth
    ks = np.logspace(-2.2, -0.6, 100)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.loglog(ks, depth(ks) * 1e6, color="tab:blue")
    ax.plot([kj, ke], [depth(kj) * 1e6, depth(ke) * 1e6], "o", color="tab:red")
    ax.annotate("Jupiter (about 1 percent)", (kj, depth(kj) * 1e6), textcoords="offset points", xytext=(-110, -4), fontsize=8)
    ax.annotate("Earth (84 ppm)", (ke, depth(ke) * 1e6), textcoords="offset points", xytext=(8, -12), fontsize=8)
    ax.set_xlabel("radius ratio Rp / Rs (no unit)")
    ax.set_ylabel("transit depth (ppm = parts per million)")
    ax.set_title("Depth = (Rp / Rs)^2 around a Sun-like star")
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "depth_vs_radius.png", dpi=110)

    # duration vs b
    bs = np.linspace(0, 1.1, 23)
    num = [duration_numeric(P, aR, kk, bb, n=100001) * 24 for bb in bs]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(bs, num, "o", ms=4, color="tab:blue", label="numerical light curve")
    ax.plot(bs, [duration_approx(P, aR, kk, bb) * 24 for bb in bs], color="tab:red", label="formula (P/pi)(Rs/a) sqrt((1+k)^2 - b^2)")
    ax.set_xlabel("impact parameter b (stellar radii)")
    ax.set_ylabel("transit duration (hours)")
    ax.set_title("Grazing transits are shorter")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "duration_vs_b.png", dpi=110)
    print("b = 0.8: duration approx", round(duration_approx(P, aR, kk, 0.8) * 24, 3), "h; b = 1.2 (miss):", duration_approx(P, aR, kk, 1.2))

    # period from spacing
    rng = np.random.default_rng(4)
    epochs = np.arange(8)
    mids = 2.0 + 4.2 * epochs + rng.normal(0, 0.003, 8)
    pf, t0f = fit_period(epochs, mids)
    print(f"period from 8 noisy mid-times: {pf:.4f} d (true 4.2), t0 {t0f:.3f} d")

    # design problem: Earth around the Sun
    aE = a_over_rs(365.25)
    TE = duration_approx(365.25, aE, ke, 0.0)
    nE = points_per_transit(TE, 0.5 / 24)
    d_e = depth(ke)
    sig = sigma_needed(d_e, 3 * nE, 7.0)
    print(f"Earth: a = {a_metres(365.25) / 1e9:.1f} million km = {aE:.1f} Rs; T = {TE * 24:.2f} h; {nE} points per transit")
    print(f"3 transits: {3 * nE} points inside; sigma needed for SNR 7: {sig * 1e6:.1f} ppm per 30-minute point")
    rng = np.random.default_rng(8)
    means = rng.normal(0.0, sig, (4000, 3 * nE)).mean(axis=1)
    print(f"Monte Carlo: the in-transit mean scatters by {means.std() * 1e6:.2f} ppm; depth / scatter = {d_e / means.std():.2f}")
    ns = np.arange(1, 13)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(ns, [sigma_needed(d_e, n_ * nE, 7.0) * 1e6 for n_ in ns], "o-", color="tab:blue")
    ax.axhline(sig * 1e6, color="tab:red", ls=":", lw=1)
    ax.set_xlabel("number of transits observed")
    ax.set_ylabel("allowed noise per 30-minute point (ppm)")
    ax.set_title("Seeing an Earth (84 ppm) at SNR 7: more transits relax the limit", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "noise_needed.png", dpi=110)

# %% [markdown]
# ## Where this stops
# The approximate duration formula assumes a circular orbit and Rs << a. Real light-curve fits
# use the exact geometry, an eccentric orbit and fitted limb-darkening. Session 3 searches a
# noisy light curve for transits when the period is not known.
