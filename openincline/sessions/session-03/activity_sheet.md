# Activity sheet: openincline, Session 3: Simulating the block and validating it

Name: ____________________   Date: ____________

**Objectives**

- Build a time-stepping simulation with a stuck state and a sliding state.
- Validate it against two exact results: x = (1/2) a t^2 and the slide angle atan(mu_s).
- Estimate how an uncertainty in mu_s changes the slide angle.
- Compare a sliding block with a rolling cylinder using a = g sin t / (1 + I / (m r^2)).

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Simulate a block at a fixed 30 degrees with mu_s = 0.40 and mu_k = 0.30 for 2 s. Compare with the exact distance, then find how a 0.05 uncertainty in mu_s = 0.5 moves the slide angle.

1. ______________________________  (hint: tan 30 = 0.577 > 0.40, so the simulation switches to sliding immediate...)
2. ______________________________  (hint: Exact a = 9.81 * (sin 30 - 0.30 * cos 30) = 2.356 m/s^2, so exact x(2 ...)
3. ______________________________  (hint: The simulation with dt = 0.001 s gives the same x(t) to within 1e-6 m ...)
4. ______________________________  (hint: Tilting test with mu_s = 0.5: the simulation slips at 26.566 degrees a...)
5. ______________________________  (hint: Sensitivity: mu_s = 0.45 gives arctan 0.45 = 24.23 degrees and mu_s = ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the simulation need a 'stuck' state? What would go wrong if it always used kinetic friction?

Answer: ______________________________________________


**B. Numerical.** A block has mu_s = 0.30 with an uncertainty of +-0.03. Find the range of its slide angle. Compare with the linear estimate.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the slow-tilt figure the block does not move until about 53 s. Why 53 s? What would you see if the tilt rate were doubled to 1 degree per second?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a 2 m ramp at 20 degrees must deliver a rolling barrel to the bottom in at least 1.5 s so that the barrel does not hit the stop too hard. Compare a solid cylinder (k = 0.5) and a hollow tube (k = 1.0). Which satisfies the limit, and what friction coefficient is needed to avoid slipping?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
