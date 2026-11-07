"""Session 2 (Level 2): the sampling theorem and the alias frequency formula.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the alias formula and the Nyquist limit
# **A. Real-world problem.** Session 1 found a sawtooth by looking at pictures. Engineers meet
# the same sawtooth in sound cards, oscilloscopes and cameras, and they need a formula and a
# rule: how fast must we sample so that nothing is mistaken for something else?
#
# **Plan.** (1) sample a sine wave, (2) show that two different frequencies give *identical*
# samples, (3) write the alias formula, (4) use it to design a frame rate.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: sampling a sine wave
# A signal x(t) = sin(2 pi f t) is measured only at the instants t_n = n / fs (n = 0, 1, 2, ...),
# where fs is the sampling rate (samples per second, hertz). The numbers we keep are
#
#     x[n] = sin(2 pi f n / fs)

# %%
def sample_sine(f, fs, n_samples, phase=0.0):
    """The samples x[n] = sin(2 pi f n / fs + phase), n = 0 .. n_samples - 1."""
    n = np.arange(n_samples)
    return np.sin(2.0 * np.pi * f * n / fs + phase)


# %% [markdown]
# ## Step 2: two frequencies, one set of samples
# Add a whole number k of sampling rates to the frequency: f' = f + k fs. Then
# 2 pi f' n / fs = 2 pi f n / fs + 2 pi k n, and adding a whole number of turns (2 pi k n) to an
# angle changes nothing. So f and f + k fs give exactly the same samples. Also sin(-a) = -sin(a),
# so f and -f give the same samples up to a sign. After sampling, no maths can tell them apart.

# %%
def same_samples(f1, f2, fs, n_samples=64, phase=0.0, tol=1e-9):
    return bool(np.allclose(sample_sine(f1, fs, n_samples, phase), sample_sine(f2, fs, n_samples, phase), atol=tol))


# %% [markdown]
# ## Step 3: the alias frequency
# Choose the whole number k that brings f closest to a multiple of fs (k = round(f / fs)). What
# is left over is the *signed alias* f - k fs, always between -fs/2 and +fs/2. Its size is the
# frequency the samples seem to have:
#
#     f_alias = | f - k fs |,   k = round(f / fs),   so 0 <= f_alias <= fs / 2
#
# The limit fs / 2 is the **Nyquist frequency**. Below it nothing is confused; above it we get an alias.

# %%
def nearest_multiple(f, fs):
    """k = round(f / fs), rounding halves upward (a tie only happens at f = fs/2 + j fs)."""
    return int(np.floor(f / fs + 0.5))


def signed_alias(f, fs):
    return f - fs * nearest_multiple(f, fs)


def alias_frequency(f, fs):
    return abs(signed_alias(f, fs))


def nyquist(fs):
    return fs / 2.0


# %% [markdown]
# ## Step 4: design a frame rate
# To keep a signal whose highest frequency is f_max, the sampling rate must satisfy
# fs > 2 f_max. A wheel with N identical spokes looks the same after 1/N of a turn, so its
# picture repeats N f times per second: the signal frequency is N f, not f. `pattern_apparent_rev`
# gives the apparent turning speed of such a wheel in rev/s.

# %%
def min_sampling_rate(f_max):
    """Smallest rate that must be exceeded (strictly) to avoid aliasing: 2 f_max."""
    return 2.0 * f_max


def pattern_apparent_rev(f_rev, n_spokes, fs):
    """Apparent signed speed (rev/s) of a wheel with n identical spokes turning f_rev rev/s."""
    return signed_alias(n_spokes * f_rev, fs) / n_spokes


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    f, fs = 40.0, 50.0
    t = np.linspace(0, 0.2, 2000)
    tn = np.arange(0, 0.2, 1 / fs)
    fa = signed_alias(f, fs)
    print(f"f = {f} Hz at fs = {fs} Hz: k = {nearest_multiple(f, fs)}, signed alias = {fa}, alias = {alias_frequency(f, fs)} Hz")
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.plot(t, np.sin(2 * np.pi * f * t), color="lightgray", label="true 40 Hz signal")
    ax.plot(t, np.sin(2 * np.pi * fa * t), color="tab:blue", label="alias (-10 Hz) through the samples")
    ax.plot(tn, np.sin(2 * np.pi * f * tn), "ko", label="samples at 50 Hz")
    ax.set_xlabel("time t (s)")
    ax.set_ylabel("x(t) (arbitrary units)")
    ax.set_title("Samples of a 40 Hz sine at 50 Hz fit a slow 10 Hz sine")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "samples_alias.png", dpi=120)

    f_axis = np.linspace(0, 150, 1501)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(f_axis, [alias_frequency(x, fs) for x in f_axis], color="tab:blue", label="f_alias")
    ax2.axhline(nyquist(fs), color="tab:red", ls="--", label="Nyquist fs/2 = 25 Hz")
    ax2.set_xlabel("true frequency f (Hz)")
    ax2.set_ylabel("alias frequency (Hz)")
    ax2.set_title("Folding at fs = 50 Hz: zigzag between 0 and fs/2")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "folding.png", dpi=120)
    print("4-blade fan at 12 rev/s filmed at 30 fps looks like", pattern_apparent_rev(12, 4, 30), "rev/s")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
