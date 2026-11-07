"""Session 3 (Level 3): find a planet in a noisy light curve (detrend, BLS, vetting, false alarms).

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: find the planet in a noisy light curve
# **A. Real-world problem.** A real light curve is not a clean box. It has noise, the star's
# own slow brightness changes (spots rotating in and out of view), and gaps where the
# telescope was not looking. A planet's dip is only a fraction of a percent. How do you
# find a regular tiny dip in that, and how do you know it is not a fluke or an eclipsing
# binary star?
#
# **Plan.** (1) build a synthetic star with a hidden planet (seeded), (2) remove the slow
# variability without eating the transits, (3) search with Box Least Squares (BLS),
# (4) vet the candidate (odd-even check), (5) measure the false-alarm rate on pure noise,
# (6) look at two ways the search fails.
# Everything is a simplified teaching model, not a validated survey pipeline.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G_M_SUN = 1.32712440018e20     # G times the Sun's mass, m^3 / s^2
R_SUN_KM = 695700.0            # km
R_EARTH_KM = 6371.0            # km
DAY = 86400.0                  # seconds in a day
CADENCE = 0.5 / 24.0           # 30 minutes, in days


# %% [markdown]
# ## Step 1: a transit model (from Session 2) and a synthetic star
# `a_over_rs` uses Kepler's third law. `transit_model` is the uniform-disk transit: flux is
# 1 minus the exactly overlapping area of the two circles divided by the star's area.

# %%
def a_over_rs(period_days, m_sun=1.0, r_sun=1.0):
    """Orbit radius divided by stellar radius, from Kepler's third law (circular orbit)."""
    a_m = (G_M_SUN * m_sun * (period_days * DAY) ** 2 / (4 * np.pi ** 2)) ** (1.0 / 3.0)
    return a_m / (r_sun * R_SUN_KM * 1000.0)


def overlap_area(z, k):
    """Overlap area of the unit star disk and a planet disk of radius k whose centre is z away."""
    z = np.abs(np.asarray(z, dtype=float))
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


def transit_model(t, period, t0, k, a_rs, b):
    """Relative flux of a star with one transiting planet on a circular orbit (no limb darkening)."""
    t = np.asarray(t, dtype=float)
    phase = 2 * np.pi * (t - t0) / period
    x = a_rs * np.sin(phase)
    y = b * np.cos(phase)
    z = np.sqrt(x ** 2 + y ** 2)
    z = np.where(np.cos(phase) > 0, z, 1e3)      # planet behind the star: no transit
    return 1.0 - overlap_area(z, k) / np.pi


def time_grid(days=40.0, seed=1, n_gaps=3, drop=0.03):
    """30-minute cadence with a few gaps and a few randomly lost points."""
    rng = np.random.default_rng(seed)
    t = np.arange(0.0, days, CADENCE)
    keep = rng.random(len(t)) > drop
    for _ in range(n_gaps):
        start = rng.uniform(1.0, days - 3.0)
        keep &= ~((t > start) & (t < start + rng.uniform(0.6, 1.5)))
    return t[keep]


def synthetic_star(t, planets, sigma=0.0008, rot_period=7.3, rot_amp=0.004, seed=2):
    """Star = 1 + slow spot variability + transits + white noise. `planets` is a list of dicts."""
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 2 * np.pi, 2)
    star = rot_amp * (np.sin(2 * np.pi * t / rot_period + ph[0])
                      + 0.4 * np.sin(4 * np.pi * t / rot_period + ph[1]))
    flux = np.ones_like(t)
    for p in planets:
        flux *= transit_model(t, p["period"], p["t0"], p["k"], p["a_rs"], p["b"])
    return (1.0 + star) * flux + rng.normal(0.0, sigma, len(t))


def demo_planet():
    return dict(period=4.2, t0=1.3, k=0.07, b=0.3, a_rs=a_over_rs(4.2, 1.0, 1.0))


def demo_lightcurve():
    t = time_grid()
    return t, synthetic_star(t, [demo_planet()])


# %% [markdown]
# ## Step 2: detrending with a moving median
# A median filter replaces each point by the median of its neighbours inside a window. The
# slow stellar variability survives in that smooth curve; divide it out. But if the window
# is shorter than about three transit durations, the median "learns" the transit too and the
# division erases it. Rule of thumb used here: window = at least 3 times the transit
# duration, and much shorter than the variability period.

# %%
def moving_median(t, f, window):
    """Median of f within +-window/2 days of each point (works with gaps)."""
    lo = np.searchsorted(t, t - window / 2)
    hi = np.searchsorted(t, t + window / 2)
    return np.array([np.median(f[a:b]) for a, b in zip(lo, hi)])


def detrend(t, f, window):
    trend = moving_median(t, f, window)
    return f / trend, trend


def in_transit_mask(t, period, t0, width):
    ph = (t - t0 + period / 2) % period - period / 2
    return np.abs(ph) < width / 2


def depth_retained(window, seed=2):
    """Fraction of the true transit depth still present after detrending with this window."""
    t, f = demo_lightcurve()
    p = demo_planet()
    flat, _ = detrend(t, f, window)
    inn = in_transit_mask(t, p["period"], p["t0"], 0.08)
    out = ~in_transit_mask(t, p["period"], p["t0"], 0.4)
    depth_measured = np.median(flat[out]) - np.mean(flat[inn])
    true_depth = 1.0 - transit_model(np.array([p["t0"]]), p["period"], p["t0"], p["k"], p["a_rs"], p["b"])[0]
    return float(depth_measured / true_depth)


# %% [markdown]
# ## Step 3: Box Least Squares (BLS)
# Fold the light curve at a trial period. If the period is right, all transits land on top of
# each other and a box-shaped dip appears. BLS tries many periods, many box durations and many
# start phases, and for each box computes
#
#     SNR = (mean outside - mean inside) / ( sigma * sqrt(1/n_in + 1/n_out) )
#
# where n_in and n_out count the points inside and outside the box and sigma is the noise
# per point. The period with the largest SNR is the candidate.

# %%
def period_grid(pmin, pmax, baseline, dur_min):
    """Periods spaced so the transit slips by at most half a duration over the whole run."""
    step = dur_min / (2.0 * baseline)
    n = int(np.ceil(np.log(pmax / pmin) / step)) + 1
    return pmin * np.exp(step * np.arange(n))


def bls(t, f, periods, durations, sigma, bin_width=0.02):
    """Return dict with snr per period and the best (period, t0, duration, depth)."""
    t = np.asarray(t, dtype=float)
    y = f - np.mean(f)
    n_tot = len(t)
    total = y.sum()
    ms = sorted({max(1, int(round(d / bin_width))) for d in durations})
    snr_best = np.zeros(len(periods))
    best = (-1.0, 0.0, 0.0, 0.0, 0.0)      # snr, period, t0, duration, depth
    for i, per in enumerate(periods):
        nb = int(np.ceil(per / bin_width))
        idx = np.minimum(((t % per) / per * nb).astype(int), nb - 1)
        cnt = np.bincount(idx, minlength=nb).astype(float)
        sm = np.bincount(idx, weights=y, minlength=nb)
        mmax = min(max(ms), nb)
        cc = np.concatenate([[0.0], np.cumsum(np.concatenate([cnt, cnt[:mmax]]))])
        ss = np.concatenate([[0.0], np.cumsum(np.concatenate([sm, sm[:mmax]]))])
        for m in ms:
            if m >= nb:
                continue
            n_in = cc[m:m + nb] - cc[:nb]
            s_in = ss[m:m + nb] - ss[:nb]
            n_out = n_tot - n_in
            ok = (n_in >= 3) & (n_out >= 3)
            if not ok.any():
                continue
            ni = np.where(ok, n_in, 1.0)
            no = np.where(ok, n_out, 1.0)
            depth = (total - s_in) / no - s_in / ni
            snr = np.where(ok, depth / (sigma * np.sqrt(1.0 / ni + 1.0 / no)), -np.inf)
            j = int(np.argmax(snr))
            if snr[j] > snr_best[i]:
                snr_best[i] = snr[j]
            if snr[j] > best[0]:
                t0 = (j + m / 2.0) * per / nb
                best = (float(snr[j]), float(per), float(t0), m * bin_width * per / (nb * bin_width), float(depth[j]))
    return {"snr": snr_best, "periods": np.asarray(periods), "best": best}


def box_duration_days(period, bin_width, m):
    nb = int(np.ceil(period / bin_width))
    return m * period / nb


def run_bls(t, f, sigma=None, pmin=0.8, pmax=15.0, durations=(0.06, 0.08, 0.1, 0.13, 0.17, 0.22, 0.3)):
    if sigma is None:
        sigma = 1.4826 * np.median(np.abs(f - np.median(f)))
    grid = period_grid(pmin, pmax, t.max() - t.min(), min(durations))
    res = bls(t, f, grid, durations, sigma)
    res["sigma"] = sigma
    return res


def refine(t, f, res, width=0.02):
    """Second, finer BLS pass around the best period."""
    p0 = res["best"][1]
    grid = np.linspace(p0 * (1 - width), p0 * (1 + width), 161)
    fine = bls(t, f, grid, (0.06, 0.08, 0.1, 0.13, 0.17, 0.22), res["sigma"], bin_width=0.01)
    return fine["best"]


def alias_snr(res, period):
    """Largest SNR within 1.5 percent of `period` in a BLS result."""
    g = res["periods"]
    sel = np.abs(g / period - 1.0) < 0.015
    return float(res["snr"][sel].max()) if sel.any() else float("nan")


# %% [markdown]
# ## Step 4: fit a transit and measure the planet
# BLS gives period, mid-time, a box duration and a box depth. A box underestimates the depth a
# little (it ignores the rounded ingress and egress). A short grid fit of the transit model
# over the radius ratio k and impact parameter b gives a better k. Then the planet radius in
# Earth radii is k times the assumed stellar radius, converted from solar radii to Earth radii.

# %%
def fold(t, period, t0):
    """Time from the nearest mid-transit, in days, between -period/2 and +period/2."""
    return (t - t0 + period / 2) % period - period / 2


def fit_transit(t, f, period, t0, a_rs):
    """Grid fit of k and b (and a small t0 shift). Returns (k, b, t0, rms)."""
    near = np.abs(fold(t, period, t0)) < 0.3
    tt, ff = t[near], f[near]
    best = (None, None, None, np.inf)
    for dt in np.linspace(-0.03, 0.03, 13):
        for b in (0.0, 0.2, 0.4, 0.6, 0.8):
            for k in np.arange(0.02, 0.13, 0.002):
                r = ff - transit_model(tt, period, t0 + dt, k, a_rs, b)
                rms = float(np.sqrt(np.mean(r ** 2)))
                if rms < best[3]:
                    best = (float(k), float(b), float(t0 + dt), rms)
    return best


def planet_radius_earth(k, r_star_sun):
    """Planet radius in Earth radii from radius ratio k and stellar radius in solar radii."""
    return k * r_star_sun * R_SUN_KM / R_EARTH_KM


# %% [markdown]
# ## Step 5: vetting. An eclipsing binary has odd and even events of different depth
# If BLS folds on half the true period of an eclipsing binary (two stars eclipsing each other,
# the deeper "primary" and a shallower "secondary" eclipse), every second event is a secondary.
# The odd-even check measures the mean depth of odd and even events separately. A planet
# gives equal depths; a binary does not.

# %%
def odd_even(t, f, period, t0, width, sigma):
    """Return (depth_odd, depth_even, significance in sigma) of the difference."""
    n = np.round((t - t0) / period).astype(int)
    inn = in_transit_mask(t, period, t0, width)
    out = ~in_transit_mask(t, period, t0, 3 * width)
    base = np.median(f[out])
    d, e = [], []
    for parity in (0, 1):
        sel = inn & (n % 2 == parity)
        d.append(base - np.mean(f[sel]))
        e.append(sigma / np.sqrt(max(sel.sum(), 1)))
    sig = abs(d[0] - d[1]) / np.hypot(e[0], e[1])
    return float(d[1]), float(d[0]), float(sig)       # (odd, even, significance)


def eclipsing_binary(t, period=6.0, t0=2.0, primary=0.010, secondary=0.008, width=0.12, sigma=0.0008, seed=5):
    """Two eclipses per orbit (box shaped, for teaching): deeper at phase 0, shallower at phase 0.5."""
    rng = np.random.default_rng(seed)
    flux = np.ones_like(t)
    flux[in_transit_mask(t, period, t0, width)] -= primary
    flux[in_transit_mask(t, period, t0 + period / 2, width)] -= secondary
    return flux + rng.normal(0.0, sigma, len(t))


# %% [markdown]
# ## Step 6: how often does pure noise fool BLS? (false-alarm rate)
# Make many light curves of pure white noise (seeded), run the same BLS on each, and record
# the largest SNR found. The fraction above a threshold is the false-alarm rate for that search.

# %%
def noise_max_snr(n_trials=100, seed=11, days=30.0, cadence=1.0 / 24.0):
    """Largest BLS SNR of each of `n_trials` pure-noise light curves (unit noise, 1 hour cadence)."""
    rng = np.random.default_rng(seed)
    t = np.arange(0.0, days, cadence)
    grid = period_grid(1.0, 10.0, days, 0.15)
    out = []
    for _ in range(n_trials):
        f = 1.0 + rng.normal(0.0, 0.001, len(t))
        res = bls(t, f, grid, (0.1, 0.2), 0.001, bin_width=0.05)
        out.append(res["best"][0])
    return np.array(out)


def false_alarm_rate(max_snr, threshold):
    return float(np.mean(np.asarray(max_snr) > threshold))


# %% [markdown]
# ## Step 7: two ways the search fails
# 1. **Aliasing.** If every other transit falls in a data gap, a planet at period P and one at
#    2P explain the data equally well; BLS cannot tell them apart.
# 2. **Period near the run length.** With only one transit in the data, the period is not
#    measured at all: any period long enough that a second transit would fall outside the run fits.

# %%
def alias_case():
    """A run where the odd transits are lost in gaps: returns (t, f, planet)."""
    t, f = demo_lightcurve()
    p = demo_planet()
    n = np.round((t - p["t0"]) / p["period"]).astype(int)
    near = np.abs(fold(t, p["period"], p["t0"])) < 0.6
    keep = ~(near & (n % 2 == 1))
    return t[keep], f[keep], p


def one_transit_case():
    """A 14 day run, planet period 11 d: only one transit is inside the run."""
    t = np.arange(0.0, 14.0, CADENCE)
    p = dict(period=11.0, t0=4.0, k=0.07, b=0.3, a_rs=a_over_rs(11.0, 1.0, 1.0))
    f = synthetic_star(t, [p], rot_amp=0.0, seed=6)
    return t, f, p


# %% [markdown]
# ## Step 8: mini-project data, two planets around a star of assumed radius 0.9 solar radii
# `project_lightcurve()` returns a seeded light curve with two planets. Find them one after the
# other: detrend, run BLS, vet, remove (mask) the found transits, and search again.

# %%
R_STAR_PROJECT = 0.9      # assumed stellar radius, solar radii
M_STAR_PROJECT = 0.9      # assumed stellar mass, solar masses


def project_planets():
    return [dict(period=6.43, t0=2.10, k=0.050, b=0.3, a_rs=a_over_rs(6.43, M_STAR_PROJECT, R_STAR_PROJECT)),
            dict(period=2.71, t0=0.90, k=0.028, b=0.5, a_rs=a_over_rs(2.71, M_STAR_PROJECT, R_STAR_PROJECT))]


def project_lightcurve():
    t = time_grid(days=50.0, seed=21, n_gaps=3)
    return t, synthetic_star(t, project_planets(), sigma=0.0006, rot_period=11.3, rot_amp=0.003, seed=22)


def find_planets(t, f, n_planets=2, window=1.0):
    """Iterative search. Returns a list of dicts with period, t0, duration, depth, snr, k, radius_earth, odd-even."""
    flat, _ = detrend(t, f, window)
    sigma = 1.4826 * np.median(np.abs(flat - np.median(flat)))
    use = np.ones(len(t), dtype=bool)
    found = []
    for _ in range(n_planets):
        res = run_bls(t[use], flat[use], sigma=sigma)
        snr, per, t0, dur, depth = refine(t[use], flat[use], res)
        width = max(0.7 * dur, 0.06)
        odd, even, sig = odd_even(t[use], flat[use], per, t0, width, sigma)
        k_box = float(np.sqrt(depth))
        k, b, t0, _ = fit_transit(t[use], flat[use], per, t0, a_over_rs(per, M_STAR_PROJECT, R_STAR_PROJECT))
        found.append(dict(period=per, t0=t0, duration=dur, depth=depth, snr=snr, k=k, k_box=k_box, b=b,
                          radius_earth=planet_radius_earth(k, R_STAR_PROJECT),
                          depth_odd=odd, depth_even=even, oe_sigma=sig))
        use &= ~in_transit_mask(t, per, t0, 2.5 * dur)
    return found


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t, f = demo_lightcurve()
    p = demo_planet()
    print(f"demo run: {len(t)} points over {t.max():.1f} d, injected period {p['period']} d, depth {p['k'] ** 2 * 1e6:.0f} ppm")

    # --- detrending: wrong and right window
    windows = (0.15, 0.3, 0.5, 1.0, 2.0)
    for w in windows:
        print(f"window {w:4.2f} d keeps {depth_retained(w):5.1%} of the transit depth")
    fig, ax = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
    ax[0].plot(t, f, ".", ms=2, color="0.4")
    for w, c in ((0.15, "tab:red"), (1.0, "tab:green")):
        flat, trend = detrend(t, f, w)
        ax[0].plot(t, trend, color=c, lw=1.2, label=f"trend, window {w} d")
        ax[1 if w < 0.5 else 2].plot(t, flat, ".", ms=2, color=c)
    ax[0].set_ylabel("flux (relative)")
    ax[0].legend(fontsize=8)
    ax[1].set_ylabel("flat flux")
    ax[1].set_title("Too short (0.15 d): the transits are eaten", fontsize=9)
    ax[2].set_ylabel("flat flux")
    ax[2].set_title("Right (1.0 d): the transits survive", fontsize=9)
    ax[2].set_xlabel("time (days)")
    for a in ax:
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "detrend_windows.png", dpi=110)

    # --- BLS periodogram with aliases
    flat, _ = detrend(t, f, 1.0)
    res = run_bls(t, flat)
    snr, per, t0, dur, depth = res["best"]
    print(f"BLS: period {per:.3f} d, t0 {t0:.3f} d, duration {dur:.3f} d, depth {depth * 1e6:.0f} ppm, SNR {snr:.1f}")
    for name, pp in (("P/2", per / 2), ("P", per), ("2P", 2 * per)):
        print(f"  SNR near {name} = {alias_snr(res, pp):.1f}")
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.plot(res["periods"], res["snr"], lw=0.8, color="tab:blue")
    for name, pp in (("P/2", per / 2), ("P", per), ("2P", 2 * per)):
        ax.axvline(pp, color="tab:red", ls=":", lw=1)
        ax.text(pp, ax.get_ylim()[1] * 0.93, name, color="tab:red", ha="center", fontsize=9)
    ax.set_xlabel("trial period (days)")
    ax.set_ylabel("BLS signal-to-noise")
    ax.set_title("BLS periodogram: the true period and its aliases P/2 and 2P")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "periodogram.png", dpi=110)

    # --- phase-folded transit and fit
    snr, per, t0, dur, depth = refine(t, flat, res)
    k, b, t0f, rms = fit_transit(t, flat, per, t0, a_over_rs(per, 1.0, 1.0))
    print(f"refined: period {per:.4f} d, box depth {depth * 1e6:.0f} ppm; fit k {k:.3f}, b {b:.1f}")
    ph = fold(t, per, t0f)
    sel = np.abs(ph) < 0.4
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(ph[sel] * 24, flat[sel], ".", ms=3, color="0.5", label="data folded on the period")
    xs = np.linspace(-0.4, 0.4, 400)
    ax.plot(xs * 24, transit_model(xs, per, 0.0, k, a_over_rs(per, 1.0, 1.0), b), color="tab:red", label=f"model fit, k = {k:.3f}")
    ax.set_xlabel("time from mid-transit (hours)")
    ax.set_ylabel("flat flux (relative)")
    ax.set_title("Phase-folded transit with the fitted model")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "folded_transit.png", dpi=110)

    # --- odd-even
    eb = eclipsing_binary(t)
    eb_flat = eb
    eres = run_bls(t, eb_flat)
    eref = refine(t, eb_flat, eres)
    print(f"binary: BLS period {eref[1]:.3f} d (true orbit 6.0 d)")
    for name, ff, (pp, tt0) in (("planet", flat, (per, t0f)), ("binary", eb_flat, (eref[1], eref[2]))):
        o, e, s = odd_even(t, ff, pp, tt0, 0.08, 0.0008)
        print(f"  {name}: odd depth {o * 1e6:.0f} ppm, even depth {e * 1e6:.0f} ppm, difference {s:.1f} sigma")

    # --- false alarms
    mx = noise_max_snr(100)
    for th in (5, 6, 7):
        print(f"false-alarm rate above SNR {th}: {false_alarm_rate(mx, th):.0%}  (max SNR in {len(mx)} noise runs: {mx.max():.1f})")
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.hist(mx, bins=15, color="tab:gray")
    ax.axvline(res["best"][0], color="tab:red", label=f"planet search SNR {res['best'][0]:.0f}")
    ax.set_xlabel("largest BLS SNR in one pure-noise run")
    ax.set_ylabel("number of runs")
    ax.set_title("Pure noise rarely reaches a high SNR")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "false_alarm.png", dpi=110)

    # --- failure cases
    ta, fa, pa = alias_case()
    fa_flat, _ = detrend(ta, fa, 1.0)
    ra = run_bls(ta, fa_flat)
    print(f"odd transits lost: SNR near P = {alias_snr(ra, 4.2):.1f}, near 2P = {alias_snr(ra, 8.4):.1f}")
    to, fo, po = one_transit_case()
    ro = run_bls(to, fo, pmin=2.0, pmax=14.0)
    good = ro["periods"][ro["snr"] >= 0.9 * ro["snr"].max()]
    print(f"one transit: periods within 90% of the best SNR span {good.min():.1f} to {good.max():.1f} d (true 11.0 d)")

    # --- mini-project
    tp, fp = project_lightcurve()
    for i, pl in enumerate(find_planets(tp, fp), 1):
        print(f"planet {i}: P {pl['period']:.3f} d, depth {pl['depth'] * 1e6:.0f} ppm, k_box {pl['k_box']:.3f}, k_fit {pl['k']:.3f}, "
              f"R {pl['radius_earth']:.1f} Earth radii, SNR {pl['snr']:.1f}, odd-even {pl['oe_sigma']:.1f} sigma")

# %% [markdown]
# ## Where this stops
# Real surveys fit all transit parameters together, model stellar variability with Gaussian
# processes, and test many more false positives (background stars, secondary eclipses, centroid
# shifts). That is the road to the Target: see `promo/roadmap.md`.
