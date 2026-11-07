# Roadmap: the path to the opengenetics Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Selfing and inbreeding

**You will learn:** How self-fertilisation halves the heterozygous fraction each generation.

**You will build:** A simulator of repeated selfing starting from one Aa individual.

**Checkpoint (not met by the shipped code):** After 5 generations of selfing the heterozygous fraction is 1/32 = 0.03125 (the shipped code has no selfing or inbreeding).

**Difficulty:** intermediate

## Session 5: Unequal sex ratio and effective size

**You will learn:** Why 30 males and 70 females drift like a smaller population, with effective size 4 Nm Nf / (Nm + Nf).

**You will build:** A Wright-Fisher model with separate sexes.

**Checkpoint (not met by the shipped code):** 30 males and 70 females keep 0.742 of heterozygosity over 50 generations (effective size 84), not 0.778 as the shipped code gives for N = 100.

**Difficulty:** intermediate

## Session 6: Linked genes and recombination

**You will learn:** Why genes close together on a chromosome are not inherited independently.

**You will build:** A two-gene gamete simulator with a recombination fraction.

**Checkpoint (not met by the shipped code):** With recombination fraction 0.1 the gametes AB and ab each appear in 0.45 of cases and Ab and aB in 0.05 (the shipped dihybrid cross assumes 0.25 each).

**Difficulty:** advanced

## Session 7: Heterozygote advantage

**You will learn:** How selection can hold two alleles in balance instead of fixing one.

**You will build:** Selection with fitness AA 0.8, Aa 1, aa 0.6 and drift in a large population.

**Checkpoint (not met by the shipped code):** The frequency of A settles at t/(s + t) = 0.667 for s = 0.2 and t = 0.4 (the shipped selection formula has no heterozygote advantage and sends a favoured allele to 0 or 1).

**Difficulty:** advanced

## Session 8: Reproduce the Target

**You will learn:** Animation of a Punnett square beside selection-versus-drift paths.

**You will build:** A three-panel animation like the Target, from your own code.

**Checkpoint (not met by the shipped code):** Forty populations of N = 40 starting at 0.1 with s = 0.1 show a different share of takeovers than with s = 0, and your plot reports both shares.

**Difficulty:** advanced

## The final step

Combine the milestones: a population simulator with separate sexes, selection, mutation and migration, an animated Punnett square, and a short write-up comparing selection with drift. If your result looks like the Target animation, open a pull request and tell us how you did it.
