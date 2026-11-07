"""Session 1 (Level 1): a fair test, and accurate versus precise.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a fair test, and accurate versus precise
# **A. Real-world problem.** You want to know whether a lid keeps a cup of hot water warmer.
# If you put the lid on a big cup and leave a small cup bare, you have changed two things
# at once, so you cannot tell which one mattered. And if you try it only once, luck decides.
#
# **Plan.** (1) a made-up cooling test where the true answer is known, (2) change one thing
# at a time, (3) repeat the test, (4) tell *accurate* (close to the truth) from *precise*
# (repeatable).

# %%
import math
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# --- the made-up world: how many degrees C a cup of water cools in 10 minutes -------------
BASE_DROP = 20.0     # small cup, no lid
LID_EFFECT = -1.0    # a lid changes the drop by this much (degrees C): the thing we want to find
BIG_EFFECT = -3.0    # a big cup also changes the drop (degrees C): a thing we must NOT mix in
NOISE_SD = 1.5       # run-to-run scatter of one measurement (degrees C)


# %% [markdown]
# ## Step 1: the world, and a test of it
# `expected_drop` is the truth with no scatter. `run_test` adds the scatter that every real
# measurement has (a random number generator stands in for the unavoidable small wobbles).

# %%
def expected_drop(lid, big):
    """True average cooling drop (degrees C). lid and big are 0 or 1."""
    return BASE_DROP + LID_EFFECT * lid + BIG_EFFECT * big


def run_test(lid, big, rng):
    """One measured drop: the truth plus random scatter."""
    return expected_drop(lid, big) + rng.normal(0.0, NOISE_SD)


# %% [markdown]
# ## Step 2: change one thing at a time
# An *unfair* test compares "lid on a big cup" with "no lid on a small cup": the lid and the
# cup size both change. A *fair* test compares the same cup with and without the lid.
# With no scatter at all you can already see the difference:
#
#     unfair: (20 - 1 - 3) - (20) = -4        fair: (20 - 1) - (20) = -1

# %%
def unfair_effect():
    """Apparent lid effect when the lid goes on the big cup and the bare cup is small."""
    return expected_drop(1, 1) - expected_drop(0, 0)


def fair_effect():
    """Lid effect when only the lid changes (same cup)."""
    return expected_drop(1, 0) - expected_drop(0, 0)


# %% [markdown]
# ## Step 3: do it more than once
# One run of each setting gives a wobbly answer. The *mean* of n runs wobbles less: its
# scatter is NOISE_SD / sqrt(n). `p_wrong_sign(n)` is the chance that a fair test with n
# runs per setting says the lid makes things *worse* (a positive difference) when it really
# helps. The difference of two means has scatter sqrt(2/n) * NOISE_SD (two independent means,
# so their variances add); the chance of a wrong sign is the normal tail beyond
# |effect| / that scatter.

# %%
def normal_tail(z):
    """P(Z > z) for a standard normal Z."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def p_wrong_sign(n):
    """Chance that a fair test with n runs per setting reports a positive (wrong-sign) lid effect."""
    scatter = NOISE_SD * math.sqrt(2.0 / n)
    return normal_tail(abs(LID_EFFECT) / scatter)


def simulate_wrong_sign(n, trials, seed):
    """Fraction of simulated fair tests (n runs per setting) whose measured effect is > 0."""
    rng = np.random.default_rng(seed)
    with_lid = expected_drop(1, 0) + rng.normal(0, NOISE_SD, (trials, n)).mean(axis=1)
    bare = expected_drop(0, 0) + rng.normal(0, NOISE_SD, (trials, n)).mean(axis=1)
    return float(np.mean(with_lid - bare > 0))


# %% [markdown]
# ## Step 4: accurate versus precise
# A thermometer reads a cup whose true temperature is 50.0 degrees C.
# *Accurate* = the readings average close to the truth (small **bias**, the average error).
# *Precise* = the readings agree with each other (small **scatter**, the standard deviation).
# These are different: a thermometer can be precise but wrong, or right on average but jumpy.

# %%
TRUE_TEMP = 50.0


def thermometer(bias, sd, n, seed, true=TRUE_TEMP):
    """n readings: truth + bias + random scatter."""
    rng = np.random.default_rng(seed)
    return true + bias + rng.normal(0.0, sd, n)


def describe(readings, true=TRUE_TEMP):
    """(mean error = bias estimate, scatter = standard deviation of the readings)."""
    r = np.asarray(readings, dtype=float)
    return float(r.mean() - true), float(r.std(ddof=1))


# four instruments: (bias, sd) in degrees C
INSTRUMENTS = {
    "accurate and precise": (0.0, 0.1),
    "accurate, not precise": (0.0, 1.0),
    "precise, not accurate": (2.0, 0.1),
    "neither": (2.0, 1.0),
}

# %% [markdown]
# ## Step 5: see it
# First figure: the four thermometers as target boards (each dot is one reading; the red cross
# is the truth). Second figure: how often a fair test gets the wrong sign, against the number
# of runs per setting n.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("unfair test says", unfair_effect(), "; fair test says", fair_effect(), "degrees C")
    for n in (1, 3, 9, 25):
        print(f"n = {n:2d} runs per setting: wrong-sign chance {p_wrong_sign(n):.3f}"
              f" (simulated {simulate_wrong_sign(n, 20000, 1):.3f})")

    fig, axs = plt.subplots(1, 4, figsize=(10, 2.8), sharey=True)
    for ax, (name, (b, s)) in zip(axs, INSTRUMENTS.items()):
        rng = np.random.default_rng(4)
        x = rng.normal(b, s, 25)
        y = rng.normal(b, s, 25)
        ax.scatter(x, y, s=12)
        ax.plot([0], [0], "r+", ms=14, mew=2)
        ax.set_xlim(-4, 4)
        ax.set_ylim(-4, 4)
        ax.set_aspect("equal")
        ax.set_title(name, fontsize=8)
        ax.set_xlabel("error left-right (degrees C)")
    axs[0].set_ylabel("error up-down (degrees C)")
    fig.suptitle("Target boards: red cross = truth, dots = readings (x, y are two independent error readings)", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "accurate_precise.png", dpi=120)

    ns = np.arange(1, 31)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(ns, [p_wrong_sign(int(k)) for k in ns], "o-", ms=3)
    ax2.set_xlabel("runs per setting, n")
    ax2.set_ylabel("chance the fair test gets the wrong sign")
    ax2.set_title("More repeats make the fair test trustworthy")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "wrong_sign_vs_n.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
