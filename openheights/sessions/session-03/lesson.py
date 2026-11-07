"""Session 3 (Level 3): simulate noisy phone readings, correct for a hill, average, and compare methods.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulate the measurement and test the formulas
# **A. Real-world problem.** A phone clinometer never gives the same angle twice. Is the error
# formula from Session 2 right? Does averaging many readings help, and by how much? Is the
# two-angle method better than the one-angle method? What if the ground slopes, or the tower
# is so close that you look almost straight up?
#
# **Plan.** (1) simulate noisy readings from exact geometry, (2) average them and compute the
# standard error, (3) compare one-angle and two-angle methods by Monte Carlo against the error
# formulas, (4) correct for a slope, (5) find where it all breaks.

# %%
import pathlib
import math

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
EYE = 1.6


# %% [markdown]
# ## Step 1: exact geometry and noisy readings
# The true angle comes from exact trigonometry; the phone adds a random error with standard
# deviation `sigma` (degrees). A reading of 90 degrees or more is not a valid elevation.

# %%
def true_angle(d, h_above_eye):
    """Exact angle of elevation (degrees) to a point h_above_eye (m) above the eye, d (m) away."""
    return math.degrees(math.atan2(h_above_eye, d))


def noisy_readings(true_deg, sigma_deg, n, rng):
    """n phone readings: true angle plus a Gaussian error (degrees)."""
    return true_deg + rng.normal(0.0, sigma_deg, n)


def h_one(d, angle_deg, eye=EYE):
    """One-angle estimate, works on arrays of readings. Angles must be below 90 degrees."""
    a = np.asarray(angle_deg, dtype=float)
    if np.any(a <= 0) or np.any(a >= 90):
        raise ValueError("a reading outside 0 to 90 degrees is not a valid elevation")
    return d * np.tan(np.radians(a)) + eye


def h_two(b, a1_deg, a2_deg, eye=EYE):
    """Two-angle estimate (far reading a1, near reading a2, walk b). Works on arrays."""
    a1 = np.radians(np.asarray(a1_deg, dtype=float))
    a2 = np.radians(np.asarray(a2_deg, dtype=float))
    return b / (1.0 / np.tan(a1) - 1.0 / np.tan(a2)) + eye


# %% [markdown]
# ## Step 2: many readings, the mean and the standard error
# The standard deviation `s` of the readings tells how noisy ONE reading is. The mean of `n`
# readings is better: its uncertainty (standard error) is  s / sqrt(n).  Averaging cannot remove
# a systematic error, such as a tilted phone or a wrong tape distance.

# %%
def mean_and_sem(values):
    v = np.asarray(values, dtype=float)
    if v.size < 2:
        raise ValueError("need at least two values for a standard error")
    return float(v.mean()), float(v.std(ddof=1) / math.sqrt(v.size))


# %% [markdown]
# ## Step 3: error formulas, and the Monte Carlo test
# One angle (Session 2):  sigma_h = d sec^2(a) sigma.
# Two angles: with c = cot(a1) - cot(a2), the partial derivatives are
# dh/da1 = b csc^2(a1) / c^2   and   dh/da2 = -b csc^2(a2) / c^2, so
#
#     sigma_h = sigma * sqrt((b csc^2(a1))^2 + (b csc^2(a2))^2) / c^2
#
# (independent reading errors, b known exactly). A Monte Carlo run repeats the whole
# measurement many times and takes the standard deviation of the results.

# %%
def sigma_one(d, angle_deg, sigma_deg):
    return d / math.cos(math.radians(angle_deg)) ** 2 * math.radians(sigma_deg)


def sigma_two(b, a1_deg, a2_deg, sigma_deg):
    a1, a2 = math.radians(a1_deg), math.radians(a2_deg)
    c = 1.0 / math.tan(a1) - 1.0 / math.tan(a2)
    g1 = b / math.sin(a1) ** 2 / c ** 2
    g2 = b / math.sin(a2) ** 2 / c ** 2
    return math.radians(sigma_deg) * math.hypot(g1, g2)


def monte_carlo(d, h_above_eye, sigma_deg, trials=20000, b=None, seed=1):
    """Return (one-angle estimates, two-angle estimates) over many repeated measurements.

    One angle: read at distance d. Two angles: far reading at d, near reading at d - b (the walk
    is b metres towards the tower)."""
    rng = np.random.default_rng(seed)
    one = h_one(d, noisy_readings(true_angle(d, h_above_eye), sigma_deg, trials, rng))
    if b is None:
        return one, None
    a1 = noisy_readings(true_angle(d, h_above_eye), sigma_deg, trials, rng)
    a2 = noisy_readings(true_angle(d - b, h_above_eye), sigma_deg, trials, rng)
    return one, h_two(b, a1, a2)


# %% [markdown]
# ## Step 4: a sloping ground
# If the ground rises towards the tower at slope angle `phi`, a tape along the ground gives the
# slope distance `s`; the horizontal distance is D = s cos(phi). The base is D tan(phi) above
# your feet, so the tower top is higher above your eye than the base is by only
#     h = D (tan(a) - tan(phi)) + eye
# (measured from the base up; phi is negative when the ground falls towards the tower).

# %%
def h_on_slope(s, phi_deg, angle_deg, eye=EYE):
    """Tower height above its own base (m), from slope distance s, ground slope phi and the top angle."""
    D = s * math.cos(math.radians(phi_deg))
    return D * (math.tan(math.radians(angle_deg)) - math.tan(math.radians(phi_deg))) + eye


def h_ignoring_slope(s, angle_deg, eye=EYE):
    """The naive answer: treat the slope distance as flat ground."""
    return s * math.tan(math.radians(angle_deg)) + eye


# %% [markdown]
# ## Step 5: the failure case, and the mini-project data
# Close to a tall tower the angle approaches 90 degrees and sec^2 explodes; a reading of 90 or
# more is even impossible. The flagpole data below are synthetic phone readings (degrees).

# %%
FLAG_D = 18.0          # m, horizontal distance from the tape
FLAG_EYE = 1.55        # m
FLAG_TAPE_ERROR = 0.1  # m, estimated tape error
FLAG_READINGS = [23.6, 23.7, 23.4, 23.1, 23.3, 23.1, 23.6, 24.2, 23.3, 23.3, 23.8, 23.7]


def flagpole_report(readings=FLAG_READINGS, d=FLAG_D, eye=FLAG_EYE, tape_error=FLAG_TAPE_ERROR):
    """Mean height, standard error, and a combined uncertainty (reading scatter plus tape error)."""
    heights = h_one(d, readings, eye)
    mean, sem = mean_and_sem(heights)
    mean_angle = float(np.mean(readings))
    tape = math.tan(math.radians(mean_angle)) * tape_error
    return mean, sem, math.hypot(sem, tape)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    H, sig = 28.4, 0.5
    d1, b = 40.0, 10.0
    one, two = monte_carlo(d1, H, sig, b=b)
    print(f"d = {d1} m: one-angle  MC std {one.std():.3f} m   formula {sigma_one(d1, true_angle(d1, H), sig):.3f} m   mean {one.mean():.3f}")
    a1, a2 = true_angle(d1, H), true_angle(d1 - b, H)
    print(f"two-angle (far {d1} m, walk {b} m): MC std {two.std():.3f} m   formula {sigma_two(b, a1, a2, sig):.3f} m   mean {two.mean():.3f}")

    # averaging n readings
    rng = np.random.default_rng(3)
    ns = [1, 2, 5, 10, 25, 50, 100]
    sems = []
    for n in ns:
        est = np.array([h_one(28.4, noisy_readings(45.0, sig, n, rng)).mean() for _ in range(3000)])
        sems.append(est.std())
    print("n:", ns)
    print("std of the mean:", np.round(sems, 3), " formula sigma_h/sqrt(n):", np.round([0.496 / math.sqrt(n) for n in ns], 3))

    # coverage of the +/- 2 SEM interval
    rng = np.random.default_rng(5)
    hit = 0
    for _ in range(3000):
        m, s = mean_and_sem(h_one(28.4, noisy_readings(45.0, sig, 30, rng)))
        hit += abs(m - (28.4 + EYE)) < 2 * s
    print("fraction of +/- 2 SEM intervals that contain the truth:", hit / 3000)

    # slope
    s_, phi = 30 / math.cos(math.radians(10)), 10.0
    top = math.degrees(math.atan((30 + 30 * math.tan(math.radians(phi)) - EYE) / 30))
    print(f"slope 10 deg: top angle {top:.2f}, naive {h_ignoring_slope(s_, top):.2f} m, corrected {h_on_slope(s_, phi, top):.2f} m (true 30)")

    # failure near 90 degrees
    print("close to the tower (true height above eye 28.4 m, sigma 0.5 deg):")
    ds = np.array([2, 5, 10, 20, 28.4, 40])
    for d in ds:
        a = true_angle(d, H)
        o = monte_carlo(d, H, sig, trials=20000)[0]
        print(f"  d = {d:5.1f} m  angle {a:5.1f} deg  formula {sigma_one(d, a, sig):6.2f} m  MC std {o.std():.2f} m  MC mean {o.mean():.2f} m (true {H + EYE:.1f})")

    print("two-angle method, far reading at 40 m, longer walk b:")
    for bb in (10, 20, 30):
        t = monte_carlo(40.0, H, sig, b=bb)[1]
        print(f"  b = {bb} m: MC std {t.std():.2f} m   formula {sigma_two(bb, true_angle(40.0, H), true_angle(40.0 - bb, H), sig):.2f} m")

    mean, sem, comb = flagpole_report()
    print(f"flagpole: {mean:.2f} m, standard error {sem:.3f} m, combined {comb:.3f} m")

    # figures
    dd = np.linspace(2, 100, 300)
    aa = np.degrees(np.arctan(H / dd))
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(dd, [sigma_one(x, y, sig) for x, y in zip(dd, aa)], label="one angle: formula")
    mc_d = [5, 10, 20, 30, 40, 60, 80, 100]
    ax.plot(mc_d, [monte_carlo(x, H, sig, trials=20000)[0].std() for x in mc_d], "o", label="one angle: Monte Carlo")
    two_s = [sigma_two(10, true_angle(x, H), true_angle(x - 10, H), sig) for x in dd[dd > 11]]
    ax.plot(dd[dd > 11], two_s, "--", label="two angles (walk 10 m): formula")
    ax.set_ylim(0, 6)
    ax.set_xlabel("distance of the far reading from the base (m)")
    ax.set_ylabel("standard deviation of the height (m)")
    ax.set_title("Simulation agrees with the error formula (sigma = 0.5 degrees)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "monte_carlo_error.png", dpi=120)

    fig2, axs = plt.subplots(1, 2, figsize=(9, 4))
    axs[0].loglog(ns, sems, "o", label="simulated std of the mean")
    axs[0].loglog(ns, [0.496 / math.sqrt(n) for n in ns], "-", label="sigma_h / sqrt(n)")
    axs[0].set_xlabel("number of readings n")
    axs[0].set_ylabel("uncertainty of the mean height (m)")
    axs[0].set_title("Averaging helps like 1/sqrt(n)")
    axs[0].legend(fontsize=8)
    axs[0].grid(alpha=0.3, which="both")
    dfar = np.linspace(0.5, 40, 300)
    axs[1].plot(dfar, [sigma_one(x, true_angle(x, H), sig) for x in dfar])
    axs[1].set_ylim(0, 10)
    axs[1].set_xlabel("distance from the base (m)")
    axs[1].set_ylabel("height error, one reading (m)")
    axs[1].set_title("Failure: close to the tower the error blows up")
    axs[1].grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "averaging_and_failure.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The simulation uses independent Gaussian errors, a straight vertical tower and a perfectly
# level phone. Real errors include hand tremor, a tilted phone and a leaning tree.
