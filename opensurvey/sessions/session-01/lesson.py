"""Session 1 (Level 1): a level and a staff give the height difference between two points.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: height difference with a level and a staff
# **A. Real-world problem.** Before a road, a drain or a building platform is built, the
# surveyor must know how much higher or lower one point is than another. The tools are a
# *level* (a telescope that stays exactly horizontal) and a *staff* (a tall ruler held upright).
#
# **Plan.** (1) turn two staff readings into a height difference, (2) chain several set-ups
# into a levelling run down a slope, (3) check that the instrument height does not matter,
# (4) measure the distance along the run by pacing.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: backsight minus foresight
# The level is set up between two points A and B. The line of sight is horizontal, at some
# height HI above sea level (the collimation height). The staff on A reads `bs` (backsight),
# the staff on B reads `fs` (foresight). A *large* reading means the ground is *low*, because
# the staff is mostly below the line of sight. So
#
#     rise from A to B  =  bs - fs           (negative number = a fall)
#     RL of B           =  RL of A + (bs - fs)
#
# RL means *reduced level*: height above a chosen datum. Check by hand: bs = 1.525 m and
# fs = 2.310 m give bs - fs = -0.785 m, so B is 0.785 m lower than A.

# %%
def height_difference(bs, fs):
    """Rise (positive) or fall (negative) from the back point to the fore point, metres."""
    return bs - fs


def next_rl(rl_back, bs, fs):
    """Reduced level of the fore point."""
    return rl_back + height_difference(bs, fs)


# %% [markdown]
# ## Step 2: a levelling run down a slope
# One set-up only sees a short distance. To go further, we leave a staff on a *turning point*
# and move the level on. Here the ground falls 4 percent (4 m per 100 m) and we level from A
# to B, 90 m apart, with set-ups every 30 m. Each set-up has its own arbitrary instrument height.

# %%
RL_A = 100.0
SLOPE = 0.04                       # ground falls 4 m per 100 m
STATIONS = [0.0, 30.0, 60.0, 90.0]  # A, turning point 1, turning point 2, B  (metres along the run)
HI_LIST = [101.5, 100.0, 98.9]     # collimation height of each set-up (m); any value works


def ground_rl(x, rl0=RL_A, slope=SLOPE):
    """True reduced level of the ground at distance x along the run."""
    return rl0 - slope * np.asarray(x, dtype=float)


def staff_reading(hi, rl_ground):
    """What the telescope reads on a staff standing on ground at rl_ground."""
    return hi - rl_ground


def level_run(stations=STATIONS, hi_list=HI_LIST, rl0=RL_A, slope=SLOPE):
    """Simulate the run. Returns a list of (bs, fs) readings, one pair per set-up."""
    pairs = []
    for k, hi in enumerate(hi_list):
        back, fore = stations[k], stations[k + 1]
        pairs.append((float(staff_reading(hi, ground_rl(back, rl0, slope))),
                      float(staff_reading(hi, ground_rl(fore, rl0, slope)))))
    return pairs


def run_rls(pairs, rl0=RL_A):
    """Reduced level at A and after each set-up."""
    rls = [rl0]
    for bs, fs in pairs:
        rls.append(next_rl(rls[-1], bs, fs))
    return rls


# %% [markdown]
# ## Step 3: the instrument height cancels
# Raise the instrument by any amount: both readings shrink by that amount, so bs - fs does
# not change. That is why the level may stand anywhere between the two staffs.

# %%
def difference_for_hi(hi, rl_a, rl_b):
    """bs - fs for one set-up with collimation height hi, on ground at rl_a and rl_b."""
    return height_difference(staff_reading(hi, rl_a), staff_reading(hi, rl_b))


# %% [markdown]
# ## Step 4: distance by pacing
# Calibrate your pace: walk a known distance, count paces. Then distance = paces x pace length.
# Pacing is rough (a few percent), tape measuring is better, and Session 2 uses a total station.

# %%
def pace_length(known_distance, paces):
    """Average length of one pace, metres."""
    return known_distance / paces


def pace_distance(paces, pace_len):
    """Distance covered, metres."""
    return paces * pace_len


# %% [markdown]
# ## Step 5: see it
# Left: the ground, the three set-ups' lines of sight and the staffs. Right: the reduced level
# of the ground along the run, with the instrument-height test.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    pairs = level_run()
    rls = run_rls(pairs)
    for k, (bs, fs) in enumerate(pairs, 1):
        print(f"set-up {k}: bs {bs:.3f}  fs {fs:.3f}  bs-fs {bs - fs:+.3f}  RL after {rls[k]:.3f}")
    print(f"total fall A to B = {rls[0] - rls[-1]:.3f} m over {STATIONS[-1]:.0f} m")

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    xs = np.linspace(0, 90, 91)
    ax.plot(xs, ground_rl(xs), color="saddlebrown", lw=2, label="ground")
    for k, hi in enumerate(HI_LIST):
        a, b = STATIONS[k], STATIONS[k + 1]
        ax.plot([a, b], [hi, hi], "--", lw=1.2, label=f"line of sight {k + 1} (HI {hi:.1f} m)")
    for x in STATIONS:
        g = float(ground_rl(x))
        ax.plot([x, x], [g, g + 3.0], color="black", lw=3)
    ax.set_xlabel("distance along the run (m)")
    ax.set_ylabel("reduced level (m)")
    ax.set_title("A levelling run down a 4 percent slope: three set-ups")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "levelling_run.png", dpi=120)

    his = np.linspace(99.0, 103.0, 41)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(his, staff_reading(his, 100.0), label="backsight bs on A")
    ax2.plot(his, staff_reading(his, 98.8), label="foresight fs on B")
    ax2.plot(his, [difference_for_hi(h, 100.0, 98.8) for h in his], "k", lw=2, label="bs - fs")
    ax2.set_xlabel("instrument height HI (m)")
    ax2.set_ylabel("staff reading or difference (m)")
    ax2.set_title("The instrument height cancels: bs - fs = -1.2 m")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "height_cancels.png", dpi=120)

    pl = pace_length(20.0, 27)
    print(f"pace length from 20 m in 27 paces = {pl:.3f} m; 90 m is about {90 / pl:.0f} paces")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
