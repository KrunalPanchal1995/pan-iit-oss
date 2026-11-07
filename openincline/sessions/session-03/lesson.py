"""Session 3 (Level 3): a time-stepping simulation, validated, with uncertainty, and a rolling cylinder.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulate the block and check it against the formulas
# **A. Real-world problem.** To measure a friction coefficient you tilt a board slowly until the
# block slips. Your eye cannot see the exact instant, and the coefficient is never known exactly.
# We simulate the experiment step by step, check the simulation against the exact formulas,
# and ask how much an uncertain mu changes the answer.
#
# **Plan.** (1) a stepping rule with a "stuck" and a "sliding" state, (2) validate against
# a = g (sin t - mu_k cos t) and against atan(mu_s), (3) sensitivity to mu, (4) a rolling cylinder
# for comparison, (5) the mini-project: estimate mu_s from tilt trials.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G = 9.81  # gravity, m/s^2


# %% [markdown]
# ## Step 1: the stepping rule
# Time is cut into small steps of length dt. At each step:
#
# - **stuck** (v = 0): compare the slope pull m g sin t with the static limit mu_s m g cos t.
#   If the pull is larger, the block starts sliding. Otherwise nothing moves.
# - **sliding** (v > 0): a = g (sin t - mu_k cos t); update x by x + v dt + (1/2) a dt^2 and
#   v by v + a dt. If v would become negative the block stops and is stuck again.
#
# The ramp angle may change in time (theta_fn), so we can also tilt the ramp slowly, as in the
# real experiment. Mass cancels, so it does not appear.

# %%
def simulate_block(theta_fn, mu_s, mu_k, T, dt=1e-3, g=G):
    """Slide a block down a ramp whose angle (degrees) is theta_fn(t). Returns a dict of arrays:
    t, x (m down the slope), v (m/s), theta (degrees), sliding (bool), and slip_angle (degrees, or None)."""
    n = int(round(T / dt))
    t = np.arange(n + 1) * dt
    x, v = np.zeros(n + 1), np.zeros(n + 1)
    theta = np.array([theta_fn(ti) for ti in t], dtype=float)
    sliding = np.zeros(n + 1, dtype=bool)
    slip_angle = None
    for i in range(n):
        th = np.radians(theta[i])
        s, c = np.sin(th), np.cos(th)
        if not sliding[i]:
            if s > mu_s * c:                       # pull beats the static limit
                sliding[i] = True
                if slip_angle is None:
                    slip_angle = float(theta[i])
            else:
                x[i + 1], v[i + 1] = x[i], 0.0
                continue
        a = g * (s - mu_k * c)
        v_new = v[i] + a * dt
        if v_new <= 0.0:                           # decelerated to rest: stuck again
            x[i + 1] = x[i] + (v[i] ** 2 / (2 * -a) if a < 0 else 0.0)
            v[i + 1] = 0.0
            sliding[i + 1] = False
            continue
        x[i + 1] = x[i] + v[i] * dt + 0.5 * a * dt * dt
        v[i + 1] = v_new
        sliding[i + 1] = True
    return {"t": t, "x": x, "v": v, "theta": theta, "sliding": sliding, "slip_angle": slip_angle}


def analytic_acceleration(theta_deg, mu_k, g=G):
    """Exact sliding acceleration (m/s^2)."""
    t = np.radians(theta_deg)
    return g * (np.sin(t) - mu_k * np.cos(t))


def analytic_slip_angle(mu_s):
    """Exact slip angle (degrees): tan t = mu_s."""
    return float(np.degrees(np.arctan(mu_s)))


def tilt_experiment(mu_s, mu_k, rate_deg_per_s=0.5, dt=1e-3):
    """Tilt the ramp from 0 at a steady rate until the block slips. Returns the simulated slip angle."""
    T = (analytic_slip_angle(mu_s) + 5.0) / rate_deg_per_s   # run a little past the expected slip
    out = simulate_block(lambda t: rate_deg_per_s * t, mu_s, mu_k, T, dt)
    return out["slip_angle"]


# %% [markdown]
# ## Step 2: validation
# Two exact references: (a) at a fixed angle above the slide angle, x(t) = (1/2) a t^2 with
# a = g (sin t - mu_k cos t); (b) in the tilting test the block must slip at atan(mu_s).
# We also change dt to see whether the answer stops changing.

# %%
def validate_fixed_angle(theta_deg, mu_s, mu_k, T=2.0, dt=1e-3):
    """Largest difference (m) between simulated and exact x(t)."""
    out = simulate_block(lambda t: theta_deg, mu_s, mu_k, T, dt)
    a = analytic_acceleration(theta_deg, mu_k)
    return float(np.max(np.abs(out["x"] - 0.5 * a * out["t"] ** 2)))


# %% [markdown]
# ## Step 3: sensitivity to the friction coefficient
# A measured mu_s is never exact. Because tan t = mu_s, a small error d(mu) in mu_s moves
# the slide angle by d(theta) = d(mu) / (1 + mu^2) (in radians). For mu_s = 0.5 and an error of
# 0.05 this is 0.05 / 1.25 = 0.04 rad, about 2.3 degrees.

# %%
def slip_angle_range(mu_s, d_mu):
    """(low, high) slide angles in degrees for mu_s - d_mu and mu_s + d_mu."""
    return analytic_slip_angle(mu_s - d_mu), analytic_slip_angle(mu_s + d_mu)


def slip_angle_sensitivity(mu_s):
    """Degrees of slide angle per unit change of mu_s: (180 / pi) / (1 + mu_s^2)."""
    return float(np.degrees(1.0 / (1.0 + mu_s ** 2)))


# %% [markdown]
# ## Step 4: a rolling cylinder for comparison
# A cylinder that rolls without slipping turns part of its energy into spin. With I the moment of
# inertia about its axis, m its mass and r its radius, a = g sin t / (1 + I / (m r^2)).
# A solid cylinder has I = (1/2) m r^2, a hollow tube I = m r^2. Friction does no work here; it only
# stops the contact point from slipping, which needs mu_s >= tan t * k / (1 + k) with k = I / (m r^2).

# %%
def rolling_acceleration(theta_deg, k, g=G):
    """Acceleration (m/s^2) of a rolling body with k = I / (m r^2)."""
    return g * np.sin(np.radians(theta_deg)) / (1.0 + k)


def rolls_without_slipping(theta_deg, k, mu_s):
    """True if static friction is large enough to keep rolling."""
    return bool(mu_s >= np.tan(np.radians(theta_deg)) * k / (1.0 + k))


def descent_time(a, distance):
    """Time (s) to travel `distance` from rest with constant acceleration a."""
    return float(np.sqrt(2.0 * distance / a))


# %% [markdown]
# ## Step 5: mini-project data
# A real measurement gives a list of tilt angles, one per trial, at which the block slipped.
# `synthetic_tilt_trials` makes a made-up (synthetic) data set so that you can test your analysis
# before you collect your own. The true mu_s is the function argument.

# %%
def synthetic_tilt_trials(true_mu=0.42, n=12, spread_deg=1.2, seed=7):
    """Made-up slip angles (degrees): atan(true_mu) plus random reading and surface noise."""
    rng = np.random.default_rng(seed)
    return np.round(np.degrees(np.arctan(true_mu)) + spread_deg * rng.standard_normal(n), 1)


def estimate_mu(angles_deg):
    """Return (mu_s, mu_low, mu_high): tan of the mean angle and of mean +- 2 standard errors."""
    a = np.asarray(angles_deg, dtype=float)
    mean = a.mean()
    sem = a.std(ddof=1) / np.sqrt(len(a))
    f = lambda d: float(np.tan(np.radians(d)))
    return f(mean), f(mean - 2 * sem), f(mean + 2 * sem)


# %% [markdown]
# ## Step 6: see it
# Figures: simulation against the exact curve (block and cylinders), the tilting test, and the
# sensitivity band.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    mu_s, mu_k, th = 0.40, 0.30, 30.0
    err = validate_fixed_angle(th, mu_s, mu_k)
    print(f"fixed 30 degrees, mu_s 0.40, mu_k 0.30: a = {analytic_acceleration(th, mu_k):.3f} m/s^2, "
          f"largest |x_sim - x_exact| over 2 s = {err:.2e} m")
    for dt in (4e-3, 2e-3, 1e-3):
        print(f"  tilt test dt = {dt:.0e}: slip angle {tilt_experiment(0.5, 0.4, 0.5, dt):.4f} degrees "
              f"(exact {analytic_slip_angle(0.5):.4f})")
    for rate in (0.5, 2.0, 5.0):
        print(f"  tilt rate {rate} deg/s: slip angle {tilt_experiment(0.5, 0.4, rate):.3f} degrees")
    lo, hi = slip_angle_range(0.5, 0.05)
    print(f"mu_s = 0.50 +- 0.05 -> slide angle {lo:.2f} to {hi:.2f} degrees (spread {hi - lo:.2f}); "
          f"linear estimate {2 * 0.05 * slip_angle_sensitivity(0.5):.2f} degrees")
    kk = {"frictionless block": 0.0, "rough block (mu_k 0.30)": None, "solid cylinder": 0.5, "hollow tube": 1.0}
    for name, k in kk.items():
        a = analytic_acceleration(th, mu_k) if k is None else (
            analytic_acceleration(th, 0.0) if k == 0.0 else rolling_acceleration(th, k))
        print(f"  30 degrees: {name}: a = {a:.3f} m/s^2, time for 2 m = {descent_time(a, 2.0):.3f} s")
    print(f"  solid cylinder rolls without slipping at 30 degrees with mu_s 0.2? {rolls_without_slipping(30, 0.5, 0.2)}; "
          f"with mu_s 0.1? {rolls_without_slipping(30, 0.5, 0.1)}")
    ang = synthetic_tilt_trials()
    est = estimate_mu(ang)
    print("synthetic trials (degrees):", ang.tolist())
    print(f"mean {ang.mean():.2f} degrees -> mu_s = {est[0]:.3f} (range {est[1]:.3f} to {est[2]:.3f}); true value 0.42")
    np.savetxt(OUT / "ramp_trials.csv", np.column_stack([np.arange(1, len(ang) + 1), ang]), delimiter=",",
               header="trial,slip_angle_deg", comments="", fmt=["%d", "%.1f"])

    out = simulate_block(lambda t: th, mu_s, mu_k, 2.0)
    t = out["t"]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(t, 0.5 * analytic_acceleration(th, mu_k) * t ** 2, color="gray", lw=4, alpha=0.5, label="exact block")
    ax.plot(t[::100], out["x"][::100], "o", color="tab:blue", label="simulated block")
    ax.plot(t, 0.5 * analytic_acceleration(th, 0.0) * t ** 2, ls="--", label="frictionless block")
    ax.plot(t, 0.5 * rolling_acceleration(th, 0.5) * t ** 2, label="solid cylinder (rolling)")
    ax.plot(t, 0.5 * rolling_acceleration(th, 1.0) * t ** 2, label="hollow tube (rolling)")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("distance down the slope (m)")
    ax.set_title("30 degrees: simulation matches the formula")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "sim_vs_exact.png", dpi=120)

    tilt = simulate_block(lambda t: 0.5 * t, 0.5, 0.4, 70.0)
    fig2, (axa, axb) = plt.subplots(2, 1, figsize=(6.4, 5), sharex=True)
    axa.plot(tilt["t"], tilt["theta"])
    axa.axhline(analytic_slip_angle(0.5), color="red", ls="--", label="atan(mu_s) = 26.57 degrees")
    axa.set_ylabel("ramp angle (degrees)")
    axa.legend()
    axa.grid(alpha=0.3)
    axb.plot(tilt["t"], tilt["x"] * 100)
    axb.set_ylabel("block position (cm)")
    axb.set_xlabel("time (s)")
    axb.grid(alpha=0.3)
    axa.set_title("Slow tilt: nothing moves until the slide angle")
    fig2.tight_layout()
    fig2.savefig(OUT / "tilt_test.png", dpi=120)

    mus = np.linspace(0.1, 1.0, 91)
    fig3, ax3 = plt.subplots(figsize=(6.4, 4.2))
    ax3.plot(mus, [analytic_slip_angle(m_) for m_ in mus], label="slide angle atan(mu_s)")
    ax3.fill_between(mus, [analytic_slip_angle(max(m_ - 0.05, 0)) for m_ in mus],
                     [analytic_slip_angle(m_ + 0.05) for m_ in mus], alpha=0.25, label="mu_s +- 0.05")
    ax3.set_xlabel("static friction coefficient mu_s (no unit)")
    ax3.set_ylabel("slide angle (degrees)")
    ax3.set_title("An uncertain mu_s means an uncertain slide angle")
    ax3.grid(alpha=0.3)
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(OUT / "sensitivity.png", dpi=120)
    print("saved figures and ramp_trials.csv in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), run the checkpoint,
# then start the mini-project.
