"""Session 2 (Level 2): flicker frequency from a height signal, sampling, and the flame correlations.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: how fast does the flame flicker?
# **A. Real-world problem.** A flame does not just have a height, it breathes: it grows and
# shrinks several times a second. A phone camera takes a snapshot every 1/30 s. Can 30 snapshots
# per second tell you a flicker frequency, and how fast a flicker can the camera see at all?
#
# **Plan.** (1) a flicker is a height signal h(t), (2) count its cycles, (3) find its frequency
# with the Fourier transform (FFT), (4) learn the two limits of sampling (resolution and Nyquist),
# (5) compare with two published correlations for flame height and for flicker frequency.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the height signal
# We model the flame height as a steady mean plus a sinusoidal flicker:
#
#     h(t) = h0 + A sin(2 pi f t)        f in hertz (cycles per second), t in seconds
#
# A camera sees it only at the frame times t = k / fs, with fs the frame rate (frames per second).

# %%
def height_signal(duration, fs, h0, amp, f, phase=0.0):
    """Samples of h(t) taken fs times per second for `duration` seconds. Returns (t, h)."""
    n = int(round(duration * fs))
    t = np.arange(n) / fs
    return t, h0 + amp * np.sin(2 * np.pi * f * t + phase)


# %% [markdown]
# ## Step 2: count the cycles
# Subtract the mean. Each time the signal crosses zero going upward, one cycle starts. The
# frequency is (number of full cycles) / (time they took). We find each crossing time by
# straight-line interpolation between the two samples around it.

# %%
def count_frequency(h, fs):
    """Frequency (Hz) from upward zero crossings of the mean-removed signal."""
    x = np.asarray(h, dtype=float) - np.mean(h)
    idx = np.where((x[:-1] < 0) & (x[1:] >= 0))[0]
    if len(idx) < 2:
        return 0.0
    t_cross = (idx + (-x[idx]) / (x[idx + 1] - x[idx])) / fs
    return float((len(idx) - 1) / (t_cross[-1] - t_cross[0]))


# %% [markdown]
# ## Step 3: the Fourier transform (FFT)
# The FFT splits a signal into sinusoids of different frequencies and tells how big each one is.
# A flicker shows up as one tall peak. We multiply by a Hann window (a smooth bump) first so the
# ends of the recording do not leak into other frequencies, and we scale the result so the peak
# height equals the flicker amplitude A. `pad` zero-pads the signal to draw the spectrum on a
# finer frequency grid (it does not add information).

# %%
def spectrum(h, fs, pad=1):
    """Amplitude spectrum of the mean-removed, Hann-windowed signal. Returns (freqs_hz, amplitude)."""
    x = np.asarray(h, dtype=float) - np.mean(h)
    n = len(x)
    w = np.hanning(n)
    nfft = n * pad
    amp = np.abs(np.fft.rfft(x * w, nfft)) * 2.0 / w.sum()
    return np.fft.rfftfreq(nfft, d=1.0 / fs), amp


def peak_frequency(freqs, amp):
    """Frequency of the tallest peak, refined by a parabola through the peak and its two neighbours."""
    k = int(np.argmax(amp[1:-1])) + 1
    a, b, c = amp[k - 1], amp[k], amp[k + 1]
    denom = a - 2 * b + c
    shift = 0.0 if denom == 0 else 0.5 * (a - c) / denom
    return float(freqs[k] + shift * (freqs[1] - freqs[0]))


def fft_frequency(h, fs, pad=8):
    f, a = spectrum(h, fs, pad)
    return peak_frequency(f, a)


# %% [markdown]
# ## Step 4: the two limits of sampling
# * **Resolution.** A recording of T seconds cannot separate two frequencies closer than 1 / T hertz.
# * **Nyquist limit.** At frame rate fs the highest frequency you can see correctly is fs / 2. A faster
#   flicker is *aliased*: it appears at the wrong, lower frequency |f - m fs| where m is the whole
#   number nearest to f / fs. (Like a wagon wheel that seems to turn backwards in a film.)

# %%
def nyquist(fs):
    return fs / 2.0


def resolution(duration):
    return 1.0 / duration


def alias_frequency(f, fs):
    """Frequency the camera appears to see for a true flicker f at frame rate fs."""
    return float(abs(f - fs * np.round(f / fs)))


# %% [markdown]
# ## Step 5: two published correlations
# **Flame height (Heskestad).** For a turbulent buoyant diffusion flame (a pool fire or gas burner)
# the mean flame height H, defined as the height reached half of the time, is
#
#     H = 0.235 Q^(2/5) - 1.02 D       H in m, Q = heat release rate in kW, D = burner diameter in m
#
# **Flicker (puffing) frequency.** Pool fires puff at about  f = 1.5 / sqrt(D)  hertz  (D in m).
#
# Both are *fits to experiments*, not laws: they describe fires from roughly 0.1 m across upwards
# (see README for the range) and are poor for small laminar flames such as a candle.

# %%
def heskestad_height(q_kw, d_m):
    """Mean flame height (m). Returns 0 when the correlation gives no flame (negative value)."""
    return float(max(0.0, 0.235 * q_kw ** 0.4 - 1.02 * d_m))


def heat_release_for_height(h_m, d_m):
    """Inverse of the Heskestad correlation: the Q (kW) that gives flame height h_m."""
    return float(((h_m + 1.02 * d_m) / 0.235) ** 2.5)


def flicker_frequency(d_m):
    return 1.5 / np.sqrt(d_m)


# %% [markdown]
# ## Step 6: see it
# Left: a sampled flicker and its spectrum. Right: the aliasing map, the apparent frequency
# against the true frequency for three frame rates.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    q, d = 50.0, 0.30
    H, f_true = heskestad_height(q, d), flicker_frequency(d)
    print(f"Q = {q:.0f} kW, D = {d} m -> H = {H:.3f} m, f = {f_true:.3f} Hz")
    t, h = height_signal(10.0, 30.0, H, 0.05 * H, f_true)
    print(f"cycle counting: {count_frequency(h, 30.0):.3f} Hz; FFT: {fft_frequency(h, 30.0):.3f} Hz; "
          f"resolution {resolution(10.0):.2f} Hz; Nyquist {nyquist(30.0):.1f} Hz")

    fig, ax = plt.subplots(1, 2, figsize=(9, 3.8))
    ax[0].plot(t[:90], h[:90] * 1000, "o-", ms=3)
    ax[0].set_xlabel("time (s)")
    ax[0].set_ylabel("flame height (mm)")
    ax[0].set_title("Sampled flicker, 30 frames per second")
    ax[0].grid(alpha=0.3)
    fr, am = spectrum(h, 30.0, pad=8)
    ax[1].plot(fr, am * 1000)
    ax[1].axvline(f_true, color="tab:red", ls=":", label=f"true {f_true:.2f} Hz")
    ax[1].set_xlim(0, 15)
    ax[1].set_xlabel("frequency (Hz)")
    ax[1].set_ylabel("amplitude (mm)")
    ax[1].set_title("Spectrum: one peak at the flicker")
    ax[1].legend()
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "signal_and_spectrum.png", dpi=110)

    ft = np.linspace(0, 40, 801)
    fig2, ax2 = plt.subplots(figsize=(6.2, 4.2))
    for fs in (24, 30, 60):
        ax2.plot(ft, [alias_frequency(x, fs) for x in ft], label=f"{fs} frames per second")
    ax2.set_xlabel("true flicker frequency (Hz)")
    ax2.set_ylabel("apparent frequency (Hz)")
    ax2.set_title("Aliasing: a fast flicker looks slower")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "aliasing_map.png", dpi=120)

    for dd in (0.02, 0.1, 0.3, 1.0):
        print(f"D = {dd} m: f = {flicker_frequency(dd):.2f} Hz, appears at {alias_frequency(flicker_frequency(dd), 30):.2f} Hz (30 fps), "
              f"{alias_frequency(flicker_frequency(dd), 15):.2f} Hz (15 fps)")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
