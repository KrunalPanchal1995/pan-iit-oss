"""Session 3 (Level 3): simulate sampled signals and filmed wheels, find the folded peak, recover the true frequency.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulate, measure and recover
# **A. Real-world problem.** You are handed two clips of a fan and nothing else. Each clip
# shows the marked blade turning at a slow, wrong-looking speed. Can you work out how fast the
# fan really turns?
#
# **Plan.** (1) build sampled signals and rotating-marker clips in code, (2) find the folded peak
# with the FFT and check it against the exact alias formula, (3) combine two frame rates to
# recover the true frequency, (4) measure what jitter and camera exposure do.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the exact folding formula (our reference)
# From Session 2: the signed alias is f - k fs with k = round(f / fs). Everything we measure
# below is compared with this.

# %%
def signed_alias(f, fs):
    return f - fs * math.floor(f / fs + 0.5)


def alias_frequency(f, fs):
    return abs(signed_alias(f, fs))


# %% [markdown]
# ## Step 2: sampled signals, with optional jitter and exposure
# `sampled_signal` returns x[n] = sin(2 pi f t_n + phase) at t_n = n/fs. Two real-camera effects can be switched on:
# * `jitter_std`: each sample time is wrong by a random amount (standard deviation, seconds);
# * `exposure`: the shutter stays open for a fraction of a frame period and the sensor *averages*
#   the signal over that time (motion blur).

# %%
def sampled_signal(f, fs, n, phase=0.3, jitter_std=0.0, exposure=0.0, seed=0, substeps=201):
    t = np.arange(n) / fs
    if jitter_std > 0:
        t = t + np.random.default_rng(seed).normal(0.0, jitter_std, n)
    if exposure <= 0:
        return np.sin(2 * np.pi * f * t + phase)
    tau = exposure / fs
    offs = (np.arange(substeps) + 0.5) / substeps * tau - tau / 2
    return np.sin(2 * np.pi * f * (t[:, None] + offs[None, :]) + phase).mean(axis=1)


# %% [markdown]
# ## Step 3: the spectrum and its folded peak
# The FFT splits a list of N samples into frequencies 0, fs/N, 2 fs/N, ... up to fs/2. The
# amplitude of a pure sine appears as one tall peak, at the *alias* frequency.

# %%
def spectrum(x, fs):
    """Frequencies (Hz) and amplitudes of the real signal x (a pure sine of amplitude 1 gives a peak of height 1)."""
    n = len(x)
    amp = 2.0 * np.abs(np.fft.rfft(x)) / n
    amp[0] /= 2.0
    if n % 2 == 0:
        amp[-1] /= 2.0
    return np.fft.rfftfreq(n, 1.0 / fs), amp


def peak_frequency(x, fs):
    freqs, amp = spectrum(x, fs)
    return float(freqs[int(np.argmax(amp))])


def max_alias_error(fs, n, f_values):
    """Largest |FFT peak - exact alias formula| over a list of true frequencies."""
    worst = 0.0
    for f in f_values:
        worst = max(worst, abs(peak_frequency(sampled_signal(f, fs, n), fs) - alias_frequency(f, fs)))
    return worst


# %% [markdown]
# ## Step 4: a filmed wheel
# `render_clip` makes a stack of small greyscale pictures: a bright blob (the marker) on a
# wheel of radius `radius` pixels, one picture per frame. `measure_apparent` finds the blob in
# each picture, computes its angle, and turns the frame-to-frame angle steps into a signed
# apparent speed. The mean distance of the blob from the centre, divided by the radius, tells how
# much the motion blur has smeared it.

# %%
def render_clip(f, fs, n_frames, size=64, radius=20.0, sigma=2.0, phase=0.4, exposure=0.0, noise=0.0, seed=0, substeps=15):
    yy, xx = np.mgrid[0:size, 0:size]
    c = (size - 1) / 2.0
    tau = exposure / fs
    offs = (np.arange(substeps) + 0.5) / substeps * tau - tau / 2 if exposure > 0 else np.array([0.0])
    rng = np.random.default_rng(seed)
    clip = np.zeros((n_frames, size, size))
    for k in range(n_frames):
        for o in offs:
            th = 2 * np.pi * f * (k / fs + o) + phase
            mx, my = c + radius * np.cos(th), c - radius * np.sin(th)
            clip[k] += np.exp(-((xx - mx) ** 2 + (yy - my) ** 2) / (2 * sigma ** 2)) / len(offs)
    if noise > 0:
        clip += rng.normal(0.0, noise, clip.shape)
    return clip


def marker_polar(clip):
    """Angle (radians, counter-clockwise) and radius (pixels) of the brightest blob in every frame."""
    n, size, _ = clip.shape
    yy, xx = np.mgrid[0:size, 0:size]
    c = (size - 1) / 2.0
    ang, rad = [], []
    for img in clip:
        w = np.clip(img - 0.1 * img.max(), 0, None)
        x = (w * xx).sum() / w.sum() - c
        y = c - (w * yy).sum() / w.sum()
        ang.append(math.atan2(y, x))
        rad.append(math.hypot(x, y))
    return np.array(ang), np.array(rad)


def measure_apparent(clip, fs):
    """Signed apparent speed in rev/s (negative = clockwise) from the mean frame-to-frame turn."""
    ang, _ = marker_polar(clip)
    steps = np.angle(np.exp(1j * np.diff(ang)))          # each step folded into (-pi, pi]
    mean_step = np.angle(np.mean(np.exp(1j * steps)))
    return float(mean_step / (2 * np.pi) * fs)


# %% [markdown]
# ## Step 5: recover the true frequency from two frame rates
# One clip says f = a1 + k1 fs1 for some whole number k1. A second clip filmed at another rate says
# f = a2 + k2 fs2. Only a few numbers appear in both lists: the common value is the answer. If the
# apparent speeds are measured as signed numbers, the pair (a1, a2) repeats only every
# lcm(fs1, fs2) rev/s (for whole-number rates), so that is the unambiguous range. Using only the sizes |a| we must also try -a.

# %%
def candidates(a, fs, f_lo, f_hi, signed=True):
    """All frequencies in [f_lo, f_hi] that look like a at frame rate fs."""
    bases = [a] if signed else sorted({a, -a})
    out = []
    for b in bases:
        k0 = math.ceil((f_lo - b) / fs - 1e-9)
        k1 = math.floor((f_hi - b) / fs + 1e-9)
        out += [b + k * fs for k in range(k0, k1 + 1)]
    return sorted(out)


def recover_frequency(a1, fs1, a2, fs2, f_lo=0.0, f_hi=100.0, tol=0.3, signed=True):
    """Frequencies compatible with both clips (list; one entry means the answer is unique in the range)."""
    c1 = candidates(a1, fs1, f_lo, f_hi, signed)
    c2 = candidates(a2, fs2, f_lo, f_hi, signed)
    found = []
    for x in c1:
        near = [y for y in c2 if abs(x - y) <= tol]
        if near:
            found.append(round((x + near[0]) / 2.0, 6))
    return found


def ambiguity_period(fs1, fs2):
    """With whole-number rates and signed measurements, f and f + this give the same pair of pictures."""
    return int(np.lcm(int(round(fs1)), int(round(fs2))))


# %% [markdown]
# ## Step 6: what jitter and exposure do
# * **Jitter** of standard deviation s (seconds) in the sample times turns the sine
#   into sin(2 pi f t + 2 pi f e). The coherent peak shrinks by the factor exp(-(2 pi f s)^2 / 2);
#   the missing power becomes a noise floor. It depends on the TRUE f, not on the alias.
# * **Exposure** (the shutter open for tau seconds) averages the signal over tau, which multiplies a
#   sine of frequency f by |sinc(f tau)| with sinc(x) = sin(pi x)/(pi x). That is a built-in
#   anti-alias filter: fast motion is blurred away *before* it can fold. It cannot be undone afterwards.

# %%
def jitter_factor(f, jitter_std):
    return math.exp(-0.5 * (2 * np.pi * f * jitter_std) ** 2)


def projected_amplitude(x, fs, f_signed):
    """Amplitude of x at the frequency f_signed (complex projection)."""
    n = np.arange(len(x))
    return float(2.0 * abs(np.sum(x * np.exp(-2j * np.pi * f_signed * n / fs))) / len(x))


def exposure_gain(f, exposure, fs):
    return abs(float(np.sinc(f * exposure / fs)))


# %% [markdown]
# ## Step 7: the mystery fan (used by the mini-project)
# A real fan with one marked blade, filmed at whatever frame rate you choose. Do not read the
# true speed from the code; recover it from the clips.

# %%
_MYSTERY_REV_PER_S = 135.0 / 6.0          # kept out of your way on purpose


def mystery_fan(fs, n_frames=60, seed=5):
    return render_clip(_MYSTERY_REV_PER_S, fs, n_frames, phase=0.9 + 0.1 * fs, noise=0.01, seed=seed)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    f, fs, n = 22.5, 30.0, 300
    x = sampled_signal(f, fs, n)
    freqs, amp = spectrum(x, fs)
    print(f"true f = {f} Hz at fs = {fs} Hz: exact alias = {alias_frequency(f, fs)} Hz, FFT peak = {peak_frequency(x, fs)} Hz")
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
    t = np.linspace(0, 0.4, 2000)
    axs[0].plot(t, np.sin(2 * np.pi * f * t + 0.3), color="lightgray", label="true 22.5 Hz")
    axs[0].plot(t, np.sin(2 * np.pi * signed_alias(f, fs) * t + 0.3), color="tab:blue", label="alias -7.5 Hz")
    axs[0].plot(np.arange(12) / fs, x[:12], "ko", label="samples at 30 Hz")
    axs[0].set_xlabel("time t (s)")
    axs[0].set_ylabel("x(t) (arbitrary units)")
    axs[0].set_title("The samples")
    axs[0].legend(fontsize=8)
    axs[1].plot(freqs, amp, color="tab:blue")
    axs[1].axvline(alias_frequency(f, fs), color="tab:red", ls="--", label="exact alias 7.5 Hz")
    axs[1].axvline(f % fs, color="gray", ls=":", label="where 22.5 Hz would be (not on axis)")
    axs[1].set_xlabel("frequency (Hz)")
    axs[1].set_ylabel("amplitude (arbitrary units)")
    axs[1].set_title("FFT: one peak, folded to 7.5 Hz")
    axs[1].legend(fontsize=8)
    for a in axs:
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "spectrum_peak.png", dpi=120)

    f_test = np.arange(0.7, 90, 0.9)
    print("largest |FFT peak - formula| over", len(f_test), "frequencies:", round(max_alias_error(30.0, 300, f_test), 3), "Hz")

    a1, a2 = signed_alias(f, 30.0), signed_alias(f, 24.0)
    print("two clips:", a1, "rev/s at 30 fps and", a2, "rev/s at 24 fps ->", recover_frequency(a1, 30, a2, 24, 0, 100))
    fig2, ax2 = plt.subplots(figsize=(8, 2.6))
    for y, fsx, a, col in ((1, 30, a1, "tab:blue"), (0, 24, a2, "tab:green")):
        for c_ in candidates(a, fsx, 0, 130):
            ax2.plot(c_, y, "|", ms=30, color=col)
    ax2.axvline(22.5, color="tab:red", ls="--", label="common value 22.5")
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(["24 fps clip", "30 fps clip"])
    ax2.set_xlabel("candidate true speed (rev/s)")
    ax2.set_title("Each clip allows a ladder of speeds; the true one is on both ladders")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "two_rates.png", dpi=120)

    sig = np.linspace(0, 0.004, 9)
    meas = [np.mean([projected_amplitude(sampled_signal(40, 50, 20000, jitter_std=s, seed=sd), 50, -10) for sd in range(3)]) for s in sig]
    taus = np.linspace(0, 1, 21)
    ratio = []
    for e in taus:
        _, r = marker_polar(render_clip(22.5, 30.0, 8, exposure=e))
        ratio.append(r.mean() / 20.0)
    fig3, axs3 = plt.subplots(1, 2, figsize=(10, 3.6))
    axs3[0].plot(sig * 1000, [jitter_factor(40, s) for s in sig], color="tab:blue", label="formula exp(-(2 pi f s)^2 / 2)")
    axs3[0].plot(sig * 1000, meas, "ko", label="simulation")
    axs3[0].set_xlabel("timing jitter s (ms)")
    axs3[0].set_ylabel("peak amplitude (relative)")
    axs3[0].set_title("Jitter at f = 40 Hz, fs = 50 Hz")
    axs3[1].plot(taus, [abs(np.sinc(22.5 * e / 30.0)) for e in taus], color="tab:blue", label="|sinc(f tau)|")
    axs3[1].plot(taus, ratio, "ko", label="rendered clips")
    axs3[1].set_xlabel("exposure (fraction of frame period)")
    axs3[1].set_ylabel("marker radius / wheel radius")
    axs3[1].set_title("Motion blur at f = 22.5 rev/s, 30 fps")
    for a in axs3:
        a.grid(alpha=0.3)
        a.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "jitter_exposure.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), run the checkpoint,
# then start the mini-project.
