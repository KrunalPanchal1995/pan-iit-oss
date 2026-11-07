"""Session 1 (Level 1): fair outcomes and the sum of two dice.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: fair outcomes and the sum of two dice
# **A. Real-world problem.** In a board game you roll two dice and add them. Why does it feel
# as if 7 comes up more than 2 or 12? We list every equally likely outcome, count, and then
# check the count by rolling virtual dice.
#
# *Education about chance only. This is not betting advice.*
#
# **Plan.** (1) list the 36 outcomes, (2) count each sum, (3) draw the bar chart,
# (4) roll many times and watch the frequencies settle onto the exact values.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the sample space
# The *sample space* is the list of all things that can happen. For one fair die it is
# 1, 2, 3, 4, 5, 6 and each is equally likely, so P(any one face) = 1/6.
# For two dice, (first, second) is a pair, so there are 6 x 6 = 36 equally likely pairs.
# (1, 2) and (2, 1) are different pairs.

# %%
def sample_space(dice=2):
    """All equally likely outcomes of rolling `dice` fair dice, as a list of tuples."""
    outcomes = [()]
    for _ in range(dice):
        outcomes = [o + (face,) for o in outcomes for face in range(1, 7)]
    return outcomes


def sum_counts(dice=2):
    """Dictionary: sum -> number of outcomes that give that sum."""
    counts = {}
    for o in sample_space(dice):
        counts[sum(o)] = counts.get(sum(o), 0) + 1
    return counts


def sum_probabilities(dice=2):
    """Exact probability of each sum = favourable outcomes / all outcomes."""
    total = 6 ** dice
    return {s: c / total for s, c in sorted(sum_counts(dice).items())}


# %% [markdown]
# ## Step 2: simulate rolling
# A seeded random generator gives the same "random" rolls every run, so results can be checked.
# The fraction of rolls that gave each sum is the *relative frequency*.

# %%
def roll_sums(n, seed=1):
    """Sum of two dice for n simulated rolls."""
    rng = np.random.default_rng(seed)
    return rng.integers(1, 7, size=n) + rng.integers(1, 7, size=n)


def relative_frequencies(sums):
    """Fraction of the rolls that gave each sum 2..12 (array of 11 numbers)."""
    return np.array([(sums == s).mean() for s in range(2, 13)])


# %% [markdown]
# ## Step 3: see it
# Left: exact probabilities of each sum. Right: the frequency of a 7 as the number of rolls
# grows; it wobbles at first and then settles near 6/36 = 0.1667.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    counts = sum_counts()
    print("outcomes:", len(sample_space()), " counts by sum:", counts)
    print("P(7) =", counts[7], "/ 36 =", round(counts[7] / 36, 4))
    for n in (36, 1000, 100000):
        f = relative_frequencies(roll_sums(n))
        print(f"{n:6d} rolls: frequency of 7 = {f[5]:.4f}")

    sums = np.arange(2, 13)
    exact = np.array([sum_probabilities()[s] for s in sums])
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.bar(sums - 0.2, exact, width=0.4, label="exact (counting)")
    ax.bar(sums + 0.2, relative_frequencies(roll_sums(1000)), width=0.4, label="1000 simulated rolls")
    ax.set_xlabel("sum of two dice")
    ax.set_ylabel("probability (fraction of rolls)")
    ax.set_title("Seven is the most likely sum")
    ax.set_xticks(sums)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "dice_sums.png", dpi=120)

    s = roll_sums(20000)
    k = np.arange(1, len(s) + 1)
    running = np.cumsum(s == 7) / k
    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    ax2.semilogx(k, running, label="simulated frequency of a 7")
    ax2.axhline(1 / 6, color="red", ls="--", label="exact 6/36 = 0.1667")
    ax2.set_xlabel("number of rolls")
    ax2.set_ylabel("fraction of rolls that were a 7")
    ax2.set_title("The simulation settles onto the exact value")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "convergence.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
