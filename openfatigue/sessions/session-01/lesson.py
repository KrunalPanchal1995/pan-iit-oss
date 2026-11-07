"""Session 1 (Level 1): a part can break below its one-pull strength if you load it again and again.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: repeated loading breaks things that one pull cannot
# **A. Real-world problem.** Bend a paper clip once and it stays whole. Bend it back and forth
# and it snaps, although no single bend was stronger than the first. Bridges, axles and aircraft
# parts fail the same way. This is *fatigue*.
#
# **Plan.** (1) draw a cyclic stress wave, (2) write the simple "life versus stress" relation
# (the S-N curve), (3) turn a stress into a number of cycles and a time, (4) plot the curve.
# This is a simplified teaching model with illustrative numbers for a generic steel. It is not
# a design tool for real parts.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

SU = 600.0      # ultimate (one-pull) strength of our illustrative steel, MPa
SE = 300.0      # endurance limit = 0.5 * SU, a common rule of thumb for steels, MPa
# Basquin line through two anchor points: 0.9*SU at 1000 cycles and SE at 1 million cycles
B = -np.log10(0.9 * SU / SE) / 3.0            # exponent b (negative); about -0.085
A = (0.9 * SU) ** 2 / SE                      # coefficient A, MPa


# %% [markdown]
# ## Step 1: the cyclic stress wave
# A shaft that turns while it is bent sees every point of its surface go from pull to push and
# back again. The stress is a wave: `stress = mean + amplitude * sin(2 pi f t)`.
# *Amplitude* is the height of the wave above its middle; one *cycle* is one full wave.

# %%
def stress_wave(t, amplitude, mean=0.0, freq=1.0):
    """Stress (MPa) at time t (s) for a sine load with the given amplitude, mean and frequency (Hz)."""
    return mean + amplitude * np.sin(2 * np.pi * freq * np.asarray(t, dtype=float))


def stress_range(amplitude):
    """Range = highest minus lowest stress of one cycle = 2 * amplitude."""
    return 2.0 * amplitude


# %% [markdown]
# ## Step 2: the S-N curve (Basquin's relation)
# Test many identical bars, each at a different stress amplitude S_a, and count the cycles N
# until each breaks. On log axes the points fall near a straight line:
#
#     S_a = A * N**b        (b is negative: more stress, fewer cycles)
#
# Our line passes through 0.9*S_u at 1000 cycles and through the endurance limit S_e at one
# million cycles. For many steels, S_e is about half of S_u and b is a small negative number,
# about -0.1 (here -0.085). Below S_e a steel part may last "forever" (see the caveat in
# Session 2).

# %%
def cycles_to_failure(amplitude):
    """Cycles to failure for a fully reversed stress amplitude (MPa).
    Returns numpy.inf at or below the endurance limit (no predicted failure, steel only)."""
    amp = float(amplitude)
    if amp <= SE:
        return np.inf
    return float((amp / A) ** (1.0 / B))


def time_to_failure_hours(amplitude, freq):
    """Hours of running at `freq` cycles per second until failure (inf if no predicted failure)."""
    return cycles_to_failure(amplitude) / freq / 3600.0


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t = np.linspace(0, 2, 400)
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.plot(t, stress_wave(t, 400), label="stress amplitude 400 MPa")
    ax.axhline(SU, color="red", ls="--", label="one-pull strength 600 MPa")
    ax.axhline(-SU, color="red", ls="--")
    ax.axhline(0, color="gray", lw=0.8)
    ax.annotate("", xy=(0.25, 400), xytext=(0.25, 0), arrowprops=dict(arrowstyle="<->"))
    ax.text(0.28, 180, "amplitude", fontsize=9)
    ax.set_xlabel("time (s), 1 Hz")
    ax.set_ylabel("stress (MPa)")
    ax.set_title("A cyclic stress wave never exceeds the one-pull strength, yet it breaks the part")
    ax.title.set_fontsize(9)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "stress_wave.png", dpi=120)

    n = np.logspace(3, 7, 200)
    s = np.where(n < 1e6, A * n ** B, SE)
    fig2, ax2 = plt.subplots(figsize=(6.5, 4.2))
    ax2.semilogx(n, s, label="S-N curve (illustrative steel)")
    ax2.axhline(SU, color="red", ls="--", label="one-pull strength S_u")
    ax2.axhline(SE, color="gray", ls=":", label="endurance limit S_e")
    for amp in (500, 400, 350):
        nn = cycles_to_failure(amp)
        ax2.plot(nn, amp, "ko")
        ax2.annotate(f"{amp} MPa: {nn:,.0f} cycles", (nn, amp), textcoords="offset points", xytext=(6, 5), fontsize=8)
        print(f"amplitude {amp} MPa -> {nn:,.0f} cycles")
    ax2.set_xlabel("cycles to failure N (log scale)")
    ax2.set_ylabel("stress amplitude S_a (MPa)")
    ax2.set_title("S-N curve: the more stress, the fewer cycles")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "sn_curve.png", dpi=120)
    print(f"b = {B:.4f}, A = {A:.1f} MPa")
    print(f"400 MPa at 10 Hz lasts {time_to_failure_hours(400, 10) * 60:.1f} minutes")

# %% [markdown]
# ## Where this stops
# Real fatigue data scatter widely, and mean stress, notches and surface finish all matter.
# Those are Sessions 2 and 3.
