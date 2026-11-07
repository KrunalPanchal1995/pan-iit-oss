"""Session 3 (Level 3): locating a quake from P picks only (Geiger's method), with errors.

Educational only. This is not an earthquake warning or prediction tool:
earthquakes cannot be predicted. Flat-map (2-D) model, constant speed unless stated.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: Geiger's method, pick errors and station geometry
# **A. Real-world problem.** In real life we do not know when the quake began (origin time t0),
# and arrival times are picked by eye or by an algorithm with errors of a fraction of a second.
# How do we find the epicentre, how wrong can it be, and which networks are good?
#
# **Plan.** (1) unknowns (x, y, t0) from P arrivals at N >= 4 stations, (2) linearise and
# iterate (Gauss-Newton, Geiger's method), (3) Monte Carlo of pick errors, (4) station geometry
# through the condition number and covariance, (5) a two-layer failure case, (6) a simple
# magnitude formula, (7) the 95 percent error ellipse.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

VP = 6.0   # km/s, APPROXIMATE typical crust P speed

# made-up networks (km) and a made-up quake (x km, y km, origin time s)
GOOD = np.array([[5.0, 10.0], [95.0, 5.0], [100.0, 70.0], [50.0, 100.0], [0.0, 80.0]])   # surrounds the quake
BAD = np.array([[0.0, 0.0], [12.0, 6.0], [24.0, 0.0], [36.0, 7.0], [48.0, 2.0]])          # all in one corner
QUAKE = np.array([55.0, 40.0, 3.0])


# %% [markdown]
# ## Step 1: predicted arrival times
# P arrival at station i:  t_i = t0 + R_i / vp, with R_i = sqrt((xi - x)^2 + (yi - y)^2).
# The unknowns are (x, y, t0): three numbers, so we need at least three stations, and a fourth
# lets us check the result and average the picks. We use P only because S is harder to pick.

# %%
def p_arrivals(m, stations, vp=VP):
    """Predicted P arrival times (s) for the model m = (x, y, t0)."""
    s = np.asarray(stations, dtype=float)
    return m[2] + np.hypot(s[:, 0] - m[0], s[:, 1] - m[1]) / vp


# %% [markdown]
# ## Step 2: Geiger's method (Gauss-Newton)
# The model is not linear in (x, y), so we guess, linearise, solve and repeat. Residual
# r_i = observed - predicted. A small change dm = (dx, dy, dt0) changes t_i by
#     J_i . dm   with   J_i = ( -(xi - x) / (vp R_i),  -(yi - y) / (vp R_i),  1 ).
# Solve J dm = r by least squares, update m, repeat until the step is tiny.
# Each step is capped at 25 km so that a very bad geometry cannot throw the guess far away.

# %%
def jacobian(m, stations, vp=VP):
    s = np.asarray(stations, dtype=float)
    dx, dy = s[:, 0] - m[0], s[:, 1] - m[1]
    R = np.maximum(np.hypot(dx, dy), 1e-9)
    return np.column_stack([-dx / (vp * R), -dy / (vp * R), np.ones(len(R))])


def geiger(stations, t_obs, vp=VP, start=None, max_iter=30, tol=1e-8):
    """Least-squares (x, y, t0) from P arrival times. Returns (m, history, J_at_solution)."""
    s = np.asarray(stations, dtype=float)
    t_obs = np.asarray(t_obs, dtype=float)
    if len(t_obs) < 4:
        raise ValueError("need at least 4 stations (3 unknowns plus one check)")
    if start is None:
        x0, y0 = s.mean(axis=0)
        t00 = float(np.mean(t_obs - np.hypot(s[:, 0] - x0, s[:, 1] - y0) / vp))
        start = (x0, y0, t00)
    m = np.array(start, dtype=float)
    hist = [m.copy()]
    for _ in range(max_iter):
        r = t_obs - p_arrivals(m, s, vp)
        dm = np.linalg.lstsq(jacobian(m, s, vp), r, rcond=None)[0]
        step = np.linalg.norm(dm[:2])
        if step > 25.0:
            dm = dm * 25.0 / step
        m = m + dm
        hist.append(m.copy())
        if np.linalg.norm(dm[:2]) < tol:
            break
    return m, hist, jacobian(m, s, vp)


# %% [markdown]
# ## Step 3: picking errors (Monte Carlo)
# Add Gaussian noise of standard deviation sigma to every pick, locate, repeat many times
# with a fixed random seed, and look at the scatter of the epicentre errors.

# %%
def monte_carlo(stations, quake, sigma, n=2000, seed=7, vp=VP):
    """Horizontal epicentre errors (km) for n noisy sets of picks."""
    rng = np.random.default_rng(seed)
    t_true = p_arrivals(quake, stations, vp)
    errs = np.empty(n)
    for k in range(n):
        m, _, _ = geiger(stations, t_true + sigma * rng.standard_normal(len(t_true)), vp)
        errs[k] = np.hypot(m[0] - quake[0], m[1] - quake[1])
    return errs


# %% [markdown]
# ## Step 4: station geometry
# Linear theory says the covariance of the solution is C = sigma^2 (J^T J)^-1. Two numbers
# summarise the network: the condition number of J (big = nearly degenerate) and the
# horizontal dilution sqrt(Cxx + Cyy) / sigma (km of epicentre error per second of pick error).

# %%
def condition_number(J):
    return float(np.linalg.cond(J))


def covariance(J, sigma):
    """3x3 covariance of (x, y, t0) for independent picks with standard deviation sigma (s)."""
    return sigma ** 2 * np.linalg.inv(J.T @ J)


def horizontal_dilution(J):
    C = np.linalg.inv(J.T @ J)
    return float(np.sqrt(C[0, 0] + C[1, 1]))


def ellipse95(J, sigma):
    """95 percent error ellipse of the epicentre: (semi-major km, semi-minor km, angle of major axis, degrees)."""
    C = covariance(J, sigma)[:2, :2]
    w, v = np.linalg.eigh(C)
    k = 5.991   # chi-square, 2 degrees of freedom, 95 percent
    ang = np.degrees(np.arctan2(v[1, 1], v[0, 1]))
    return float(np.sqrt(k * w[1])), float(np.sqrt(k * w[0])), float(ang)


# %% [markdown]
# ## Step 5: a failure case, a layered Earth
# Real speed increases with depth. Toy: a surface layer (thickness H, speed v1) over a faster
# half-space (v2). Close stations get the direct wave, far stations the faster wave that
# dives and runs along the boundary (a head wave). If we pretend the speed is constant, the
# arrival times cannot all be right and the epicentre is biased.

# %%
H_TOY, V1_TOY, V2_TOY = 15.0, 5.0, 7.0


def first_arrival_two_layer(x_km, H=H_TOY, v1=V1_TOY, v2=V2_TOY):
    """First P arrival time (s) at surface distance x for a surface source, two layers."""
    x = np.asarray(x_km, dtype=float)
    direct = x / v1
    head = x / v2 + 2.0 * H * np.sqrt(v2 ** 2 - v1 ** 2) / (v1 * v2)
    return np.minimum(direct, head)


def crossover_distance(H=H_TOY, v1=V1_TOY, v2=V2_TOY):
    return 2.0 * H * np.sqrt((v2 + v1) / (v2 - v1))


def locate_layered(stations, quake, v_assumed=VP):
    """Generate two-layer arrivals, locate them assuming constant v. Returns (m, error_km, rms_s)."""
    s = np.asarray(stations, dtype=float)
    d = np.hypot(s[:, 0] - quake[0], s[:, 1] - quake[1])
    t = quake[2] + first_arrival_two_layer(d)
    m, _, _ = geiger(s, t, v_assumed)
    rms = float(np.sqrt(np.mean((t - p_arrivals(m, s, v_assumed)) ** 2)))
    return m, float(np.hypot(m[0] - quake[0], m[1] - quake[1])), rms


# %% [markdown]
# ## Step 6: magnitude from amplitude and distance (approximate)
# A far-away quake looks smaller, so the amplitude must be corrected for distance. One simple
# textbook form uses the S-P time dt as a proxy for distance:
#     ML = log10(A) + 3 log10(8 dt) - 2.92     (A in mm on a Wood-Anderson seismograph, dt in s).
# It is an APPROXIMATE educational formula, not what agencies publish.

# %%
def ml_magnitude(amp_mm, sp_s):
    """Richter-style local magnitude from peak amplitude (mm) and S-P time (s). Approximate."""
    return float(np.log10(amp_mm) + 3.0 * np.log10(8.0 * sp_s) - 2.92)


def amplitude_from_ml(ml, sp_s):
    return float(10.0 ** (ml - 3.0 * np.log10(8.0 * sp_s) + 2.92))


# %% [markdown]
# ## Step 7: the mini-project in one function
# Five stations, noisy picks, an epicentre error and a 95 percent ellipse.

# %%
def mini_project(seed=3, sigma=0.1, stations=GOOD, quake=QUAKE):
    rng = np.random.default_rng(seed)
    t_obs = p_arrivals(quake, stations) + sigma * rng.standard_normal(len(stations))
    m, hist, J = geiger(stations, t_obs)
    err = float(np.hypot(m[0] - quake[0], m[1] - quake[1]))
    a, b, ang = ellipse95(J, sigma)
    return {"m": m, "error_km": err, "semi_major": a, "semi_minor": b, "angle_deg": ang, "history": hist, "J": J}


# %% [markdown]
# ## Step 8: see it
# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib.patches import Ellipse

    OUT.mkdir(exist_ok=True)
    t_true = p_arrivals(QUAKE, GOOD)
    m, hist, J = geiger(GOOD, t_true)
    print("noise-free Geiger: iterations", len(hist) - 1, "result", m.round(4))
    print("errors per iteration (km):", [round(float(np.hypot(h[0] - 55, h[1] - 40)), 4) for h in hist])

    res = mini_project()
    print("mini-project: error %.2f km, 95%% ellipse %.2f x %.2f km" % (res["error_km"], res["semi_major"], res["semi_minor"]))

    fig, ax = plt.subplots(figsize=(5.8, 5.6))
    h = np.array(res["history"])
    ax.plot(h[:, 0], h[:, 1], "o-", color="#e76f51", ms=4, label="Gauss-Newton path")
    ax.plot(GOOD[:, 0], GOOD[:, 1], "k^", label="stations")
    ax.plot(55, 40, "r*", ms=16, label="true epicentre")
    ax.add_patch(Ellipse(res["m"][:2], 2 * res["semi_major"], 2 * res["semi_minor"], angle=res["angle_deg"], fill=False, color="#264653"))
    ax.set_xlabel("east (km)")
    ax.set_ylabel("north (km)")
    ax.set_title("Locating from noisy P picks (sigma 0.1 s)")
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT / "geiger_path.png", dpi=120)

    sig = np.array([0.05, 0.1, 0.2, 0.4])
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for name, net, col in (("surrounding network", GOOD, "#2a9d8f"), ("one-sided network", BAD, "#d9534f")):
        med, p95 = [], []
        for sg in sig:
            e = monte_carlo(net, QUAKE, sg, n=1000)
            med.append(np.median(e))
            p95.append(np.percentile(e, 95))
            print(f"{name:20s} sigma {sg:.2f} s: median {med[-1]:7.2f} km, 95th percentile {p95[-1]:8.2f} km")
        ax2.plot(sig, med, "o-", color=col, label=name + " (median)")
        ax2.plot(sig, p95, "s--", color=col, alpha=0.6, label=name + " (95th percentile)")
    ax2.set_yscale("log")
    ax2.set_xlabel("pick error sigma (s)")
    ax2.set_ylabel("epicentre error (km)")
    ax2.set_title("Error grows with sigma, and geometry matters")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend(fontsize=7)
    fig2.tight_layout()
    fig2.savefig(OUT / "error_vs_sigma.png", dpi=120)

    for name, net in (("surrounding", GOOD), ("one-sided", BAD)):
        mm, e, rms = locate_layered(net, QUAKE)
        print(f"two-layer toy, {name} network, constant 6.0 km/s: epicentre off by {e:.2f} km, rms residual {rms:.3f} s")
    xx = np.linspace(0, 200, 201)
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.plot(xx, first_arrival_two_layer(xx), color="#264653", label="two-layer first arrival")
    ax3.plot(xx, xx / VP, color="#e9c46a", ls="--", label="constant 6.0 km/s")
    ax3.axvline(crossover_distance(), color="gray", ls=":")
    ax3.set_xlabel("distance from the source (km)")
    ax3.set_ylabel("first P arrival (s)")
    ax3.set_title("A kinked curve cannot be matched by one straight line")
    ax3.grid(alpha=0.3)
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(OUT / "two_layer.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
