"""Session 3 (Level 3): digital filters, validated against the analog theory.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: digital filters, validated against the analog theory
# **A. Real-world problem.** A microcontroller reads a sensor at a fixed sample rate and must
# clean the numbers in software. The one-line digital filter `y += alpha * (x - y)` copies an
# RC circuit. Does it really? How much noise does it remove, what does it cost in delay, when
# does it fail, and what do we do when one pole is not steep enough?
#
# **Plan.** (1) the exponential moving average and alpha, (2) measure its frequency response
# two ways (sine sweep and FFT) and compare with the analog Bode curve, (3) noise removed
# versus delay, (4) a second-order Butterworth biquad, (5) the failure case: aliasing,
# (6) the real-world design: a temperature sensor with 50 Hz pickup.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the exponential moving average (EMA) and alpha
# `y[n] = y[n-1] + alpha * (x[n] - y[n-1])`. We choose alpha from the RC time constant tau and
# the sample time dt. **Discretisation used here: exact (step-invariant).** If the input is
# held constant during each sample, the RC circuit moves exactly the fraction
# `alpha = 1 - exp(-dt / tau)` of the way to the input, so the digital step response equals
# the analog one at every sample. The simpler backward-Euler choice `dt / (tau + dt)` is
# almost the same when dt is small compared with tau.

# %%
def alpha_exact(fc, fs):
    """alpha for cutoff fc (Hz) at sample rate fs (Hz), exact step-invariant discretisation."""
    return 1.0 - np.exp(-2.0 * np.pi * fc / fs)


def alpha_euler(fc, fs):
    """alpha from backward Euler: dt / (tau + dt). An approximation, good when fc << fs."""
    return 1.0 / (1.0 + fs / (2.0 * np.pi * fc))


def ema(x, alpha, y0=0.0):
    """Exponential moving average filter, started at y0."""
    y = np.empty(len(x))
    level = y0
    for i, v in enumerate(x):
        level += alpha * (v - level)
        y[i] = level
    return y


# %% [markdown]
# ## Step 2: frequency response, measured two ways
# Theory for the EMA: `H(z) = alpha / (1 - (1 - alpha) z^-1)`, so at frequency f (with
# `w = 2 pi f / fs`) the gain is `|H| = alpha / |1 - (1 - alpha) exp(-j w)|`. The analog
# gain is `1 / sqrt(1 + (f / f_c)^2)`. We test both with (a) sine sweeps and (b) an FFT of
# the filter's reaction to white noise.

# %%
def analog_gain(f, fc):
    return 1.0 / np.sqrt(1.0 + (np.asarray(f, dtype=float) / fc) ** 2)


def digital_gain(f, alpha, fs):
    """Theoretical gain of the EMA at frequency f (Hz) for sample rate fs (Hz)."""
    z1 = np.exp(-2j * np.pi * np.asarray(f, dtype=float) / fs)
    return np.abs(alpha / (1.0 - (1.0 - alpha) * z1))


def fit_amplitude(y, t, f):
    """Amplitude of the sine of frequency f inside y (least-squares fit of a sine and a cosine)."""
    m = np.column_stack([np.sin(2 * np.pi * f * t), np.cos(2 * np.pi * f * t)])
    coef, *_ = np.linalg.lstsq(m, y, rcond=None)
    return float(np.hypot(coef[0], coef[1]))


def sweep_gain(f, alpha, fs):
    """Measured gain: feed a unit sine of frequency f, wait for start-up to fade, fit the output."""
    settle = int(14.0 / alpha)                      # (1 - alpha)^n is about e^-14 after this many samples
    n = settle + int(6 * fs / f) + 200
    t = np.arange(n) / fs
    y = ema(np.sin(2 * np.pi * f * t), alpha)
    return fit_amplitude(y[settle:], t[settle:], f)


def fft_gain(alpha, fs, nfft=512, segments=600, seed=1):
    """Measured gain from white noise: |cross-spectrum| / input spectrum, averaged over segments.
    Returns (frequencies in Hz, gain)."""
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(nfft * segments)
    y = ema(x, alpha)
    w = np.hanning(nfft)
    sxy = np.zeros(nfft // 2 + 1, dtype=complex)
    sxx = np.zeros(nfft // 2 + 1)
    for k in range(segments):
        X = np.fft.rfft(w * x[k * nfft:(k + 1) * nfft])
        Y = np.fft.rfft(w * y[k * nfft:(k + 1) * nfft])
        sxy += Y * np.conj(X)
        sxx += np.abs(X) ** 2
    return np.fft.rfftfreq(nfft, 1.0 / fs), np.abs(sxy) / sxx


# %% [markdown]
# ## Step 3: noise removed versus delay
# For white noise of variance sigma^2, the EMA output variance is
# `sigma_out^2 = sigma^2 * alpha / (2 - alpha)`. Reason: the impulse response is
# `h[k] = alpha (1 - alpha)^k` and the output variance is `sigma^2` times the sum of `h[k]^2`,
# which is `alpha^2 / (1 - (1 - alpha)^2) = alpha / (2 - alpha)`. The price is delay: a slow
# signal arrives late by `(1 - alpha) / alpha` samples (the average of the impulse response
# in time), and a step needs a number of samples to reach 90 percent.

# %%
def variance_ratio_theory(alpha):
    return alpha / (2.0 - alpha)


def variance_ratio_measured(alpha, n=400_000, seed=3):
    rng = np.random.default_rng(seed)
    y = ema(rng.standard_normal(n), alpha)[2000:]
    return float(np.var(y))


def lag_samples(alpha):
    """Delay of a slow signal in samples: (1 - alpha) / alpha."""
    return (1.0 - alpha) / alpha


def samples_to_90(alpha):
    """Smallest number of samples after which a unit step reaches 0.9 of its final value."""
    n = 0
    level = 0.0
    while level < 0.9:
        level += alpha * (1.0 - level)
        n += 1
    return n


# %% [markdown]
# ## Step 4: a second-order Butterworth filter
# One pole falls only 20 dB per decade. A second-order low-pass falls 40 dB per decade. The
# Butterworth choice (quality factor Q = 1/sqrt(2)) has the flattest passband. Standard
# **biquad coefficients** (the widely used audio-EQ cookbook low-pass, a bilinear transform
# with the cutoff pre-warped so that the -3 dB point lands exactly on fc):
#
#     w0 = 2 pi fc / fs,  c = cos(w0),  a = sin(w0) / (2 Q),  Q = 1/sqrt(2)
#     b0 = b2 = (1 - c) / 2,  b1 = 1 - c,
#     a0 = 1 + a,  a1 = -2 c,  a2 = 1 - a      (all divided by a0)
#     y[n] = b0 x[n] + b1 x[n-1] + b2 x[n-2] - a1 y[n-1] - a2 y[n-2]
#
# A cheaper way is to cascade two buffered RC stages; that gives -6 dB at the stage cutoff
# (gain 1/2), so each stage must be set to fc / sqrt(sqrt(2) - 1) for -3 dB at fc, and the
# knee is softer than Butterworth.

# %%
def butter2_coeffs(fc, fs):
    """(b, a) of the 2nd-order Butterworth low-pass biquad, with a[0] = 1."""
    w0 = 2.0 * np.pi * fc / fs
    c = np.cos(w0)
    al = np.sin(w0) / (2.0 * (1.0 / np.sqrt(2.0)))
    a0 = 1.0 + al
    b = np.array([(1.0 - c) / 2.0, 1.0 - c, (1.0 - c) / 2.0]) / a0
    a = np.array([1.0, -2.0 * c / a0, (1.0 - al) / a0])
    return b, a


def biquad(x, b, a, init=0.0):
    """Direct form I biquad. init is the value the input and output had before the first sample."""
    y = np.empty(len(x))
    x1 = x2 = y1 = y2 = init
    for i, v in enumerate(x):
        out = b[0] * v + b[1] * x1 + b[2] * x2 - a[1] * y1 - a[2] * y2
        x2, x1 = x1, v
        y2, y1 = y1, out
        y[i] = out
    return y


def biquad_gain(f, b, a, fs):
    z1 = np.exp(-2j * np.pi * np.asarray(f, dtype=float) / fs)
    return np.abs((b[0] + b[1] * z1 + b[2] * z1 ** 2) / (1.0 + a[1] * z1 + a[2] * z1 ** 2))


def cascade_stage_fc(fc, stages=2):
    """Cutoff of each of `stages` identical buffered RC stages so that the cascade is -3 dB at fc."""
    return fc / np.sqrt(2.0 ** (1.0 / stages) - 1.0)


# %% [markdown]
# ## Step 5: the failure case, aliasing and a cutoff above Nyquist
# A sampler cannot see frequencies above half the sample rate (the Nyquist frequency fs/2).
# A 50 Hz hum sampled at 55 Hz looks like 5 Hz, and a digital filter cannot tell it from a
# real 5 Hz signal. Also, an EMA whose analog cutoff is above fs/2 has no -3 dB point left.

# %%
def alias_frequency(f, fs):
    """Apparent frequency (Hz) of a sine of frequency f after sampling at fs."""
    return float(abs(f - fs * np.round(f / fs)))


def ema_minus3db_hz(alpha, fs):
    """Frequency (Hz) where the EMA gain is 1/sqrt(2), or None if it never falls that far
    below Nyquist. Solves |H|^2 = 1/2 for cos(w)."""
    b = 1.0 - alpha
    if b <= 0.0:
        return None
    cw = (1.0 + b * b - 2.0 * alpha * alpha) / (2.0 * b)
    if cw < -1.0 or cw > 1.0:
        return None
    return float(np.arccos(cw) * fs / (2.0 * np.pi))


# %% [markdown]
# ## Step 6: the real-world design, a temperature sensor with 50 Hz pickup
# The temperature is 25.0 C and steps to 30.0 C at t = 1 s. The wire adds 0.5 C of 50 Hz hum
# and the electronics add white noise of 0.05 C (standard deviation), sampled at 500 Hz.
# Requirements: hum left at the output at most 0.02 C, random noise left at most 0.008 C
# (standard deviation), and the reading must reach 90 percent of the step within 0.5 s.

# %%
FS_T = 500.0


def temperature_trace(seconds=6.0, hum=0.5, noise=0.05, seed=5, fs=FS_T):
    t = np.arange(int(seconds * fs)) / fs
    true = np.where(t < 1.0, 25.0, 30.0)
    rng = np.random.default_rng(seed)
    return t, true, true + hum * np.sin(2 * np.pi * 50.0 * t) + noise * rng.standard_normal(len(t))


def ripple_after(filter_fn, hum=0.5, fs=FS_T):
    """Amplitude (C) of the 50 Hz hum left at the output of filter_fn (noise-free input)."""
    t, _, _ = temperature_trace(seconds=8.0, noise=0.0, hum=hum, fs=fs)
    clean = 25.0 + hum * np.sin(2 * np.pi * 50.0 * t)
    y = filter_fn(clean)
    return fit_amplitude(y[len(t) // 2:], t[len(t) // 2:], 50.0)


def time_to_90(filter_fn, fs=FS_T):
    """Seconds after the step until the filtered noise-free reading reaches 25 + 0.9 * 5 = 29.5 C."""
    t, true, _ = temperature_trace(noise=0.0, hum=0.0, fs=fs)
    y = filter_fn(true)
    if not np.any(y >= 29.5):
        return float("inf")             # too slow: never gets there within the 6 s trace
    return float(t[int(np.argmax(y >= 29.5))] - 1.0)


def noise_rms_after(filter_fn, noise=0.05, n=100_000, seed=9):
    """Standard deviation (C) of the random noise left at the output (hum-free, steady input)."""
    x = noise * np.random.default_rng(seed).standard_normal(n)
    return float(np.std(filter_fn(x)[2000:]))


def passes(filter_fn, ripple_max=0.02, t90_max=0.5, noise_max=0.008):
    """True if the filter meets all three requirements of the temperature design."""
    return (ripple_after(filter_fn) <= ripple_max and time_to_90(filter_fn) <= t90_max
            and noise_rms_after(filter_fn) <= noise_max)


def ema_filter(fc, fs=FS_T):
    a = alpha_exact(fc, fs)
    return lambda x: ema(x, a, y0=x[0])


def butter_filter(fc, fs=FS_T):
    b, a = butter2_coeffs(fc, fs)
    return lambda x: biquad(x, b, a, init=x[0])


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    fs, fc = 1000.0, 20.0
    a = alpha_exact(fc, fs)
    print(f"fs = {fs:.0f} Hz, fc = {fc:.0f} Hz: alpha exact {a:.5f}, backward Euler {alpha_euler(fc, fs):.5f}")

    # sweep and FFT against theory
    fsw = np.array([2.0, 5.0, 10.0, 20.0, 40.0, 80.0, 160.0, 320.0])
    meas = np.array([sweep_gain(f, a, fs) for f in fsw])
    ff, gf = fft_gain(a, fs)
    print("f (Hz)   analog   digital  sweep")
    for f, m in zip(fsw, meas):
        print(f"{f:6.0f}  {float(analog_gain(f, fc)):.4f}  {float(digital_gain(f, a, fs)):.4f}  {m:.4f}")
    fig, ax = plt.subplots(figsize=(7, 4))
    fl = np.logspace(0, np.log10(499), 300)
    ax.semilogx(fl, 20 * np.log10(analog_gain(fl, fc)), "k--", label="analog RC")
    ax.semilogx(fl, 20 * np.log10(digital_gain(fl, a, fs)), color="C0", label="digital EMA (theory)")
    ax.semilogx(ff[1:], 20 * np.log10(gf[1:]), color="C2", lw=0.8, alpha=0.8, label="FFT of noise response")
    ax.semilogx(fsw, 20 * np.log10(meas), "ro", label="sine sweep")
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("gain (dB)")
    ax.set_ylim(-45, 3)
    ax.set_title("fs = 1000 Hz, fc = 20 Hz: the EMA follows the analog Bode curve until near Nyquist")
    ax.title.set_fontsize(9)
    ax.grid(alpha=0.3, which="both")
    ax.legend(loc="lower left", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "bode_compare.png", dpi=120)

    # noise versus lag
    alphas = np.array([0.5, 0.2, 0.1, 0.05, 0.02, 0.01])
    print("alpha  var_theory var_measured lag(samples) n90")
    for al in alphas:
        print(f"{al:5.2f}  {variance_ratio_theory(al):.4f}     {variance_ratio_measured(al):.4f}       "
              f"{lag_samples(al):6.1f}      {samples_to_90(al)}")
    al_grid = np.linspace(0.01, 0.9, 90)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    ax2.plot(lag_samples(al_grid), 10 * np.log10(variance_ratio_theory(al_grid)), color="C0", lw=2, label="theory")
    ax2.plot(lag_samples(alphas), [10 * np.log10(variance_ratio_measured(al)) for al in alphas], "ro", label="measured")
    ax2.set_xlabel("lag of a slow signal (samples)")
    ax2.set_ylabel("white-noise power at the output (dB relative to input)")
    ax2.set_title("Less noise costs more delay: no free lunch")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "noise_vs_lag.png", dpi=120)

    # butterworth
    bb, ab = butter2_coeffs(fc, fs)
    f1 = np.logspace(0, np.log10(499), 300)
    st = cascade_stage_fc(fc)
    casc = digital_gain(f1, alpha_exact(st, fs), fs) ** 2
    print(f"Butterworth gain at fc: {float(biquad_gain(fc, bb, ab, fs)):.4f} (1/sqrt 2 = {2 ** -0.5:.4f}); "
          f"at 10 fc: {20 * np.log10(float(biquad_gain(10 * fc, bb, ab, fs))):.1f} dB")
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    ax3.semilogx(f1, 20 * np.log10(digital_gain(f1, a, fs)), color="C0", label="1st order (EMA)")
    ax3.semilogx(f1, 20 * np.log10(casc), color="C1", label="two cascaded RC stages")
    ax3.semilogx(f1, 20 * np.log10(biquad_gain(f1, bb, ab, fs)), color="C3", lw=2, label="2nd-order Butterworth biquad")
    ax3.axvline(fc, color="0.6", ls="--", lw=1)
    ax3.axhline(-3.01, color="0.6", ls="--", lw=1)
    ax3.set_ylim(-60, 3)
    ax3.set_xlabel("frequency (Hz)")
    ax3.set_ylabel("gain (dB)")
    ax3.set_title("All three are -3 dB at fc = 20 Hz; the Butterworth falls 40 dB per decade")
    ax3.title.set_fontsize(9)
    ax3.grid(alpha=0.3, which="both")
    ax3.legend(loc="lower left", fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "butterworth.png", dpi=120)

    # aliasing
    fs_bad = 55.0
    t = np.arange(0, 1.0, 1 / fs_bad)
    tt = np.linspace(0, 1.0, 2000)
    fig4, ax4 = plt.subplots(figsize=(7, 3.6))
    ax4.plot(tt, np.sin(2 * np.pi * 50 * tt), color="0.8", lw=0.8, label="real 50 Hz hum")
    ax4.plot(t, np.sin(2 * np.pi * 50 * t), "o", color="C3", ms=3, label="samples at 55 Hz")
    ax4.plot(tt, -np.sin(2 * np.pi * alias_frequency(50, fs_bad) * tt), color="C0", lw=1.5,
             label="what the samples look like: 5 Hz")
    ax4.set_xlim(0, 0.6)
    ax4.set_xlabel("time (s)")
    ax4.set_ylabel("hum (relative units)")
    ax4.set_title("Failure case: 50 Hz hum sampled at 55 Hz masquerades as 5 Hz")
    ax4.grid(alpha=0.3)
    ax4.legend(loc="lower right", fontsize=8)
    fig4.tight_layout()
    fig4.savefig(OUT / "aliasing.png", dpi=120)
    print(f"alias of 50 Hz at 55 Hz sampling: {alias_frequency(50, 55):.1f} Hz; "
          f"EMA (fc = 2 Hz at fs = 55) gain there: {float(digital_gain(5.0, alpha_exact(2.0, 55.0), 55.0)):.3f}, "
          f"analog gain at 50 Hz: {float(analog_gain(50.0, 2.0)):.3f}")
    print(f"fc = 40 Hz at fs = 60 Hz: alpha = {alpha_exact(40.0, 60.0):.3f}, -3 dB point: "
          f"{ema_minus3db_hz(alpha_exact(40.0, 60.0), 60.0)}")

    # temperature design
    scan = np.arange(0.25, 14.01, 0.25)
    for name, mk in (("EMA", ema_filter), ("Butterworth", butter_filter)):
        ok = [f for f in scan if passes(mk(f))]
        print(f"{name}: passing cutoffs {ok[0]:.2f} to {ok[-1]:.2f} Hz ({len(ok)} of {len(scan)} tested), "
              f"fastest t90 {min(time_to_90(mk(f)) for f in ok):.3f} s")
    print("fc (Hz)   EMA ripple  EMA t90   | Butterworth ripple  t90")
    for f in (1.0, 2.0, 4.0, 8.0):
        e, bt = ema_filter(f), butter_filter(f)
        print(f"{f:5.1f}    {ripple_after(e):.4f} C   {time_to_90(e):.3f} s |   {ripple_after(bt):.4f} C     {time_to_90(bt):.3f} s")
    t6, true6, meas6 = temperature_trace()
    fig5, ax5 = plt.subplots(figsize=(7, 3.8))
    ax5.plot(t6, meas6, color="0.75", lw=0.8, label="raw reading (hum + noise)")
    ax5.plot(t6, ema_filter(1.5)(meas6), color="C0", lw=2, label="EMA, fc = 1.5 Hz")
    ax5.plot(t6, true6, "k:", lw=1, label="true temperature")
    ax5.set_xlim(0.5, 3.5)
    ax5.set_xlabel("time (s)")
    ax5.set_ylabel("temperature (C)")
    ax5.set_title("Temperature sensor: step from 25 C to 30 C at t = 1 s, 50 Hz pickup")
    ax5.grid(alpha=0.3)
    ax5.legend(loc="lower right", fontsize=8)
    fig5.tight_layout()
    fig5.savefig(OUT / "temperature.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), run the
# checkpoint, then start the mini-project.
