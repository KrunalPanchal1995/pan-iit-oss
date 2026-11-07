# Roadmap: the path to the openproteinmd Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: A stiffer backbone

**You will learn:** Bond-angle (bending) forces and why real chains are not perfectly flexible.

**You will build:** Add the bending energy k (1 - cos phi), with phi the angle between consecutive bond vectors, to the 12-bead chain with k = 1.0.

**Checkpoint (not met by the shipped code):** The hot chain (T = 0.8, dt = 0.01, 4 or more runs of 200 tau) has a mean radius of gyration of at least 2.3 sigma (the shipped flexible chain gives 2.09).

**Difficulty:** intermediate

## Session 5: Go 3D with a longer sequence

**You will learn:** Moving the same simulation to three dimensions and a 20-bead chain, with correct degrees of freedom (3 N).

**You will build:** A 3D chain of 20 beads, sequence PHPHHPPHPHHPPHPHHPHP, bending strength 0.5, cooled from T = 1.0 to 0.2 over 560 tau.

**Checkpoint (not met by the shipped code):** In 10 of 10 runs with different seeds the final radius of gyration is below 1.6 sigma, and the straight chain starts at 5.77 (the shipped code is 2D with 12 beads and cannot run this).

**Difficulty:** advanced

## Session 6: Error bars you can trust

**You will learn:** Block averaging, standard errors and why folding temperatures need uncertainty.

**You will build:** Extend the mini-project so that each temperature reports a mean Rg with a standard error.

**Checkpoint (not met by the shipped code):** The standard error of the mean Rg at T = 0.40 is below 0.03 sigma (the shipped 4-run average has a standard error of about 0.045).

**Difficulty:** intermediate

## Session 7: Compare with the exact lattice model

**You will learn:** The classic HP lattice model and exhaustive enumeration, as a check on the idea.

**You will build:** Enumerate every self-avoiding walk of 12 beads on a square lattice for HPHPPHHPHPPH and count H-H contacts.

**Checkpoint (not met by the shipped code):** Your enumeration finds 120292 walks of 11 steps (counting all four first steps) and a maximum of 5 H-H lattice contacts.

**Difficulty:** advanced

## The final step

Combine the milestones: a 3D chain with a stiff backbone, a longer sequence, error bars on every number and a check against the exact lattice model, cooled slowly and exported as an animation. If your result looks like the Target animation, open a pull request and tell us how you did it. Keep saying clearly that it is a toy model.
