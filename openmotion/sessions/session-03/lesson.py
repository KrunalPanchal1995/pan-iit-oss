"""Session 3 (Level 3): velocity and acceleration from noisy position data, validated.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: differentiating and integrating real, noisy data
# **A. Real-world problem.** A phone camera or a GPS gives you positions at fixed time steps,
# each wrong by a little. You want velocity and acceleration, which are slopes of slopes.
# Slopes magnify small errors. How much, how can we tame it, and how do we know the answer
# is right? We test every method on a motion whose true answer we know exactly.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
A_DRIFT, A_WAVE, W = 8.0, 3.0, 1.2     # x(t) = 8 t + 3 sin(1.2 t): a trolley that surges while moving on


# %% [markdown]
# ## Step 1: a motion with a known exact answer
# For x(t) = 8 t + 3 sin(1.2 t) metres we can differentiate by hand:
#
#     v(t) = 8 + 3.6 cos(1.2 t) m/s        a(t) = -4.32 sin(1.2 t) m/s^2
#
# Simulated measurement: positions every dt seconds plus random noise of standard deviation
# sigma (metres). The same seed gives the same noise, so results can be repeated.

# %%
def true_motion(t):
    t = np.asarray(t, dtype=float)
    x = A_DRIFT * t + A_WAVE * np.sin(W * t)
    v = A_DRIFT + A_WAVE * W * np.cos(W * t)
    a = -A_WAVE * W ** 2 * np.sin(W * t)
    return x, v, a


def sample(dt, sigma, T=20.0, seed=1):
    """Times and noisy positions. Noise is Gaussian, mean 0, standard deviation sigma (m)."""
    t = np.arange(0.0, T + dt / 2, dt)
    rng = np.random.default_rng(seed)
    return t, true_motion(t)[0] + rng.normal(0.0, sigma, size=t.shape)


# %% [markdown]
# ## Step 2: finite differences
# Velocity is the slope between neighbouring samples, and acceleration is the change of slope:
#
#     v[i] ~ (x[i+1] - x[i-1]) / (2 dt)          a[i] ~ (x[i+1] - 2 x[i] + x[i-1]) / dt^2
#
# If each x has random error of size sigma, the velocity error is about sigma / (1.41 dt) and
# the acceleration error about 2.45 sigma / dt^2 (hand calculation in the README). Halving dt
# doubles the first and quadruples the second.

# %%
def central_velocity(x, dt):
    """Centred difference; the first and last entries are NaN (no neighbour on one side)."""
    v = np.full_like(x, np.nan)
    v[1:-1] = (x[2:] - x[:-2]) / (2.0 * dt)
    return v


def second_difference(x, dt):
    a = np.full_like(x, np.nan)
    a[1:-1] = (x[2:] - 2.0 * x[1:-1] + x[:-2]) / dt ** 2
    return a


def rms_error(est, truth):
    """Root-mean-square difference, ignoring NaN entries."""
    d = np.asarray(est) - np.asarray(truth)
    return float(np.sqrt(np.nanmean(d ** 2)))


# %% [markdown]
# ## Step 3: smoothing while differentiating
# Fit a cubic polynomial to the 2h+1 samples around each point (least squares) and read the
# slope or curvature of the fit. Averaging many points cuts the noise; but a wide window flattens
# real wiggles, so there is a best width. The weights depend only on h and dt, so the whole
# fit is one convolution.

# %%
def poly_weights(half, order, deriv, dt):
    """Convolution weights giving the `deriv`-th derivative of a local polynomial fit of the given order."""
    k = np.arange(-half, half + 1) * dt
    V = np.vander(k, order + 1, increasing=True)
    fact = float(np.prod(np.arange(1, deriv + 1))) if deriv else 1.0
    return fact * np.linalg.pinv(V)[deriv]


def smooth_derivative(x, dt, half=8, order=3, deriv=1):
    """Derivative of the local polynomial fit; the first and last `half` entries are NaN."""
    w = poly_weights(half, order, deriv, dt)
    out = np.full_like(x, np.nan)
    out[half:len(x) - half] = np.convolve(x, w[::-1], mode="valid")
    return out


def cumulative_integral(f, dt):
    """Running trapezoid integral of samples f, starting from 0."""
    f = np.asarray(f, dtype=float)
    return np.concatenate([[0.0], np.cumsum(0.5 * (f[1:] + f[:-1]) * dt)])


def mean_error(fn, dt, sigma, seeds=range(10), T=20.0):
    """Average RMS error over several noise seeds. fn(t, x, dt) returns the estimate; truth is index 1 (v) or 2 (a)."""
    errs = []
    for s in seeds:
        t, x = sample(dt, sigma, T, seed=s)
        errs.append(fn(t, x, dt))
    return float(np.mean(errs))


# %% [markdown]
# ## Step 4: the mini-project data
# `phone_dataset` plays the role of a phone recording: a trolley is filmed at 30 frames per second
# and its position is read from each frame (error about 2 cm). It speeds up, cruises and brakes
# exactly like Session 2's trip, so we know the truth. Replace it by your own recording later.

# %%
def phone_dataset(seed=7, fps=30.0, sigma=0.02):
    """Times, noisy positions (m) and the exact velocity of the Session 2 style trip (6 s, 10 s, 4 s)."""
    t = np.arange(0.0, 20.0 + 0.5 / fps, 1.0 / fps)
    v = np.interp(t, [0.0, 6.0, 16.0, 20.0], [0.0, 12.0, 12.0, 0.0])
    x = cumulative_integral(v, 1.0 / fps)
    rng = np.random.default_rng(seed)
    return t, x + rng.normal(0.0, sigma, size=t.shape), v


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    dt, sigma = 0.05, 0.02
    t, x = sample(dt, sigma)
    xt, vt, at = true_motion(t)
    v_c, a_c = central_velocity(x, dt), second_difference(x, dt)
    v_s, a_s = smooth_derivative(x, dt, 8, 3, 1), smooth_derivative(x, dt, 8, 3, 2)
    print(f"dt = {dt} s, sigma = {sigma} m, {len(t)} samples")
    print(f"velocity RMS error: central {rms_error(v_c, vt):.3f} m/s, smoothed {rms_error(v_s, vt):.3f} m/s")
    print(f"acceleration RMS error: second difference {rms_error(a_c, at):.2f} m/s^2, smoothed {rms_error(a_s, at):.2f} m/s^2")
    print(f"predicted noise-only errors: velocity {sigma / (np.sqrt(2) * dt):.3f}, acceleration {sigma * np.sqrt(6) / dt ** 2:.2f}")
    print(f"amplitude of true acceleration: {A_WAVE * W ** 2:.2f} m/s^2")

    fig, ax = plt.subplots(3, 1, figsize=(7, 8), sharex=True)
    ax[0].plot(t, x - A_DRIFT * t, ".", ms=3, color="gray", label="noisy data")
    ax[0].plot(t, xt - A_DRIFT * t, "k-", lw=1, label="truth")
    ax[0].set_ylabel("x - 8t (m)")
    ax[1].plot(t, v_c, color="C3", lw=0.8, label="central difference")
    ax[1].plot(t, v_s, color="C0", lw=1.6, label="local cubic fit, 17 points")
    ax[1].plot(t, vt, "k--", lw=1, label="truth")
    ax[1].set_ylabel("velocity (m/s)")
    ax[2].plot(t, a_c, color="C3", lw=0.6, label="second difference")
    ax[2].plot(t, a_s, color="C0", lw=1.6, label="local cubic fit, 17 points")
    ax[2].plot(t, at, "k--", lw=1, label="truth")
    ax[2].set_ylabel("acceleration (m/s^2)")
    ax[2].set_xlabel("time t (s)")
    ax[2].set_ylim(-30, 30)
    for axis in ax:
        axis.grid(alpha=0.3)
        axis.legend(fontsize=8, loc="upper right")
    ax[0].set_title("A 2 cm position error is invisible here, but differentiating twice magnifies it")
    fig.tight_layout()
    fig.savefig(OUT / "noisy_recovery.png", dpi=120)

    # sensitivity to the sampling step
    dts = np.array([0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.2, 2.0])
    clean = [rms_error(central_velocity(sample(d, 0.0)[1], d), true_motion(sample(d, 0.0)[0])[1]) for d in dts]
    noisy = [mean_error(lambda tt, xx, d: rms_error(central_velocity(xx, d), true_motion(tt)[1]), d, sigma) for d in dts]
    print("dt, noise-free error, noisy error (velocity, central difference):")
    for d, c, n in zip(dts, clean, noisy):
        print(f"  {d:5.2f}  {c:.4f}  {n:.4f}")
    fig2, ax2 = plt.subplots(1, 2, figsize=(9, 4))
    ax2[0].loglog(dts, clean, "o-", label="no noise (truncation)")
    ax2[0].loglog(dts, noisy, "s-", label="noise 2 cm")
    ax2[0].loglog(dts, sigma / (np.sqrt(2) * dts), ":", color="gray", label="noise theory")
    ax2[0].set_xlabel("sampling step dt (s)")
    ax2[0].set_ylabel("velocity RMS error (m/s)")
    ax2[0].set_title("Error against sampling step")
    ax2[0].legend(fontsize=8)
    halves = np.array([2, 3, 4, 6, 8, 12, 16, 24, 32, 48])
    ev = [mean_error(lambda tt, xx, d, h=h: rms_error(smooth_derivative(xx, d, h, 3, 1), true_motion(tt)[1]), dt, sigma) for h in halves]
    ea = [mean_error(lambda tt, xx, d, h=h: rms_error(smooth_derivative(xx, d, h, 3, 2), true_motion(tt)[2]), dt, sigma) for h in halves]
    print("half-window, window length (s), velocity error, acceleration error:")
    for h, a1, a2 in zip(halves, ev, ea):
        print(f"  {h:3d}  {(2 * h + 1) * dt:5.2f}  {a1:.4f}  {a2:.3f}")
    ax2[1].semilogy((2 * halves + 1) * dt, ev, "o-", label="velocity (m/s)")
    ax2[1].semilogy((2 * halves + 1) * dt, ea, "s-", label="acceleration (m/s^2)")
    ax2[1].set_xlabel("window length (s)")
    ax2[1].set_ylabel("RMS error")
    ax2[1].set_title("Smoothing: there is a best window")
    ax2[1].legend(fontsize=8)
    for axis in ax2:
        axis.grid(alpha=0.3, which="both")
    fig2.tight_layout()
    fig2.savefig(OUT / "error_sensitivity.png", dpi=120)

    # integration is the safe direction
    tv = np.arange(0.0, 20.0 + 0.025, 0.05)
    rng = np.random.default_rng(3)
    v_meas = true_motion(tv)[1] + rng.normal(0.0, 0.2, size=tv.shape)
    x_int = cumulative_integral(v_meas, 0.05)
    print(f"integrating velocity with 0.2 m/s noise: final position error {x_int[-1] - true_motion(tv)[0][-1]:+.3f} m")

    # mini-project data
    tp, xp, vp = phone_dataset()
    print(f"phone dataset: {len(tp)} frames, final position {xp[-1]:.2f} m (exact 180 m)")
    print("saved figures in", OUT)

# %% [markdown]
# ## Where this stops
# Fixed windows blur sharp changes (the corners of a trip) and cannot choose their own width.
# The Target at the top of the README uses a more careful method; the roadmap shows the path.
