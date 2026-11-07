"""Session 1 (Level 1): people leave a room like water through a pipe; the door sets the pace.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: people flow through a door
# **A. Real-world problem.** A fire alarm rings during a college function. 240 people are
# in the hall and there is one exit door. How long until the last person is outside? Would
# a second door help, and by how much? Engineers answer this with a surprisingly simple
# idea: a crowd moving through a door behaves like a liquid flowing through a pipe.
#
# **Plan.** (1) flow = density x speed x width, (2) the effective width of a door,
# (3) the time to empty a room = waiting for the alarm + walking + queueing at the door,
# (4) what a second door or a wider door buys you.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

SPECIFIC_FLOW = 1.3     # persons per second per metre of effective width (typical peak value)
DOOR_EDGE = 0.15        # m lost at each side of a door (people keep away from the frame)
WALK_SPEED = 1.2        # m/s, an unhurried walk on a level floor


# %% [markdown]
# ## Step 1: a crowd is a flow
# Count how many people cross a line each second. That number is the **flow** F
# (persons per second). It depends on three things:
#
#     F = D x v x W
#
# D is the **density** (persons per square metre), v the walking speed (m/s) and W the width
# of the passage (m). Check the units: persons/m2 x m/s x m = persons/s. In a dense crowd of
# about 2 persons/m2 people shuffle at about 0.65 m/s, so every metre of width passes about
# 2 x 0.65 = 1.3 persons per second. This number, the **specific flow** Fs, is what makes
# hand calculations possible.

# %%
def crowd_flow(density, speed, width):
    """Flow F = D v W in persons per second (density in persons/m2, speed in m/s, width in m)."""
    if density < 0 or speed < 0 or width < 0:
        raise ValueError("density, speed and width cannot be negative")
    return density * speed * width


# %% [markdown]
# ## Step 2: the effective width of a door
# People do not brush against the door frame; they keep a small gap on each side. So the
# useful, **effective width** is the clear width minus about 0.15 m at each side:
#
#     We = W_clear - 2 x 0.15 m
#
# A 1.2 m door is effectively 0.9 m wide. Its maximum flow is Fs x We = 1.3 x 0.9 = 1.17
# persons per second.

# %%
def effective_width(clear_width, edge=DOOR_EDGE):
    """Effective width (m) = clear width minus the edge gap on both sides."""
    we = clear_width - 2.0 * edge
    if we <= 0:
        raise ValueError("the opening is narrower than the two edge gaps; no one can pass")
    return we


def door_flow(clear_width, n_doors=1, fs=SPECIFIC_FLOW):
    """Total flow (persons/s) through n identical doors running at the specific flow fs."""
    if n_doors < 1:
        raise ValueError("need at least one door")
    return n_doors * fs * effective_width(clear_width)


# %% [markdown]
# ## Step 3: the time to empty a room
# Three things add up:
#
#     t_evac = t_pre + L / v + N / F
#
# * t_pre, the **pre-movement time**: people hear the alarm, finish a sentence, pick up a bag.
# * L / v, the walking time of the first people to reach the door from distance L.
# * N / F, the **queue time**: N people pass a door that lets through F persons per second.
#
# This is the simplest form of the "hydraulic" method used by fire engineers. It assumes the
# door is the slowest part (the bottleneck) and that a queue forms there.

# %%
def walk_time(distance, speed=WALK_SPEED):
    """Time (s) to walk a distance (m) at a speed (m/s)."""
    if speed <= 0:
        raise ValueError("speed must be positive")
    return distance / speed


def evacuation_time(n_people, clear_width, n_doors=1, distance=20.0, t_pre=60.0,
                    speed=WALK_SPEED, fs=SPECIFIC_FLOW):
    """Time (s) until the last of n_people has passed the door(s)."""
    if n_people < 0:
        raise ValueError("number of people cannot be negative")
    return t_pre + walk_time(distance, speed) + n_people / door_flow(clear_width, n_doors, fs)


def people_left(t, n_people, clear_width, n_doors=1, distance=20.0, t_pre=60.0,
                speed=WALK_SPEED, fs=SPECIFIC_FLOW):
    """Number of people still inside at time(s) t (s): full until the first reach the door,
    then falling at the door flow until zero."""
    t = np.asarray(t, float)
    start = t_pre + walk_time(distance, speed)
    passed = door_flow(clear_width, n_doors, fs) * np.clip(t - start, 0.0, None)
    return np.clip(n_people - passed, 0.0, n_people)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"dense crowd: F = 2.0 x 0.65 x 1.0 = {crowd_flow(2.0, 0.65, 1.0):.2f} persons/s per metre")
    print(f"1.2 m door: effective width {effective_width(1.2):.2f} m, flow {door_flow(1.2):.2f} persons/s")

    # Figure 1: the hall empties: one door against two doors
    n, w = 240, 1.2
    t = np.linspace(0, 320, 641)
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    for k, col in [(1, "#d9534f"), (2, "#2a9d8f")]:
        te = evacuation_time(n, w, k)
        ax.plot(t, people_left(t, n, w, k), color=col, lw=2.2, label=f"{k} door(s): empty at {te:.0f} s")
        ax.axvline(te, color=col, ls=":", lw=1)
        print(f"{k} door(s) of {w} m: evacuation time {te:.1f} s ({te / 60:.1f} min)")
    ax.axvspan(0, 60, color="0.85", alpha=0.6)
    ax.text(30, 15, "waiting\n(pre-movement)", ha="center", fontsize=8)
    ax.set_xlabel("time after the alarm (s)")
    ax.set_ylabel("people still inside")
    ax.set_title("240 people leave a hall through 1.2 m doors")
    ax.set_xlim(0, 320)
    ax.set_ylim(0, 260)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "room_emptying.png", dpi=120)

    # Figure 2: wider doors help, with diminishing returns
    widths = np.arange(0.8, 2.45, 0.1)
    fig2, ax2 = plt.subplots(figsize=(6.6, 4.2))
    for k, col in [(1, "#d9534f"), (2, "#2a9d8f")]:
        ax2.plot(widths, [evacuation_time(n, x, k) for x in widths], "o-", color=col, ms=4, label=f"{k} door(s)")
    ax2.axhline(60 + walk_time(20.0), color="k", ls="--", lw=1)
    ax2.text(2.4, 60 + walk_time(20.0) + 8, "pre-movement + walking (no queue)", ha="right", fontsize=8)
    ax2.set_xlabel("clear width of each door (m)")
    ax2.set_ylabel("evacuation time (s)")
    ax2.set_title("240 people: evacuation time against door width")
    ax2.set_ylim(0, 600)
    ax2.legend(fontsize=9)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "door_width.png", dpi=120)

# %% [markdown]
# ## Where this stops
# We used one fixed number, 1.3 persons per second per metre. But people walk faster when the
# crowd is thin and slower when it is packed. Session 2 builds the speed-density law behind
# that number and finds where queues form inside a building.
