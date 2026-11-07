"""Session 1 (Level 1): one gene, two alleles, and the Punnett square.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: genes in pairs and the Punnett square
# **A. Real-world problem.** Two parents each carry a pair of versions (alleles) of a gene.
# A child gets one allele from each parent. If both parents show the same trait, can a child
# still show a different one? A Punnett square lists every equally likely combination so
# you can count.
#
# *General education about inheritance in a simple textbook model. It is not medical or
# genetic advice about any person or family.*
#
# **Plan.** (1) alleles, genotype and appearance, (2) the Punnett square, (3) count the
# ratios, (4) check the counts with a seeded simulation.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: genotype and appearance
# Write the dominant allele as a capital letter (A) and the recessive allele as a small letter
# (a). A parent's *genotype* is a pair: AA, Aa or aa. The *phenotype* (appearance) is
# "dominant" if at least one A is present, and "recessive" only for aa.

# %%
def gametes(genotype):
    """The two alleles a parent can pass on, e.g. 'Aa' -> ['A', 'a'] (each passed with chance 1/2)."""
    return list(genotype)


def child_genotype(a1, a2):
    """Order the pair so that the capital letter comes first: ('a', 'A') -> 'Aa'."""
    return "".join(sorted([a1, a2]))


def punnett(parent1, parent2):
    """2 x 2 table of child genotypes: rows = alleles of parent 1, columns = alleles of parent 2."""
    return [[child_genotype(x, y) for y in gametes(parent2)] for x in gametes(parent1)]


def phenotype(genotype):
    return "dominant" if "A" in genotype else "recessive"


# %% [markdown]
# ## Step 2: count the four boxes
# Every box of the square is equally likely, so counting boxes gives the ratios.
# For Aa x Aa we expect genotypes AA : Aa : aa = 1 : 2 : 1 and appearance 3 : 1.

# %%
def genotype_counts(parent1, parent2):
    counts = {"AA": 0, "Aa": 0, "aa": 0}
    for row in punnett(parent1, parent2):
        for g in row:
            counts[g] += 1
    return counts


def phenotype_counts(parent1, parent2):
    counts = {"dominant": 0, "recessive": 0}
    for g, n in genotype_counts(parent1, parent2).items():
        counts[phenotype(g)] += n
    return counts


# %% [markdown]
# ## Step 3: simulate many children
# Each child gets one random allele from each parent. A seeded generator repeats exactly.
# The counts will be close to, but not exactly, 3 : 1.

# %%
def simulate_children(parent1, parent2, n, seed=1):
    """Return the number of children with the dominant and the recessive appearance."""
    rng = np.random.default_rng(seed)
    a1 = np.array(gametes(parent1))[rng.integers(0, 2, size=n)]
    a2 = np.array(gametes(parent2))[rng.integers(0, 2, size=n)]
    recessive = int(np.sum((a1 == "a") & (a2 == "a")))
    return {"dominant": n - recessive, "recessive": recessive}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
    for ax, (p1, p2) in zip(axes, [("Aa", "Aa"), ("AA", "aa"), ("Aa", "aa")]):
        table = punnett(p1, p2)
        for i in range(2):
            for j in range(2):
                g = table[i][j]
                ax.add_patch(plt.Rectangle((j, 1 - i), 1, 1, fc="#9ecae1" if phenotype(g) == "dominant" else "#fdae6b", ec="k"))
                ax.text(j + 0.5, 1.5 - i, g, ha="center", va="center", fontsize=16)
            ax.text(-0.15, 1.5 - i, gametes(p1)[i], ha="center", va="center", fontsize=14)
            ax.text(i + 0.5, 2.15, gametes(p2)[i], ha="center", va="center", fontsize=14)
        gc, pc = genotype_counts(p1, p2), phenotype_counts(p1, p2)
        ax.set_title(f"{p1} x {p2}\nAA:Aa:aa = {gc['AA']}:{gc['Aa']}:{gc['aa']}   dominant:recessive = {pc['dominant']}:{pc['recessive']}", fontsize=9)
        ax.set_xlim(-0.4, 2.1)
        ax.set_ylim(-0.1, 2.5)
        ax.set_aspect("equal")
        ax.axis("off")
        print(p1, "x", p2, "genotypes", gc, "appearance", pc)
    fig.suptitle("Punnett squares (blue = dominant appearance, orange = recessive appearance)", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "punnett_squares.png", dpi=120)

    sizes = [10, 100, 1000, 10000]
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    fracs = []
    for n in sizes:
        r = simulate_children("Aa", "Aa", n)
        fracs.append(r["recessive"] / n)
        print(f"{n:6d} children: dominant {r['dominant']}, recessive {r['recessive']}, fraction recessive {fracs[-1]:.3f}")
    ax2.semilogx(sizes, fracs, "o-", label="simulated fraction")
    ax2.axhline(0.25, color="r", ls="--", label="Punnett square: 1/4")
    ax2.set_xlabel("number of children simulated")
    ax2.set_ylabel("fraction with the recessive appearance")
    ax2.set_title("Aa x Aa: counts approach 1/4 as the family grows")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "recessive_fraction.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Real traits can have incomplete dominance, many genes and environment effects. This is the
# one-gene starting point. Session 2 adds the probability rules and whole populations.
