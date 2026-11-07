# Activity sheet: openregularity, Session 2: Burgers: steepening against smoothing

Name: ____________________   Date: ____________

**Objectives**

- Derive and check the no-friction shock time t* = 1/max(-u0').
- Use the exact Cole-Hopf solution to show that the viscous Burgers solution is smooth, and verify a spectral solver against it.
- Verify the energy equation dE/dt = -nu mean(u_x^2) numerically.
- Measure how the peak gradient and the needed resolution scale with nu.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For u0 = sin x without friction, find the shock time and the slope at x = pi at t = 0.9. Then check numerically that with nu = 0.04 the viscous slope stays finite, with its steepest value -10.78 at t = 1.7.

1. ______________________________  (hint: u0' = cos x, whose most negative value is -1 at x = pi, so t* = 1/1 = ...)
2. ______________________________  (hint: The slope at x = pi is u_x = -1/(1 - t), so at t = 0.9 it is -1/0.1 = ...)
3. ______________________________  (hint: With nu = 0.04 the exact Cole-Hopf slope at x = pi and t = 1.7 is -10....)
4. ______________________________  (hint: Check: the no-friction slope at t = 1.7 does not exist (shock formed a...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the viscous Burgers solution stay smooth although the no-friction solution forms a shock?

Answer: ______________________________________________


**B. Numerical.** For u0 = 2 sin x without friction, find the shock time. How does it compare with u0 = sin x?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the slope plot, which curve runs to minus infinity, and what does the viscous curve do for nu = 0.04? About when is it steepest?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a simulation of nu = 0.02 must have its peak gradient accurate to 1 percent. Using the convergence study, which power-of-two number of grid points do you need, what happens with half as many, and what about nu = 0.01?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
