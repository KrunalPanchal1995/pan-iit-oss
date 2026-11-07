"""Session 2 (Level 2): calibrating a sensor with a line.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: calibrating a sensor with a line
# **A. Real-world problem.** A cheap temperature sensor does not report the true temperature:
# it reports a number that is roughly a straight-line function of it, plus noise. To trust it
# you *calibrate* it: compare its readings with trusted reference temperatures, fit a line,
# and then use the line backwards to turn a new reading into a temperature with an
# uncertainty. This is general education about measurement, not a procedure for a
# safety-critical instrument.
#
# **Plan.** (1) simulate a sensor with known gain, offset and noise, (2) fit the line and its
# standard errors, (3) invert it, (4) separate repeatability from reproducibility, (5) add
# quantisation, (6) bias versus random error, (7) how many repeats do we need?

# %%
import math
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# the made-up sensor: reading = GAIN * true + OFFSET + noise
GAIN = 1.02        # reading per degree C (no unit: degrees of reading per degree of truth)
OFFSET = -0.80     # reading at a true temperature of 0 degrees C (degrees C)
NOISE_SD = 0.30    # random scatter of one reading (degrees C)
REF = np.arange(0.0, 101.0, 10.0)   # 11 reference temperatures, 0 to 100 degrees C


# %% [markdown]
# ## Step 1: simulate the sensor

# %%
def sensor(true, rng, gain=GAIN, offset=OFFSET, sd=NOISE_SD):
    """Reading(s) of the made-up sensor at true temperature(s)."""
    true = np.asarray(true, dtype=float)
    return gain * true + offset + rng.normal(0.0, sd, true.shape)


# %% [markdown]
# ## Step 2: fit the calibration line and its standard errors
# With x = reference temperatures (n points) and y = readings, least squares gives
#
#     slope m = Sxy / Sxx,   intercept c = ybar - m * xbar,
#     residual sd s = sqrt( sum(residual^2) / (n - 2) ),
#     SE(m) = s / sqrt(Sxx),   SE(c) = s * sqrt(1/n + xbar^2 / Sxx),
#
# where Sxx = sum (x - xbar)^2 and Sxy = sum (x - xbar)(y - ybar). `np.polyfit(x, y, 1)`
# gives the same m and c; the standard errors we add ourselves.

# %%
def fit_calibration(x, y):
    """Returns dict with slope, intercept, their standard errors, residual sd s, n, xbar, Sxx."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    xbar, ybar = x.mean(), y.mean()
    sxx = float(np.sum((x - xbar) ** 2))
    sxy = float(np.sum((x - xbar) * (y - ybar)))
    m = sxy / sxx
    c = ybar - m * xbar
    resid = y - (m * x + c)
    s = math.sqrt(float(np.sum(resid ** 2)) / (n - 2))
    return {"slope": m, "intercept": c, "se_slope": s / math.sqrt(sxx),
            "se_intercept": s * math.sqrt(1.0 / n + xbar ** 2 / sxx),
            "s": s, "n": n, "xbar": xbar, "sxx": sxx}


def bootstrap_se(x, y, reps, seed):
    """Residual bootstrap: refit after resampling the residuals. Returns (sd of slopes, sd of intercepts)."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    m, c = np.polyfit(x, y, 1)
    resid = np.asarray(y) - (m * x + c)
    ms, cs = [], []
    for _ in range(reps):
        yb = m * x + c + rng.choice(resid, size=len(x), replace=True)
        mb, cb = np.polyfit(x, yb, 1)
        ms.append(mb)
        cs.append(cb)
    return float(np.std(ms, ddof=1)), float(np.std(cs, ddof=1))


# %% [markdown]
# ## Step 3: invert the line (inverse prediction)
# The sensor shows a reading y0 (the mean of k fresh readings). The best estimate of the
# true temperature is x0 = (y0 - c) / m. Its uncertainty has three parts: the noise of the
# new reading(s), the uncertainty of the line's height, and of its tilt:
#
#     u(x0) = (s / |m|) * sqrt( 1/k + 1/n + (x0 - xbar)^2 / Sxx )

# %%
def invert(fit, y0, k=1):
    """Estimated true temperature and its standard uncertainty for a mean reading y0 of k readings."""
    x0 = (y0 - fit["intercept"]) / fit["slope"]
    u = fit["s"] / abs(fit["slope"]) * math.sqrt(1.0 / k + 1.0 / fit["n"] + (x0 - fit["xbar"]) ** 2 / fit["sxx"])
    return x0, u


# %% [markdown]
# ## Step 4: repeatability versus reproducibility
# *Repeatability*: the scatter when you repeat the measurement at once, same person, same
# day. *Reproducibility*: the scatter when conditions change (another day, another set-up).
# Suppose each day the sensor offset shifts by a random amount with sd DAY_SD. Then
# reproducibility sd = sqrt(repeatability^2 + DAY_SD^2).

# %%
DAY_SD = 0.50   # day-to-day shift of the offset (degrees C)


def day_data(days, per_day, seed, sd=NOISE_SD, day_sd=DAY_SD):
    """Readings of a constant truth: array (days, per_day) = daily shift + noise."""
    rng = np.random.default_rng(seed)
    return rng.normal(0.0, day_sd, (days, 1)) + rng.normal(0.0, sd, (days, per_day))


def repeat_and_reproduce(data):
    """(repeatability sd = pooled within-day sd, reproducibility sd = sd of all readings)."""
    within = float(np.sqrt(np.mean(data.var(axis=1, ddof=1))))
    total = float(data.std(ddof=1))
    return within, total


# %% [markdown]
# ## Step 5: resolution and quantisation
# A digital sensor turns a voltage into one of 2^N numbers (N bits). Over a range from lo to
# hi the step between neighbouring numbers is LSB = (hi - lo) / 2^N ("least significant bit").
# Rounding to the nearest step makes an error between -LSB/2 and +LSB/2, with standard
# deviation LSB / sqrt(12) when the signal moves across many steps.

# %%
def lsb(lo, hi, bits):
    return (hi - lo) / 2 ** bits


def quantise(v, lo, hi, bits):
    """Round values to the centre of their ADC step; values outside lo..hi are clipped."""
    q = lsb(lo, hi, bits)
    code = np.clip(np.floor((np.asarray(v, dtype=float) - lo) / q), 0, 2 ** bits - 1)
    return lo + (code + 0.5) * q


def quantisation_rms(lo, hi, bits, n, seed):
    """Measured rms rounding error for n uniformly random values in the range."""
    rng = np.random.default_rng(seed)
    v = rng.uniform(lo, hi, n)
    return float(np.sqrt(np.mean((quantise(v, lo, hi, bits) - v) ** 2)))


def mean_of_quantised(true, noise_sd, reps, lo, hi, bits, seed):
    """Mean of many quantised readings of a constant truth with Gaussian noise before the ADC."""
    rng = np.random.default_rng(seed)
    return float(np.mean(quantise(true + rng.normal(0.0, noise_sd, reps), lo, hi, bits)))


# %% [markdown]
# ## Step 6: bias versus random error
# Random error shrinks like 1 / sqrt(N) when you average N readings. A bias (a constant
# error such as a wrong offset) does not shrink at all.

# %%
def average_error_stats(bias, sd, N, trials, seed):
    """(mean, sd) of the error of the N-reading average over many trials."""
    rng = np.random.default_rng(seed)
    err = bias + rng.normal(0.0, sd, (trials, N)).mean(axis=1)
    return float(err.mean()), float(err.std(ddof=1))


# %% [markdown]
# ## Step 7: design - how many repeats?
# To get the 95 percent half-width of the mean down to h (degrees C) when one reading has
# known scatter sd, we need 1.96 * sd / sqrt(N) <= h, so N >= (1.96 * sd / h)^2. We round up.

# %%
Z95 = 1.959964   # the two-sided 95 percent point of the standard normal


def repeats_needed(sd, half_width, z=Z95):
    return int(math.ceil((z * sd / half_width) ** 2 - 1e-12))


def coverage(sd, N, half_width):
    """Chance that the mean of N readings lies within +-half_width of the truth (random error only)."""
    zz = half_width * math.sqrt(N) / sd
    return math.erf(zz / math.sqrt(2.0))


# %% [markdown]
# ## Step 8: see it
# Left: the calibration data, the fitted line and the true line. Right: the staircase of a
# 6-bit ADC. Second figure: averaging helps random error, not bias.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(2)
    y = sensor(REF, rng)
    f = fit_calibration(REF, y)
    print("fit: slope %.4f +- %.4f, intercept %.3f +- %.3f, s = %.3f" % (
        f["slope"], f["se_slope"], f["intercept"], f["se_intercept"], f["s"]))
    print("polyfit:", np.polyfit(REF, y, 1).round(4))
    print("bootstrap se:", np.round(bootstrap_se(REF, y, 2000, 5), 4))
    x0, u = invert(f, 40.0, k=1)
    print("reading 40.0 -> true %.2f +- %.2f degrees C" % (x0, u))
    print("repeats needed for 0.1 degrees:", repeats_needed(NOISE_SD, 0.1))
    print("LSB for 0..100 at 8 bits: %.4f, sd %.4f" % (lsb(0, 100, 8), lsb(0, 100, 8) / math.sqrt(12)))

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    ax = axs[0]
    ax.scatter(REF, y, s=18, label="readings")
    xs = np.linspace(0, 100, 50)
    ax.plot(xs, f["slope"] * xs + f["intercept"], label="fitted line")
    ax.plot(xs, GAIN * xs + OFFSET, "--", color="gray", label="true line (we do not know it)")
    ax.set_xlabel("reference temperature (degrees C)")
    ax.set_ylabel("sensor reading (degrees C)")
    ax.set_title("Calibration line")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    ax = axs[1]
    t = np.linspace(20, 30, 400)
    ax.plot(t, t, color="gray", lw=1, label="ideal")
    ax.step(t, quantise(t, 0, 100, 6), where="mid", label="6-bit ADC (LSB %.3f)" % lsb(0, 100, 6))
    ax.set_xlabel("true value (degrees C)")
    ax.set_ylabel("digital reading (degrees C)")
    ax.set_title("Quantisation staircase")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "calibration_and_adc.png", dpi=120)

    Ns = np.array([1, 4, 16, 64, 256])
    sds, means = [], []
    for N in Ns:
        mm, ss = average_error_stats(0.5, NOISE_SD, int(N), 4000, 8)
        means.append(mm)
        sds.append(ss)
        print("N = %3d: mean error %.3f, scatter of the average %.3f (theory %.3f)" % (N, mm, ss, NOISE_SD / math.sqrt(N)))
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.loglog(Ns, sds, "o-", label="random error (scatter of the average)")
    ax2.loglog(Ns, np.abs(means), "s-", label="bias (mean error)")
    ax2.set_xlabel("readings averaged, N")
    ax2.set_ylabel("error (degrees C)")
    ax2.set_title("Averaging beats random error, not bias")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3, which="both")
    fig2.tight_layout()
    fig2.savefig(OUT / "average_vs_bias.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
