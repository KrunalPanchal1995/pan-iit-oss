"""Session 2 (Level 2): probability rules, allele frequencies, Hardy-Weinberg, chi-square.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the mathematics of inheritance in a population
# **A. Real-world problem.** A recessive trait appears in about 1 birth in 10,000. How many
# people quietly carry one copy of the allele without showing the trait? The answer comes from
# the same multiplication and addition rules as coin flips, applied to alleles.
#
# *General education only, in an idealised textbook model. It says nothing about any real
# person or family and is not medical or genetic advice.*
#
# **Plan.** (1) probability rules for alleles, (2) allele frequencies p and q and
# Hardy-Weinberg proportions, (3) a chi-square test of a 3:1 ratio, (4) two genes at once
# (9:3:3:1).

# %%
import itertools
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
CHI2_CRIT_1DF_5PC = 3.84      # standard table value: 1 degree of freedom, 5 percent level


# %% [markdown]
# ## Step 1: the same rules as coin flips
# * Multiplication rule (independent events, "and"): P(both) = P(first) x P(second).
# * Addition rule (exclusive events, "or"): P(either) = P(first) + P(second).
#
# Aa x Aa: each parent passes a with probability 1/2, so P(aa) = 1/2 x 1/2 = 1/4.
# A carrier child (Aa) can happen two ways, A from parent 1 and a from parent 2, or the
# other way round: P(Aa) = 1/4 + 1/4 = 1/2.

# %%
def child_probabilities(pa1, pa2):
    """Genotype probabilities of a child when parent 1 passes A with probability pa1 and parent 2 with pa2."""
    qa1, qa2 = 1 - pa1, 1 - pa2
    return {"AA": pa1 * pa2, "Aa": pa1 * qa2 + qa1 * pa2, "aa": qa1 * qa2}


def passes_A(genotype):
    """Probability that a parent of this genotype passes on allele A."""
    return genotype.count("A") / 2


# %% [markdown]
# ## Step 2: allele frequencies and Hardy-Weinberg
# In a population, let p = fraction of all alleles that are A and q = fraction that are a,
# so p + q = 1. With random mating, no selection, no migration, no mutation and a large
# population, the genotype proportions in the next generation are
#
#     AA : p^2      Aa : 2pq      aa : q^2        (they add to (p + q)^2 = 1)
#
# Worked example: a recessive trait in 1 birth in 10,000 means q^2 = 0.0001, so q = 0.01,
# p = 0.99 and the carrier proportion is 2pq = 0.0198 (about 1 person in 50).

# %%
def hardy_weinberg(q):
    p = 1 - q
    return {"AA": p * p, "Aa": 2 * p * q, "aa": q * q}


def q_from_recessive_rate(rate):
    """The allele frequency q when the recessive appearance has frequency rate = q^2."""
    return float(np.sqrt(rate))


def allele_freq_from_counts(n_AA, n_Aa, n_aa):
    """Estimate q from genotype counts: each aa has two a alleles, each Aa has one."""
    total_alleles = 2 * (n_AA + n_Aa + n_aa)
    return (2 * n_aa + n_Aa) / total_alleles


# %% [markdown]
# ## Step 3: is the 3:1 ratio believable? (chi-square)
# Real counts never match 3:1 exactly. The chi-square statistic measures the mismatch:
#
#     chi2 = sum over categories of (observed - expected)^2 / expected
#
# With two categories (1 degree of freedom) a value above 3.84 would happen by chance less
# than 5 percent of the time if the true ratio really were 3:1, so we then doubt 3:1.

# %%
def chi_square(observed, expected):
    observed, expected = np.asarray(observed, float), np.asarray(expected, float)
    return float(np.sum((observed - expected) ** 2 / expected))


def chi_square_3_to_1(n_dominant, n_recessive):
    n = n_dominant + n_recessive
    return chi_square([n_dominant, n_recessive], [0.75 * n, 0.25 * n])


def consistent_with_3_to_1(n_dominant, n_recessive):
    return chi_square_3_to_1(n_dominant, n_recessive) < CHI2_CRIT_1DF_5PC


def acceptable_recessive_counts(n):
    """All recessive counts k out of n children for which the 3:1 ratio is NOT rejected."""
    return [k for k in range(n + 1) if consistent_with_3_to_1(n - k, k)]


# %% [markdown]
# ## Step 4: two genes at once (dihybrid cross)
# For two genes inherited independently, multiply: AaBb x AaBb gives appearance
# 9 (both dominant) : 3 : 3 : 1 (both recessive), because (3/4 : 1/4) x (3/4 : 1/4).

# %%
def dihybrid_counts():
    """Count the 16 equally likely combinations of AaBb x AaBb by appearance."""
    counts = {"A_B_": 0, "A_bb": 0, "aaB_": 0, "aabb": 0}
    for a1, b1, a2, b2 in itertools.product("Aa", "Bb", "Aa", "Bb"):
        first = "A_" if "A" in (a1, a2) else "aa"
        second = "B_" if "B" in (b1, b2) else "bb"
        counts[first + second] += 1
    return counts


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    qs = np.linspace(0, 1, 201)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(qs, (1 - qs) ** 2, label="AA = p^2")
    ax.plot(qs, 2 * qs * (1 - qs), label="Aa = 2pq (carriers)")
    ax.plot(qs, qs ** 2, label="aa = q^2")
    ax.set_xlabel("allele frequency q of the recessive allele a")
    ax.set_ylabel("genotype proportion in the next generation")
    ax.set_title("Hardy-Weinberg proportions")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "hardy_weinberg.png", dpi=120)

    q = q_from_recessive_rate(1e-4)
    hw = hardy_weinberg(q)
    print(f"1 in 10000: q = {q:.4f}, p = {1 - q:.4f}, carriers 2pq = {hw['Aa']:.4f} (about 1 in {1 / hw['Aa']:.0f})")
    print("estimate of q from 640/320/40:", allele_freq_from_counts(640, 320, 40))
    for nd, nr in [(740, 260), (800, 200)]:
        print(f"{nd}:{nr} -> chi2 = {chi_square_3_to_1(nd, nr):.3f}, consistent with 3:1: {consistent_with_3_to_1(nd, nr)}")
    ok = acceptable_recessive_counts(100)
    print("of 100 children, 3:1 is not rejected for recessive counts", ok[0], "to", ok[-1])
    print("dihybrid:", dihybrid_counts())

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ks = np.arange(0, 101)
    ax2.plot(ks, [chi_square_3_to_1(100 - k, k) for k in ks], label="chi-square")
    ax2.axhline(CHI2_CRIT_1DF_5PC, color="r", ls="--", label="critical value 3.84")
    ax2.axvspan(ok[0], ok[-1], color="g", alpha=0.15, label="3:1 not rejected")
    ax2.set_ylim(0, 20)
    ax2.set_xlim(0, 60)
    ax2.set_xlabel("recessive children out of 100")
    ax2.set_ylabel("chi-square statistic")
    ax2.set_title("How far from 25 recessive children is too far?")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "chi_square_100.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Hardy-Weinberg is a null model: real populations are finite, mutate, and are selected.
# Session 3 simulates exactly those departures.
