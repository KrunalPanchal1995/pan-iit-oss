"""Session 3 (Level 3): position and clock bias by Gauss-Newton, dilution of precision, relativity.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: solve for position AND the receiver clock, then check against the truth
# **A. Real-world problem.** Your phone's clock is cheap, so every pseudorange it measures is
# wrong by the same unknown amount (the clock bias, times c). The fix: treat the bias as a
# fourth unknown and use at least four satellites. The ranges also carry noise, so we want the
# best fit, and we want to know how the *geometry* of the satellites changes the accuracy.
# Finally, the satellite clocks themselves run at a slightly different rate than clocks on the
# ground, because of relativity. We compute how big that is.
#
# **Honest labels.** Satellite positions are *toy* positions, not real orbits. The Earth is a
# sphere. Noise is random Gaussian noise. This is a teaching model, not a navigation tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

C = 299_792_458.0          # speed of light (m/s)
R_EARTH = 6_371_000.0      # mean Earth radius (m)
R_ORBIT = 26_560_000.0     # toy satellite distance from the Earth's centre (m)
GM = 3.986004418e14        # Earth's gravitational parameter (m^3/s^2)
SEC_PER_DAY = 86400.0


# %% [markdown]
# ## Step 1: a receiver, toy satellites and noisy pseudoranges
# Pseudorange model: rho_i = |s_i - x| + b + noise_i, where x is the receiver position (m) and
# b = c x (receiver clock error) is the clock bias expressed as a distance (m).

# %%
def receiver_on_earth(lat_deg, lon_deg):
    la, lo = np.radians(lat_deg), np.radians(lon_deg)
    return R_EARTH * np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def local_axes(rec):
    """East, north, up unit vectors at the receiver."""
    up = rec / np.linalg.norm(rec)
    east = np.cross([0.0, 0.0, 1.0], up)
    east /= np.linalg.norm(east)
    return east, np.cross(up, east), up


def toy_sats(rec, az_el_deg, radius=R_ORBIT):
    """Toy satellites in given (azimuth, elevation) directions from the receiver, at `radius` from Earth's centre."""
    e, n, u = local_axes(rec)
    out = []
    for az, el in az_el_deg:
        a, h = np.radians(az), np.radians(el)
        d = np.cos(h) * np.sin(a) * e + np.cos(h) * np.cos(a) * n + np.sin(h) * u
        bq = rec @ d
        out.append(rec + (-bq + np.sqrt(bq * bq - rec @ rec + radius * radius)) * d)
    return np.array(out)


GOOD_SKY = [(20, 60), (110, 35), (200, 50), (290, 25), (60, 15), (160, 20), (250, 70), (340, 40)]
POOR_SKY = [(40, 40), (50, 45), (60, 38), (45, 52), (55, 35), (35, 47)]     # all clustered in one patch of sky


def pseudoranges(sats, rec, bias_m=0.0, sigma_m=0.0, rng=None, sat_clock_err_m=None):
    """Simulated pseudoranges (m): true distance + bias + optional satellite clock errors + Gaussian noise."""
    rho = np.linalg.norm(sats - rec, axis=1) + bias_m
    if sat_clock_err_m is not None:
        rho = rho + np.asarray(sat_clock_err_m, float)
    if sigma_m > 0:
        rho = rho + (rng or np.random.default_rng(0)).normal(0.0, sigma_m, len(rho))
    return rho


# %% [markdown]
# ## Step 2: Gauss-Newton
# Guess (x, b). Predict each pseudorange. The mismatch (residual) is linked to a correction by a
# *Jacobian* matrix G whose row for satellite i is [-(unit vector from receiver to satellite), 1].
# Solve G dz = residual in the least-squares sense, update, and repeat until dz is tiny.

# %%
def gauss_newton(sats, rho, z0=None, tol=1e-4, max_iter=20):
    """Return (x, b, iterations, history). z0 = (x, y, z, b) start; default is Earth's centre, b = 0."""
    z = np.zeros(4) if z0 is None else np.array(z0, float)
    hist = [z.copy()]
    for k in range(1, max_iter + 1):
        diff = sats - z[:3]
        dist = np.linalg.norm(diff, axis=1)
        G = np.hstack([-diff / dist[:, None], np.ones((len(sats), 1))])
        resid = rho - (dist + z[3])
        dz, *_ = np.linalg.lstsq(G, resid, rcond=None)
        z = z + dz
        hist.append(z.copy())
        if np.linalg.norm(dz) < tol:
            return z[:3], z[3], k, np.array(hist)
    return z[:3], z[3], max_iter, np.array(hist)


# %% [markdown]
# ## Step 3: dilution of precision (DOP)
# With the same noise sigma on every range, the covariance of the solution is sigma^2 (G^T G)^-1.
# Write Q = (G^T G)^-1. Then PDOP = sqrt(Q11 + Q22 + Q33) is the factor by which range noise is
# multiplied into 3D position error; TDOP is the same for the clock; HDOP and VDOP split the
# position part into horizontal and vertical using the local east-north-up axes.

# %%
def dop(sats, x):
    """Return dict with GDOP, PDOP, HDOP, VDOP, TDOP at position x for these satellites."""
    diff = sats - x
    G = np.hstack([-diff / np.linalg.norm(diff, axis=1)[:, None], np.ones((len(sats), 1))])
    Q = np.linalg.inv(G.T @ G)
    e, n, u = local_axes(x)
    R = np.array([e, n, u])
    Qenu = R @ Q[:3, :3] @ R.T
    return {"GDOP": float(np.sqrt(np.trace(Q))), "PDOP": float(np.sqrt(np.trace(Q[:3, :3]))),
            "HDOP": float(np.sqrt(Qenu[0, 0] + Qenu[1, 1])), "VDOP": float(np.sqrt(Qenu[2, 2])),
            "TDOP": float(np.sqrt(Q[3, 3]))}


def monte_carlo_error(sats, rec, sigma_m, trials=2000, seed=1, bias_m=0.0):
    """RMS 3D position error (m) over many noisy fixes."""
    rng = np.random.default_rng(seed)
    errs = np.empty(trials)
    for i in range(trials):
        rho = pseudoranges(sats, rec, bias_m, sigma_m, rng)
        x, _, _, _ = gauss_newton(sats, rho)
        errs[i] = np.linalg.norm(x - rec)
    return float(np.sqrt(np.mean(errs ** 2)))


# %% [markdown]
# ## Step 4: relativity and the satellite clock
# Two small effects change the rate of a GPS satellite clock compared with a clock on the ground.
# Well-known approximate results (we compute them from the formulas below):
# * **General relativity**: higher up, gravity is weaker and the clock runs *fast*, by
#   fraction GM/c^2 x (1/R_earth - 1/r_sat).
# * **Special relativity**: a moving clock runs *slow*, by fraction v^2 / (2 c^2), where for a
#   circular orbit v^2 = GM / r_sat.

# %%
def relativity_offsets(r_sat=R_ORBIT, r_ground=R_EARTH):
    """Return (gravity, motion, net) fractional rate offsets of a satellite clock (dimensionless)."""
    grav = GM / C**2 * (1.0 / r_ground - 1.0 / r_sat)
    motion = -(GM / r_sat) / (2.0 * C**2)
    return grav, motion, grav + motion


def microseconds_per_day(frac):
    return frac * SEC_PER_DAY * 1e6


def drift_range_km(frac, days):
    """Range error (km) built up by a clock rate error `frac` after `days` if it is left uncorrected."""
    return C * frac * days * SEC_PER_DAY / 1e3


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    rec = receiver_on_earth(19.0, 73.0)
    bias = 0.35e-3 * C                                    # receiver clock 0.35 ms fast, as a distance
    sats = toy_sats(rec, GOOD_SKY[:4])
    rho = pseudoranges(sats, rec, bias, sigma_m=5.0, rng=np.random.default_rng(7))
    x, b, k, hist = gauss_newton(sats, rho)
    print(f"4 satellites, sigma 5 m: position error {np.linalg.norm(x - rec):.1f} m, bias {b / C * 1e3:.4f} ms (true 0.35), {k} iterations")
    x0, b0, k0, _ = gauss_newton(sats, pseudoranges(sats, rec, bias))
    print(f"noise-free: position error {np.linalg.norm(x0 - rec):.2e} m, bias error {abs(b0 - bias):.2e} m, {k0} iterations")

    for name, sky in (("good 4", GOOD_SKY[:4]), ("good 8", GOOD_SKY), ("poor 6 (clustered)", POOR_SKY)):
        s = toy_sats(rec, sky)
        d = dop(s, rec)
        rms = monte_carlo_error(s, rec, 5.0)
        print(f"{name:20s} PDOP {d['PDOP']:.2f} HDOP {d['HDOP']:.2f} VDOP {d['VDOP']:.2f} TDOP {d['TDOP']:.2f}  "
              f"predicted rms {5.0 * d['PDOP']:.1f} m, simulated rms {rms:.1f} m")

    g, m, net = relativity_offsets()
    print(f"gravity {microseconds_per_day(g):+.1f} us/day, motion {microseconds_per_day(m):+.1f} us/day, net {microseconds_per_day(net):+.1f} us/day")
    print(f"left uncorrected: range error {drift_range_km(net, 1):.1f} km after 1 day, {drift_range_km(net, 10):.0f} km after 10 days")

    # common satellite clock error is absorbed by the bias, uneven error is not
    s4 = toy_sats(rec, GOOD_SKY[:4])
    com = np.full(4, C * net * SEC_PER_DAY)
    xa, ba, _, _ = gauss_newton(s4, pseudoranges(s4, rec, bias, sat_clock_err_m=com))
    one = np.array([C * net * SEC_PER_DAY, 0, 0, 0])
    xb, _, _, _ = gauss_newton(s4, pseudoranges(s4, rec, bias, sat_clock_err_m=one))
    print(f"one day uncorrected on ALL 4 clocks: position error {np.linalg.norm(xa - rec):.3f} m (absorbed by the bias)")
    print(f"one day uncorrected on ONE clock:    position error {np.linalg.norm(xb - rec) / 1e3:.1f} km")

    # figure 1: convergence
    errs = [np.linalg.norm(h[:3] - rec) for h in hist]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.semilogy(range(len(errs)), np.maximum(errs, 1e-3), "o-")
    ax.set_xlabel("Gauss-Newton iteration")
    ax.set_ylabel("position error (m, log scale)")
    ax.set_title("Starting at the Earth's centre, the fix converges in a few steps")
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "convergence.png", dpi=120)

    # figure 2: simulated error vs DOP prediction for many geometries
    rng = np.random.default_rng(3)
    pd, er = [], []
    for _ in range(25):
        k_sat = int(rng.integers(5, 9))
        sky = [(rng.uniform(0, 360), rng.uniform(10, 80)) for _ in range(k_sat)]
        s = toy_sats(rec, sky)
        pd.append(dop(s, rec)["PDOP"])
        er.append(monte_carlo_error(s, rec, 5.0, trials=300, seed=int(rng.integers(1, 10**6))))
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(pd, er, "o", ms=4, label="simulated rms error (300 fixes each)")
    xx = np.linspace(min(pd), max(pd), 20)
    ax2.plot(xx, 5.0 * xx, "-", label="prediction: sigma x PDOP")
    ax2.set_xlabel("PDOP (no unit)")
    ax2.set_ylabel("rms position error (m), sigma = 5 m")
    ax2.set_title("Geometry sets the multiplier on the noise")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "dop_validation.png", dpi=120)

    # figure 3: relativity drift
    days = np.linspace(0, 10, 11)
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.plot(days, [drift_range_km(net, d) for d in days], "o-", label="net offset left uncorrected")
    ax3.plot(days, [drift_range_km(g, d) for d in days], "--", label="gravity part only")
    ax3.plot(days, [drift_range_km(m, d) for d in days], ":", label="motion part only")
    ax3.set_xlabel("days")
    ax3.set_ylabel("range error built up (km)")
    ax3.set_title("Relativity: about 11 km of range error per day if uncorrected")
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "relativity_drift.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Real receivers also correct for the atmosphere, use real orbits, weight satellites by quality and
# reject faulty ones. The roadmap in `promo/roadmap.md` lists these steps.
