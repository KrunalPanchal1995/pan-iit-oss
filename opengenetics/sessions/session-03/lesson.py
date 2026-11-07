"""Session 3 (Level 3): Wright-Fisher simulation of drift, selection and mutation.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulating a population, drift versus selection
# **A. Real-world problem.** In a small population an allele can vanish or take over purely
# by chance, even if it is helpful. In a big population the same allele is steadily favoured.
# How small is "too small", and how much heterozygosity (genetic variety) does a population
# keep over time? That question matters for conservation planning.
#
# *General education using an idealised model. It is not a tool for real conservation
# decisions, and says nothing about any person.*
#
# **Plan.** (1) the Wright-Fisher model, (2) drift and the loss of heterozygosity,
# (3) fixation probability, (4) selection and mutation updates, (5) validation against
# Hardy-Weinberg and a closed form, (6) the failure case of a tiny population.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: one generation of the Wright-Fisher model
# N diploid individuals have 2N alleles. Random mating (selfing allowed) means each of the
# 2N alleles of the next generation is an independent draw: it is A with probability p. So
# the number of A alleles is Binomial(2N, p) and the new frequency is that count divided by 2N.
# A seeded generator makes every run repeatable. Passing an array of p values runs many
# populations at once.

# %%
def drift_step(p, N, rng):
    """Next-generation allele frequency of A after sampling 2N alleles (pure drift)."""
    return rng.binomial(2 * N, p) / (2 * N)


def heterozygosity(p):
    """Expected fraction of heterozygotes 2pq under Hardy-Weinberg proportions."""
    return 2 * p * (1 - p)


def simulate_paths(N, p0, generations, runs, seed=1, s=0.0, h=0.5, mu=0.0, nu=0.0):
    """Return an array (generations + 1, runs) of allele frequencies.

    Each generation: selection, then mutation, then random sampling (drift).
    """
    rng = np.random.default_rng(seed)
    p = np.full(runs, float(p0))
    paths = [p.copy()]
    for _ in range(generations):
        p = selection_step(p, s, h)
        p = mutation_step(p, mu, nu)
        p = drift_step(p, N, rng)
        paths.append(p.copy())
    return np.array(paths)


# %% [markdown]
# ## Step 2: selection and mutation (deterministic updates)
# Fitness of the genotypes AA, Aa, aa is 1 + s, 1 + h s, 1. The mean fitness is
# wbar = p^2 (1 + s) + 2 p q (1 + h s) + q^2, and after selection
#
#     p' = [ p^2 (1 + s) + p q (1 + h s) ] / wbar
#
# * h = 1/2: each A allele adds s/2 (additive); h = 1: A is dominant; h = 0: A is recessive.
# * Simple haploid-like advantage (one allele copy per individual):
#       p' = p (1 + s) / (1 + s p)
#   Its closed form is logit(p_t) = logit(p_0) + t ln(1 + s), with logit(p) = ln(p / (1 - p)).
#
# Mutation as a small constant flow: A becomes a at rate mu, a becomes A at rate nu:
#
#     p' = p (1 - mu) + (1 - p) nu        equilibrium p* = nu / (mu + nu)

# %%
def selection_step(p, s, h=0.5):
    """Diploid selection with fitness AA = 1 + s, Aa = 1 + h s, aa = 1."""
    q = 1 - p
    wbar = p * p * (1 + s) + 2 * p * q * (1 + h * s) + q * q
    return (p * p * (1 + s) + p * q * (1 + h * s)) / wbar


def haploid_selection_step(p, s):
    return p * (1 + s) / (1 + s * p)


def haploid_closed_form(p0, s, t):
    """p after t generations of haploid-like selection, from the logit formula."""
    z = np.log(p0 / (1 - p0)) + t * np.log(1 + s)
    return 1 / (1 + np.exp(-z))


def mutation_step(p, mu, nu):
    return p * (1 - mu) + (1 - p) * nu


# %% [markdown]
# ## Step 3: what to expect, and how to check it
# * Expected heterozygosity decays by a factor (1 - 1/(2N)) every generation of pure drift:
#   E[H_t] = H_0 (1 - 1/(2N))^t.
# * For a neutral allele the chance it eventually takes over (fixes) equals its starting
#   frequency p_0.
# * With a huge N and no selection, genotype frequencies stay at p^2 : 2pq : q^2.

# %%
def expected_heterozygosity(H0, N, t):
    return H0 * (1 - 1 / (2 * N)) ** t


def fixation_fraction(N, p0, runs, generations, seed=1, s=0.0, h=0.5):
    """Fraction of runs where A reaches frequency 1 (and the fraction where it is lost)."""
    last = simulate_paths(N, p0, generations, runs, seed, s=s, h=h)[-1]
    return float(np.mean(last == 1.0)), float(np.mean(last == 0.0))


def random_mating_genotypes(N, p, rng):
    """Draw N children from Hardy-Weinberg proportions; return the genotype fractions (AA, Aa, aa)."""
    q = 1 - p
    return rng.multinomial(N, [p * p, 2 * p * q, q * q]) / N


def min_population_for_heterozygosity(keep, generations):
    """Smallest N with (1 - 1/(2N))^generations >= keep (mini-project)."""
    N = 1
    while (1 - 1 / (2 * N)) ** generations < keep:
        N += 1
    return N


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    gens = 100

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
    for ax, N in zip(axes, (10, 100, 1000)):
        paths = simulate_paths(N, 0.5, gens, 20)
        ax.plot(paths, lw=0.8)
        ax.set_title(f"N = {N}")
        ax.set_xlabel("generation")
        ax.grid(alpha=0.3)
        print(f"N={N}: after {gens} generations the spread (std) of p is {paths[-1].std():.3f}")
    axes[0].set_ylabel("allele frequency p of A")
    fig.suptitle("Genetic drift: 20 populations each, starting at p = 0.5", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "drift_paths.png", dpi=120)

    N, t = 20, 20
    paths = simulate_paths(N, 0.5, t, 20000)
    Hs = heterozygosity(paths).mean(axis=1)
    print(f"mean H after {t} generations (N={N}): simulated {Hs[-1]:.4f}, formula {expected_heterozygosity(0.5, N, t):.4f}")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(Hs, "o", ms=3, label="simulated mean (20000 runs)")
    ax2.plot([expected_heterozygosity(0.5, N, g) for g in range(t + 1)], "-", label="H0 (1 - 1/(2N))^t")
    ax2.set_xlabel("generation")
    ax2.set_ylabel("mean heterozygosity 2pq")
    ax2.set_title("Heterozygosity decay, N = 20")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "heterozygosity_decay.png", dpi=120)

    fix, lost = fixation_fraction(10, 0.3, 4000, 400)
    print(f"neutral, N=10, p0=0.3: fixed {fix:.3f}, lost {lost:.3f} (theory: fixed 0.3)")

    # selection versus drift
    s = 0.05
    fig3, axes3 = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True)
    for ax, N in zip(axes3, (10, 5000)):
        paths = simulate_paths(N, 0.05, 200, 30, s=s, h=0.5)
        ax.plot(paths, lw=0.7, alpha=0.7)
        det = [0.05]
        for _ in range(200):
            det.append(selection_step(det[-1], s, 0.5))
        ax.plot(det, "k--", lw=2, label="deterministic")
        ax.set_title(f"N = {N}, s = {s}")
        ax.set_xlabel("generation")
        ax.grid(alpha=0.3)
        ax.legend()
        fx, ls = fixation_fraction(N, 0.05, 1000, 600, s=s)
        print(f"N={N}, s={s}, p0=0.05: fixed {fx:.3f}, lost {ls:.3f}")
    axes3[0].set_ylabel("allele frequency p of A")
    fig3.suptitle("A beneficial allele (additive): lost by chance in a tiny population", fontsize=10)
    fig3.tight_layout()
    fig3.savefig(OUT / "selection_vs_drift.png", dpi=120)

    print("smallest N keeping 90% heterozygosity for 50 generations:", min_population_for_heterozygosity(0.9, 50))

# %% [markdown]
# ## Where this stops
# The model has a constant population size, equal sexes, no migration or population structure.
# Real populations are messier, so treat N here as an "effective" size and the answers as rough.
