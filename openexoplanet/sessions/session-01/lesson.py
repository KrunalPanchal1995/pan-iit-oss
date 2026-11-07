"""Session 1 (Level 1): a planet crossing its star blocks a little light, once per orbit.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: watch a star blink
# **A. Real-world problem.** Stars are far too distant to photograph their planets directly.
# But if a planet's orbit is edge-on to us, the planet passes in front of its star once per
# orbit and blocks a little of the starlight. Astronomers point a telescope at one star for
# weeks and measure its brightness again and again. A tiny, regular dip is the sign of a planet.
#
# **Plan.** (1) make a star's brightness record (a *light curve*) with a hidden planet,
# (2) find the dips, (3) read the period from the gap between dips, (4) read the planet size
# from the depth of a dip.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: how deep is the dip?
# Think of the star as a bright disk and the planet as a small dark disk sliding across it.
# The blocked fraction of the light is the fraction of the star's disk that is covered. For a
# star of radius Rs and a planet of radius Rp, the covered fraction is the ratio of the two
# disk areas:
#
#     depth = (pi Rp^2) / (pi Rs^2) = (Rp / Rs)^2
#
# A planet with one tenth of the star's radius covers 1/100 of the disk, so the star gets
# 1 percent fainter. (Session 2 checks this carefully and adds real-star effects.)

# %%
def transit_depth(radius_ratio):
    """Fraction of starlight blocked by a planet with radius Rp = radius_ratio * Rs."""
    return radius_ratio ** 2


# %% [markdown]
# ## Step 2: a star's brightness record
# `light_curve` makes the brightness (1.0 = normal) every 36 minutes (0.025 days) for 12 days.
# During a transit the brightness drops by `depth`. Real measurements are noisy, so we add
# random noise with a fixed seed so everyone gets the same numbers.

# %%
def box_dips(t, period, t0, duration, depth):
    """Brightness with a flat-bottomed dip of the given depth and duration, once per period."""
    phase = (t - t0 + period / 2) % period - period / 2     # time from the nearest transit centre
    flux = np.ones_like(t)
    flux[np.abs(phase) < duration / 2] -= depth
    return flux


def light_curve(period=3.0, t0=1.0, duration=0.15, depth=0.01, noise=0.0015, days=12.0, seed=7):
    t = np.arange(0.0, days, 0.025)
    rng = np.random.default_rng(seed)
    return t, box_dips(t, period, t0, duration, depth) + rng.normal(0.0, noise, len(t))


# %% [markdown]
# ## Step 3: find the dips and read off the period
# A point belongs to a dip if its brightness is below a *threshold* halfway between normal
# (1.0) and the bottom of a dip. Neighbouring low points form one dip; we ask for at least 3
# in a row so that a single noisy point is not mistaken for a planet. The period is the
# typical gap between the centres of neighbouring dips.

# %%
def find_dips(t, flux, threshold, min_points=3):
    """Return the centre time of each run of at least `min_points` consecutive points below threshold."""
    low = flux < threshold
    centres, start = [], None
    for i, is_low in enumerate(np.append(low, False)):
        if is_low and start is None:
            start = i
        elif not is_low and start is not None:
            if i - start >= min_points:
                centres.append(float(np.mean(t[start:i])))
            start = None
    return np.array(centres)


def period_from_dips(centres):
    """Typical gap between neighbouring dips, in days (needs at least two dips)."""
    return float(np.median(np.diff(centres))) if len(centres) >= 2 else float("nan")


def depth_from_curve(t, flux, centres, duration):
    """Average brightness drop inside the dips, measured against the average outside."""
    inside = np.zeros(len(t), dtype=bool)
    for c in centres:
        inside |= np.abs(t - c) < duration / 4
    return float(np.mean(flux[~inside & (flux > 0.9)]) - np.mean(flux[inside]))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t, flux = light_curve()
    centres = find_dips(t, flux, threshold=0.995)
    period = period_from_dips(centres)
    depth = depth_from_curve(t, flux, centres, 0.15)
    ratio = np.sqrt(depth)
    print(f"{len(t)} measurements, {len(centres)} dips found at {np.round(centres, 2)} days")
    print(f"period from the gaps: {period:.2f} days")
    print(f"depth: {depth:.4f} (about {depth:.1%}), radius ratio Rp/Rs = {ratio:.3f}")

    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot(t, flux, ".", ms=3, color="0.35", label="measured brightness")
    for c in centres:
        ax.axvline(c, color="tab:red", ls=":", lw=1)
    ax.axhline(0.995, color="tab:blue", ls="--", lw=1, label="threshold 0.995")
    ax.set_xlabel("time (days)")
    ax.set_ylabel("brightness (1 = normal)")
    ax.set_title("A light curve with a hidden planet: dips every 3 days")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "light_curve.png", dpi=110)

    fig, ax = plt.subplots(figsize=(5.5, 4))
    ks = np.linspace(0.01, 0.2, 100)
    ax.plot(ks, 100 * transit_depth(ks), color="tab:blue")
    ax.plot([0.1], [1.0], "o", color="tab:red", label="Rp = Rs/10 blocks 1 percent")
    ax.set_xlabel("radius ratio Rp / Rs (no unit)")
    ax.set_ylabel("dip depth (percent of the starlight)")
    ax.set_title("Bigger planet, deeper dip")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "depth_vs_size.png", dpi=110)

# %% [markdown]
# ## Where this stops
# A real transit is not a flat box: the edge of a star is dimmer and the planet slides in and
# out gradually. Session 2 models that and the exact duration.
