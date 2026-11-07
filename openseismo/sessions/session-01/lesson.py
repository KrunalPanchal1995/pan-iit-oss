"""Session 1 (Level 1): P waves, S waves and the gap that gives the distance.

Educational only. This is not an earthquake warning or prediction tool:
earthquakes cannot be predicted.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: the gap between P and S gives the distance
# **A. Real-world problem.** An earthquake sends out two kinds of wave that travel at different
# speeds. A seismograph (a ground-motion recorder) sees the fast one first, the slower one
# later. The longer the wait between them, the farther away the quake was, just like counting
# seconds between lightning and thunder.
#
# **Plan.** (1) travel time = distance / speed, (2) the P-S gap grows with distance,
# (3) turn a measured gap back into a distance, (4) draw a synthetic seismogram.
#
# **Safety note.** This repo is for learning. It cannot warn you of an earthquake and
# earthquakes cannot be predicted.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# typical upper-crust speeds, APPROXIMATE values used for teaching (km/s)
VP = 6.0   # P wave: push-pull, fast
VS = 3.5   # S wave: side-to-side shaking, slower


# %% [markdown]
# ## Step 1: travel time
# A wave that travels a distance d at speed v needs t = d / v. A P wave to a station 100 km away
# at 6.0 km/s needs 100 / 6.0 = 16.7 s. An S wave at 3.5 km/s needs 100 / 3.5 = 28.6 s.

# %%
def travel_time(d_km, v_kms):
    """Time in seconds for a wave to cover d_km kilometres at v_kms km/s."""
    return np.asarray(d_km, dtype=float) / v_kms


# %% [markdown]
# ## Step 2: the gap grows with distance
# The S wave falls further behind the longer it travels. The gap is
# gap = d / vs - d / vp. It is zero at the source and grows in a straight line with distance.

# %%
def sp_gap(d_km, vp=VP, vs=VS):
    """S minus P arrival time (seconds) at distance d_km."""
    return travel_time(d_km, vs) - travel_time(d_km, vp)


# %% [markdown]
# ## Step 3: from a measured gap back to a distance
# Turn the formula around: d = gap * vp * vs / (vp - vs). With vp = 6.0 and vs = 3.5 each second
# of gap is worth 6.0 * 3.5 / 2.5 = 8.4 km. This is the "lightning and thunder" rule for earthquakes.

# %%
def km_per_second(vp=VP, vs=VS):
    """Distance (km) corresponding to one second of S-P gap."""
    return vp * vs / (vp - vs)


def distance_from_gap(gap_s, vp=VP, vs=VS):
    """Distance (km) to the quake from the S-P gap (s)."""
    return np.asarray(gap_s, dtype=float) * km_per_second(vp, vs)


# %% [markdown]
# ## Step 4: a synthetic seismogram
# We draw a made-up record: quiet, then a P wiggle, then a bigger S wiggle. This is invented
# data for learning, not a real recording.

# %%
def synthetic_trace(d_km, t_end=60.0, dt=0.05, seed=1):
    """Return (t, trace) for a made-up seismogram at distance d_km."""
    rng = np.random.default_rng(seed)
    t = np.arange(0.0, t_end, dt)
    tr = 0.03 * rng.standard_normal(t.size)
    for arrival, amp, freq in ((float(travel_time(d_km, VP)), 0.5, 1.5), (float(travel_time(d_km, VS)), 1.0, 0.8)):
        k = t >= arrival
        tr[k] += amp * np.exp(-(t[k] - arrival) / 5.0) * np.sin(2 * np.pi * freq * (t[k] - arrival))
    return t, tr


# %% [markdown]
# ## Step 5: see it
# Left: the synthetic seismogram at 100 km with the P and S arrivals marked. Right: the gap
# grows in a straight line with distance, so a measured gap reads off a distance.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    d = 100.0
    tp, ts = float(travel_time(d, VP)), float(travel_time(d, VS))
    print(f"distance {d:.0f} km: P at {tp:.2f} s, S at {ts:.2f} s, gap {ts - tp:.2f} s")
    print(f"each second of gap is worth {km_per_second():.1f} km; gap {ts - tp:.2f} s -> {float(distance_from_gap(ts - tp)):.1f} km")

    t, tr = synthetic_trace(d)
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.plot(t, tr, color="#264653", lw=0.9)
    ax.axvline(tp, color="#2a9d8f", ls="--")
    ax.axvline(ts, color="#d9534f", ls="--")
    ax.annotate("P arrives", (tp, 0.85), color="#2a9d8f", ha="right")
    ax.annotate("S arrives", (ts, 0.85), color="#d9534f", ha="right")
    ax.set_xlabel("time since the quake (s)")
    ax.set_ylabel("ground motion (arbitrary units)")
    ax.set_title(f"Synthetic seismogram, station 100 km away: S-P gap {ts - tp:.1f} s")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "seismogram.png", dpi=120)

    dd = np.linspace(0, 300, 61)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(dd, sp_gap(dd), color="#e76f51", label="S-P gap (vp 6.0, vs 3.5 km/s)")
    ax2.plot(dd, sp_gap(dd, 6.0, 4.0), color="#8d99ae", ls="--", label="if vs were 4.0 km/s")
    ax2.plot([d], [ts - tp], "ko")
    ax2.set_xlabel("distance to the quake (km)")
    ax2.set_ylabel("S-P gap (s)")
    ax2.set_title("The gap grows in a straight line with distance")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "gap_vs_distance.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the checkpoint.
