"""Session 1 (Level 1): a resistor and a capacitor smooth a noisy sensor signal.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a resistor and a capacitor smooth a noisy sensor signal
# **A. Real-world problem.** A sensor wire picks up fast jitter on top of a slow signal you
# care about. A resistor in the wire and a capacitor to ground form an *RC low-pass filter*:
# it lets slow changes through and flattens fast ones.
#
# **Plan.** (1) build a slow signal plus fast jitter, (2) smooth it with an RC filter,
# (3) measure how much of each part survives, (4) see the price: the output runs late.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

SLOW_HZ = 2.0       # the slow signal we want to keep (hertz)
JITTER_HZ = 40.0    # the fast jitter we want to remove (hertz)
FS = 5000.0         # samples per second used by the simulation


# %% [markdown]
# ## Step 1: a slow signal with fast jitter
# `slow` is a 2 Hz wave of amplitude 1 (think: a temperature that rises and falls twice a
# second, scaled to 1). `jitter` is a 40 Hz wave of amplitude 0.4 added on top.

# %%
def make_time(seconds=3.0, fs=FS):
    return np.arange(int(seconds * fs)) / fs


def noisy_signal(t, jitter_amp=0.4):
    slow = np.sin(2 * np.pi * SLOW_HZ * t)
    jitter = jitter_amp * np.sin(2 * np.pi * JITTER_HZ * t)
    return slow + jitter


# %% [markdown]
# ## Step 2: the RC filter
# The product tau = R * C (ohms times farads = seconds) is the filter's *time constant*. The
# capacitor voltage moves a fraction of the way towards the input at each tiny time step; a
# big tau means it moves slowly, so fast wiggles are ignored. The fraction per step is
# `alpha = 1 - exp(-dt / tau)`.

# %%
def time_constant(R, C):
    """tau = R * C in seconds (R in ohms, C in farads)."""
    return R * C


def rc_smooth(x, dt, tau):
    """Output of an RC low-pass for input samples x spaced dt seconds apart (tau in seconds)."""
    alpha = 1.0 - np.exp(-dt / tau)
    y = np.empty(len(x))
    level = x[0]
    for i, v in enumerate(x):
        level += alpha * (v - level)
        y[i] = level
    return y


# %% [markdown]
# ## Step 3: how much of each part survives?
# We measure the size (amplitude) of a wave of known frequency inside a signal by fitting a
# sine and a cosine of that frequency. We skip the first 2 seconds so the start-up wobble has
# died away, then compare output size with input size.

# %%
def amplitude_at(y, t, f):
    """Amplitude of the component of frequency f in y (use whole seconds of data)."""
    m = np.column_stack([np.sin(2 * np.pi * f * t), np.cos(2 * np.pi * f * t)])
    coef, *_ = np.linalg.lstsq(m, y, rcond=None)
    return float(np.hypot(coef[0], coef[1]))


def survivors(R, C, jitter_amp=0.4):
    """(fraction of slow kept, fraction of jitter kept) for an RC filter with R ohms, C farads."""
    t = make_time()
    y = rc_smooth(noisy_signal(t, jitter_amp), 1.0 / FS, time_constant(R, C))
    tail = t >= 2.0
    slow = amplitude_at(y[tail], t[tail], SLOW_HZ) / 1.0
    jit = amplitude_at(y[tail], t[tail], JITTER_HZ) / jitter_amp
    return slow, jit


# %% [markdown]
# ## Step 4: see it, and see the price
# Heavier filtering removes more jitter but also eats some of the slow signal and makes the
# output arrive late.

# %%
def delay_seconds(R, C):
    """Time by which the slow wave is late, measured from the zero crossings of the output."""
    t = make_time(3.0)
    y = rc_smooth(np.sin(2 * np.pi * SLOW_HZ * t), 1.0 / FS, time_constant(R, C))
    tail = (t >= 2.0) & (t < 2.5)
    yy, tt = y[tail], t[tail]
    i = int(np.argmax((yy[:-1] < 0) & (yy[1:] >= 0)))      # first upward zero crossing
    cross = tt[i] - yy[i] * (tt[i + 1] - tt[i]) / (yy[i + 1] - yy[i])
    return float(cross - 2.0)       # the input crosses upward at exactly t = 2.0 s


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    R, C = 10e3, 3.2e-6
    t = make_time()
    x = noisy_signal(t)
    y = rc_smooth(x, 1.0 / FS, time_constant(R, C))
    win = (t >= 2.0) & (t < 3.0)
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.plot(t[win], x[win], color="0.65", lw=1, label="sensor signal (slow + jitter)")
    ax.plot(t[win], y[win], color="C0", lw=2, label="after RC filter")
    ax.plot(t[win], np.sin(2 * np.pi * SLOW_HZ * t[win]), "k:", lw=1, label="the slow signal alone")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("signal (relative units)")
    ax.set_title("R = 10 kohm, C = 3.2 uF: jitter flattened, signal slightly late")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "smoothing.png", dpi=120)

    slow, jit = survivors(R, C)
    print(f"tau = {time_constant(R, C) * 1000:.1f} ms; slow kept {slow:.3f}, jitter kept {jit:.3f}, "
          f"delay {delay_seconds(R, C) * 1000:.1f} ms")

    taus = np.geomspace(0.002, 0.5, 14)
    kept = np.array([survivors(tt / 1e-6, 1e-6) for tt in taus])      # R = tau / 1 uF, C = 1 uF
    fig2, ax2 = plt.subplots(figsize=(6.4, 3.8))
    ax2.semilogx(taus * 1000, kept[:, 0], "o-", color="C2", label="slow signal kept (2 Hz)")
    ax2.semilogx(taus * 1000, kept[:, 1], "s-", color="C3", label="jitter kept (40 Hz)")
    ax2.set_xlabel("time constant tau = R C (ms)")
    ax2.set_ylabel("fraction of the amplitude kept")
    ax2.set_title("More smoothing removes jitter, but the slow signal suffers too")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "kept_vs_tau.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
