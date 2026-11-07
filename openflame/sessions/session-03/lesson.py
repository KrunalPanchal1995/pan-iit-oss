"""Session 3 (Level 3): a synthetic flame video, automatic measurement, error bars, aliasing, sensitivity.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: build a test video, measure it, and say how far to trust the answer
# **A. Real-world problem.** Before you trust a measurement program on a real phone video you must
# test it on a video whose answer you already know. Here we *generate* a noisy flame video with a
# known mean height and a known flicker, extract the height of every frame automatically, recover
# the frequency with an error bar, and then break the method on purpose (too few frames per
# second, a badly chosen threshold) to see how it fails.
#
# **Plan.** (1) render a video, (2) extract the height of each frame to a fraction of a pixel,
# (3) fit the flicker by least squares, (4) compute the error bar and test it against repeated
# experiments, (5) aliasing, (6) threshold sensitivity.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

ROWS, COLS, BASE, AXIS = 100, 61, 95, 30     # picture size, burner row, flame axis column
SOFT = 2.0                                   # the flame tip fades over about SOFT pixels


# %% [markdown]
# ## Step 1: a synthetic video with a known answer
# The flame height follows h(t) = h0 + A sin(2 pi f t + phase), where "height" means the position
# of the half-brightness point on the axis. Every frame gets random camera noise of standard
# deviation `noise` (brightness units, full scale 1) on top of a dim background.
# We draw all frames at once with numpy broadcasting.

# %%
def render_video(h_series, noise=0.1, soft=SOFT, background=0.04, seed=0):
    """Array (n_frames, ROWS, COLS) for a list of true flame heights (px)."""
    h = np.asarray(h_series, dtype=float)[:, None, None]
    z = (BASE - np.arange(ROWS, dtype=float))[None, :, None]
    x = (np.arange(COLS, dtype=float) - AXIS)[None, None, :]
    along = 1.0 / (1.0 + np.exp((z - h) / soft))
    half_width = np.maximum(2.0, 9.0 * (1.0 - 0.75 * z / h))
    img = background + (1.0 - background) * along * np.exp(-(np.maximum(np.abs(x) - 2.0, 0.0) / half_width) ** 2)
    img = np.where(z < 0, background, img)
    img = img + np.random.default_rng(seed).normal(0.0, noise, img.shape)
    return np.clip(img, 0.0, 1.0)


def flicker_heights(duration, fs, h0, amp, f, phase=0.0):
    t = np.arange(int(round(duration * fs))) / fs
    return t, h0 + amp * np.sin(2 * np.pi * f * t + phase)


# %% [markdown]
# ## Step 2: extract the height of every frame
# 1. Average the 5 columns around the axis to get one brightness profile per frame (this
#    averages the noise down by sqrt(5)).
# 2. Estimate the flame brightness (bottom rows) and the background (top rows) over the whole
#    video, and put the threshold a fraction `thr` of the way between them.
# 3. Walk up from the burner until the profile first drops below the threshold, and interpolate
#    in a straight line between the last pixel above and the first pixel below. That gives the tip
#    to a fraction of a pixel (sub-pixel accuracy).

# %%
def extract_heights(video, thr=0.5, subpixel=True):
    prof = video[:, : BASE + 1, AXIS - 2:AXIS + 3].mean(axis=2)[:, ::-1]      # index z = height above the burner
    flame = np.median(prof[:, 2:8])
    bg = np.median(prof[:, -8:])
    if flame - bg < 0.1:                                                     # no visible flame in this video
        return np.zeros(len(video))
    level = bg + thr * (flame - bg)
    below = prof < level
    # the tip is the first height from which 3 pixels in a row are below the level (ignores single noisy pixels)
    run = below[:, :-2] & below[:, 1:-1] & below[:, 2:]
    first = np.argmax(run, axis=1)
    first = np.where(run.any(axis=1), np.maximum(first, 1), BASE)
    if not subpixel:
        return (first - 1).astype(float)
    rows = np.arange(len(prof))
    hi, lo = prof[rows, first - 1], prof[rows, first]
    return first - 1 + (hi - level) / np.maximum(hi - lo, 1e-12)


def predicted_bias(thr, soft=SOFT):
    """Analytic shift of the measured tip for threshold thr (fraction between background and flame): soft * ln((1 - thr) / thr)."""
    return soft * np.log((1.0 - thr) / thr)


# %% [markdown]
# ## Step 3: fit the flicker
# For a trial frequency f, the best-fitting h0 + a sin + b cos is a *linear* least-squares problem.
# We scan frequencies near the FFT peak and keep the one with the smallest residual. That is the
# maximum-likelihood estimate for a sinusoid in white noise.

# %%
def fft_start(trace, fs):
    x = trace - trace.mean()
    w = np.hanning(len(x))
    nfft = len(x) * 8
    a = np.abs(np.fft.rfft(x * w, nfft))
    freqs = np.fft.rfftfreq(nfft, 1.0 / fs)
    a[freqs < 0.1] = 0.0
    return float(freqs[np.argmax(a)])


def _sine_fit(t, y, f):
    M = np.column_stack([np.ones_like(t), np.sin(2 * np.pi * f * t), np.cos(2 * np.pi * f * t)])
    coef, *_ = np.linalg.lstsq(M, y, rcond=None)
    res = y - M @ coef
    return coef, float(res @ res)


def fit_flicker(trace, fs):
    """Least-squares sinusoid. Returns dict(f, amp, mean, resid_std)."""
    t = np.arange(len(trace)) / fs
    f0, span = fft_start(trace, fs), 1.0 / (len(trace) / fs)
    grid = np.linspace(f0 - span, f0 + span, 241)
    best = min(grid, key=lambda f: _sine_fit(t, trace, f)[1])
    fine = np.linspace(best - span / 120, best + span / 120, 41)
    best = min(fine, key=lambda f: _sine_fit(t, trace, f)[1])
    coef, rss = _sine_fit(t, trace, best)
    return {"f": float(best), "amp": float(np.hypot(coef[1], coef[2])), "mean": float(coef[0]),
            "resid_std": float(np.sqrt(rss / (len(trace) - 4)))}


# %% [markdown]
# ## Step 4: the error bar
# For a sinusoid of amplitude A in white noise of standard deviation s, N samples at frame rate fs,
# no unbiased method can beat the Cramer-Rao bound
#
#     sigma_f = fs * sqrt( 12 / ( (2 pi)^2 * eta * N * (N^2 - 1) ) ),     eta = A^2 / (2 s^2)
#
# so the error bar shrinks as N^(-3/2): doubling the recording length improves the frequency by
# almost three times. We check the formula against repeated experiments (different noise seeds).

# %%
def frequency_error_bar(amp, resid_std, n, fs):
    """Cramer-Rao standard deviation of the frequency estimate (Hz)."""
    eta = amp ** 2 / (2.0 * resid_std ** 2)
    return float(fs * np.sqrt(12.0 / ((2 * np.pi) ** 2 * eta * n * (n * n - 1.0))))


def measure_video(video, fs, thr=0.5):
    """Whole pipeline: frames -> heights -> fitted flicker with error bar."""
    trace = extract_heights(video, thr)
    fit = fit_flicker(trace, fs)
    fit["f_err"] = frequency_error_bar(fit["amp"], fit["resid_std"], len(trace), fs)
    fit["trace"] = trace
    return fit


def repeat_experiments(n_trials, duration, fs, h0, amp, f, noise, thr=0.5, seed0=100):
    """Measure n_trials independent noise realisations. Returns arrays of f estimates and CR error bars."""
    t, hs = flicker_heights(duration, fs, h0, amp, f)
    fs_hat, errs = [], []
    for k in range(n_trials):
        r = measure_video(render_video(hs, noise, seed=seed0 + k), fs, thr)
        fs_hat.append(r["f"])
        errs.append(r["f_err"])
    return np.array(fs_hat), np.array(errs)


# %% [markdown]
# ## Step 5: aliasing and a frame rate that is too low
# Taking every second frame of a 30 fps video gives a 15 fps video. A flicker above the new
# Nyquist limit (7.5 Hz) does not disappear: it folds down to the wrong frequency.

# %%
def alias_frequency(f, fs):
    return float(abs(f - fs * np.round(f / fs)))


def decimate(video, k):
    """Keep every k-th frame: the same video filmed at a k times lower frame rate."""
    return video[::k]


# %% [markdown]
# ## Step 6: reading a real clip
# A phone clip becomes frames with `ffmpeg -i clip.mp4 frames/f%04d.png`. `frames_from_pngs`
# reads them into the same (n_frames, rows, columns) array, averaging colour channels to grey.
# You must crop the picture so the burner axis is the middle column (see the mini-project).

# %%
def frames_from_pngs(folder, crop=None):
    import matplotlib.image as mpimg
    files = sorted(pathlib.Path(folder).glob("*.png"))
    out = []
    for f in files:
        im = mpimg.imread(f)
        if im.ndim == 3:
            im = im[:, :, :3].mean(axis=2)
        out.append(im if crop is None else im[crop[0]:crop[1], crop[2]:crop[3]])
    return np.array(out, dtype=float)


# %% [markdown]
# ## The mini-project clip
# `candle_clip()` makes a stand-in for a phone recording of a small flame: 12 s at 30 frames per
# second, 0.5 mm per pixel, a flame 28 mm tall that flickers by +/- 1.5 mm at 7.3 Hz. It is
# *synthetic*: use it to develop your program, then point the same program at your own clip.

# %%
def candle_clip(seed=7):
    """Returns (video, fs, truth) for the synthetic candle used in the mini-project."""
    truth = {"f": 7.3, "h0_mm": 28.0, "amp_mm": 1.5, "scale_mm_per_px": 0.5}
    t, hs = flicker_heights(12.0, 30.0, truth["h0_mm"] / 0.5, truth["amp_mm"] / 0.5, truth["f"])
    return render_video(hs, noise=0.2, seed=seed), 30.0, truth


# %% [markdown]
# ## Step 7: see it
# Three figures: the extracted trace against the truth, the spectra at 30 and 15 frames per second,
# and how the threshold shifts the measured height.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    fs, dur, scale = 30.0, 8.0, 13.0                  # frames/s, seconds, mm per pixel
    f_true, amp = 2.74, 2.0                            # flicker (Hz) and amplitude (px)
    h0 = (0.235 * 40 ** 0.4 - 1.02 * 0.3) * 1000 / scale   # Heskestad height for Q = 40 kW, D = 0.3 m, in px
    t, hs = flicker_heights(dur, fs, h0, amp, f_true)
    video = render_video(hs, noise=0.15, seed=1)
    r = measure_video(video, fs)
    err = r["trace"] - hs
    print(f"video {video.shape}, true f = {f_true} Hz")
    print(f"trace error: mean {err.mean():+.3f} px, std {err.std():.3f} px (1 px = {scale} mm)")
    print(f"fit: f = {r['f']:.4f} +/- {r['f_err']:.4f} Hz, amp = {r['amp']:.2f} px, mean = {r['mean']:.2f} px ({r['mean'] * scale:.0f} mm)")

    fig, ax = plt.subplots(1, 2, figsize=(9.5, 3.8), gridspec_kw={"width_ratios": [1, 2]})
    ax[0].imshow(video[0], cmap="gray", vmin=0, vmax=1)
    ax[0].axhline(BASE - r["trace"][0], color="tab:red", lw=1)
    ax[0].set_title("frame 0, tip found")
    ax[0].set_xlabel("column (px)")
    ax[0].set_ylabel("row (px)")
    ax[1].plot(t[:90], hs[:90], "-", color="gray", label="true height")
    ax[1].plot(t[:90], r["trace"][:90], ".", color="tab:red", label="extracted")
    ax[1].set_xlabel("time (s)")
    ax[1].set_ylabel("flame height (px)")
    ax[1].set_title("Extracted height trace, first 3 s")
    ax[1].legend()
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "trace_vs_truth.png", dpi=110)

    f9 = 9.0
    t9, h9 = flicker_heights(dur, fs, h0, amp, f9)
    v9 = render_video(h9, noise=0.15, seed=2)
    r30 = measure_video(v9, fs)
    r15 = measure_video(decimate(v9, 2), fs / 2)
    print(f"true 9.0 Hz: at 30 fps measured {r30['f']:.3f} Hz; at 15 fps measured {r15['f']:.3f} Hz "
          f"(alias prediction {alias_frequency(f9, 15):.3f} Hz)")
    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    for rr, rate, c in ((r30, 30.0, "tab:blue"), (r15, 15.0, "tab:red")):
        x = rr["trace"] - rr["trace"].mean()
        a = np.abs(np.fft.rfft(x * np.hanning(len(x)), 8 * len(x))) * 2 / np.hanning(len(x)).sum()
        ax2.plot(np.fft.rfftfreq(8 * len(x), 1 / rate), a, color=c, label=f"{rate:.0f} frames per second")
        ax2.axvline(rate / 2, color=c, ls=":")
    ax2.axvline(f9, color="gray", ls="--", label="true 9 Hz")
    ax2.set_xlim(0, 15)
    ax2.set_xlabel("frequency (Hz)")
    ax2.set_ylabel("amplitude (px)")
    ax2.set_title("Same flame, two frame rates (dotted: Nyquist)")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "aliasing_spectra.png", dpi=110)

    f_hat, e_cr = repeat_experiments(30, dur, fs, h0, amp, f_true, 0.15)
    print(f"30 repeats: mean f {f_hat.mean():.4f} Hz, scatter (std) {f_hat.std(ddof=1):.4f} Hz, "
          f"Cramer-Rao bar {e_cr.mean():.4f} Hz")

    weak_hat, weak_err = repeat_experiments(30, dur, fs, h0, 0.4, f_true, 0.35)
    bad = int(np.sum(np.abs(weak_hat - f_true) > 0.1))
    print(f"weak flicker (0.4 px) and more noise: {bad} of 30 runs lock onto a noise peak "
          f"(error > 0.1 Hz) although the formula still promises +/- {weak_err.mean():.4f} Hz")

    thrs = np.arange(0.2, 0.81, 0.1)
    meas = []
    for th in thrs:
        tr = extract_heights(video, th)
        meas.append((tr - hs).mean())
        print(f"threshold {th:.2f}: mean height shift {meas[-1]:+.2f} px, predicted {predicted_bias(th):+.2f} px, "
              f"frequency {fit_flicker(tr, fs)['f']:.3f} Hz")
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    xs = np.linspace(0.12, 0.88, 100)
    ax3.plot(xs, predicted_bias(xs), color="gray", label="formula: SOFT ln((1-thr)/thr)")
    ax3.plot(thrs, meas, "o", color="tab:red", label="measured from video")
    ax3.set_xlabel("threshold (fraction between background and flame)")
    ax3.set_ylabel("height shift (px)")
    ax3.set_title("The threshold moves the height, not the frequency")
    ax3.legend()
    ax3.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "threshold_sensitivity.png", dpi=110)
    cv, cfs, ctruth = candle_clip()
    cr = measure_video(cv, cfs)
    print(f"synthetic candle: f = {cr['f']:.4f} +/- {cr['f_err']:.4f} Hz (truth {ctruth['f']} Hz), "
          f"mean height {cr['mean'] * 0.5:.1f} mm, flicker amplitude {cr['amp'] * 0.5:.2f} mm")
    for k in (2, 3):
        rk = measure_video(decimate(cv, k), cfs / k)
        print(f"  decimated by {k} ({cfs / k:.0f} fps): {rk['f']:.3f} Hz, alias prediction {alias_frequency(ctruth['f'], cfs / k):.3f} Hz")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
