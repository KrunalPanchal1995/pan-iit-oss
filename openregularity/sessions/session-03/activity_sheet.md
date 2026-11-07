# Activity sheet: openregularity, Session 3: 2-D flow, 3-D vortex stretching, and numerical blow-up

Name: ____________________   Date: ____________

**Objectives**

- Solve 2-D incompressible Navier-Stokes in vorticity form with a pseudo-spectral method and check it against the exact Taylor-Green decay.
- Verify numerically the energy and enstrophy balances, and that 2-D enstrophy cannot grow.
- Evaluate the 3-D vortex stretching term on a given field and explain why it is absent in 2-D, while stating that the 3-D problem is open.
- Recognise a numerical blow-up as a possible artefact, and remove it by adding resolution.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Check the Taylor-Green solution with nu = 0.05 and k = 1 at t = 2: predict the maximum vorticity and the energy ratio E(2)/E(0), then compare with the solver.

1. ______________________________  (hint: w0 = 2 sin x sin y has maximum 2. The exact decay factor is exp(-2 nu ...)
2. ______________________________  (hint: So the maximum vorticity at t = 2 is 2 * 0.8187 = 1.637 (1/time)....)
3. ______________________________  (hint: Energy decays like exp(-4 nu t) = exp(-0.4) = 0.670, starting from E(0...)
4. ______________________________  (hint: The solver on a 32 by 32 grid gives the same maximum and ratio; the la...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does 2-D vorticity have no stretching, and why does that help the regularity question there? Does this settle 3-D?

Answer: ______________________________________________


**B. Numerical.** For the Taylor-Green flow with k = 2, nu = 0.05, find the initial enstrophy and the decay factor of the vorticity at t = 0.5.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the random 2-D run (nu = 0.01), the enstrophy drops from 0.356 to 0.185. What fraction is left, and what would a rise of the curve indicate?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you simulate Burgers with nu = 0.01 and see the solution overflow on a 32-point grid without dealiasing. List what you would change, in order, before claiming anything about singularities, and say what evidence would be convincing.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
