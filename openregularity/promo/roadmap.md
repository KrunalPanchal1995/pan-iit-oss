# Roadmap: the path to the openregularity Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: A 3-D pseudo-spectral solver

**You will learn:** How the 3-D equations are time-stepped, with pressure projection and dealiasing, and what the cost per step is.

**You will build:** A 3-D periodic solver started from the 3-D Taylor-Green field.

**Checkpoint (not met by the shipped code):** The kinetic energy balance dE/dt = -nu mean(|w|^2) holds to 1e-3 relative error for t up to 1 at N = 32 (the shipped code only evaluates the 3-D stretching term at t = 0 and cannot step in time).

**Difficulty:** advanced

## Session 5: Track the maximum vorticity

**You will learn:** How to record max |w|(t) and its time integral, and compare candidate initial fields.

**You will build:** A study of max |w|(t) for two or three 3-D initial fields, with the Beale-Kato-Majda integral.

**Checkpoint (not met by the shipped code):** Curves of max |w|(t) from N = 32 and N = 64 agree within 1 percent up to t = 2 for one chosen field (the shipped code has no 3-D time stepping to produce them).

**Difficulty:** advanced

## Session 6: Read about Euler blow-up claims and computer-assisted proofs

**You will learn:** How researchers separate numerical evidence, rigorous computer-assisted proofs and open questions.

**You will build:** A one-page reading summary that labels every claim as proved, supported by numerical evidence, or open.

**Checkpoint (not met by the shipped code):** The summary never describes the 3-D Navier-Stokes smoothness problem as solved, and cites at least three sources you actually read.

**Difficulty:** intermediate

## Session 7: Higher-precision Cole-Hopf

**You will learn:** Why double precision fails for the exact solution at small viscosity, and how extended precision repairs it.

**You will build:** A high-precision version of the exact Burgers solution.

**Checkpoint (not met by the shipped code):** At nu = 0.01 and t = 1.5 it agrees with a converged N = 2048 spectral run to 1e-6 (the shipped double-precision formula is wrong by more than 1 already at nu = 0.02).

**Difficulty:** intermediate

## Session 8: A cheaper resolution

**You will learn:** Filters, adaptive or stretched grids that resolve a thin front with fewer points.

**You will build:** A variant of the Burgers solver that places points where the front is.

**Checkpoint (not met by the shipped code):** Peak gradient for nu = 0.01 within 1 percent of the converged value 48.4 using N = 256 or fewer points (the shipped solver needs N = 1024).

**Difficulty:** advanced

## The final step

Combine the milestones: a careful, honest numerical study of a 3-D flow with a resolution check, a precise statement of what the numbers do and do not show, and a clean animation like the Target. If your result looks like the Target animation, open a pull request and tell us how you did it. Remember that the 3-D Navier-Stokes smoothness problem is open; no simulation in this repo is a proof.
