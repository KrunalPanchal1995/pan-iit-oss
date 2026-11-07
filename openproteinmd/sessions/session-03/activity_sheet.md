# Activity sheet: openproteinmd, Session 3: A toy peptide folds: Langevin dynamics and validation

Name: ____________________   Date: ____________

**Objectives**

- Build a coarse-grained hydrophobic/polar (HP) bead chain and explain what its H-H attraction stands for.
- Run constant-temperature (Langevin) dynamics and watch the radius of gyration fall as the chain collapses.
- Validate the simulation with energy conservation (NVE) and the equipartition temperature.
- Measure how the folded state depends on temperature and on the time step, including a case that fails.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
(a) What is the radius of gyration of the straight 12-bead chain? (b) At T = 0.5, what mean kinetic energy should the thermostat produce for 12 beads in 2D, and what does the simulation give?

1. ______________________________  (hint: (a) Rg = sqrt((N^2 - 1) / 12) = sqrt(143 / 12) = sqrt(11.917) = 3.452 ...)
2. ______________________________  (hint: (b) Degrees of freedom: d N = 2 * 12 = 24 (the bath does not conserve ...)
3. ______________________________  (hint: Equipartition: mean KE = (1/2) * 24 * 0.5 = 6.0 epsilon....)
4. ______________________________  (hint: Run it: 20000 steps at T = 0.5 give a kinetic temperature of 0.508, so...)
5. ______________________________  (hint: Hand check of Rg on a simpler shape: four beads at the corners of a un...)

Final answer: ____________________

## Questions
**A. Conceptual.** The control chain PPPPPPPPPPPP never folds, even when cold, but HPHPPHHPHPPH does. What does that tell you about what causes the collapse in this model? And why does a correct equipartition temperature validate the thermostat but not the force field?

Answer: ______________________________________________


**B. Numerical.** A 12-bead chain in 2D is held at T = 0.6 by the Langevin bath. What mean kinetic energy do you expect? If a run reports a mean KE of 6.0, what is its kinetic temperature and what would you suspect?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the lesson table of mean Rg against T (1.70 at T = 0.35, 1.87 at T = 0.40), at what temperature does the curve cross the folded line 1.8? Is there a sharp transition?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you want to simulate 100 tau of the chain at T = 0.3, at the lowest computer cost, with an energy spread (max minus min of E divided by mean KE) below 5 percent in a constant-energy check. Choose dt from the lesson measurements and count the steps.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
