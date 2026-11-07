# Activity sheet: openexperiment, Session 3: Designing the experiment: order, replicates, factors and drift

Name: ____________________   Date: ____________

**Objectives**

- Show by simulation how a drifting sensor biases a naive run order, and compare random, blocked and ABBA orders.
- Compute the number of replicates for a given effect size, scatter and power, and verify it by Monte Carlo.
- Estimate main effects and an interaction from a 2x2 factorial design and see how one-factor-at-a-time fails.
- Choose a re-calibration interval and recognise the failure of extrapolating a nonlinear sensor.
- Run a two-factor calibration (temperature and supply voltage) and report effects, calibration and residual uncertainty.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Treatment B truly raises the response by 0.30 degrees C. The sensor drifts by 0.05 degrees C per run and one run has scatter 0.50. Twenty runs: 10 of A and 10 of B. (a) What bias does the all-A-then-all-B order have? (b) How many runs per group would detect a difference d = 0.5 with sigma = 1.0 at 5 percent significance and 80 percent power? (c) In the 2x2 system response = 50 + A + B + 6AB, what are the effects, and where does one-factor-at-a-time stop?

1. ______________________________  (hint: (a) Mean run number of A is 4.5, of B is 14.5: bias = 0.05 * (14.5 - 4...)
2. ______________________________  (hint: Noise alone gives scatter 0.50 * sqrt(2 / 10) = 0.2236; complete rando...)
3. ______________________________  (hint: (b) n = 2 * (1.96 + 0.8416)^2 * 1.0^2 / 0.5^2 = 2 * 7.849 / 0.25 = 62....)
4. ______________________________  (hint: (c) The four runs (-,-), (+,-), (-,+), (+,+) give 54, 44, 44, 58. A = ...)
5. ______________________________  (hint: One-factor-at-a-time starts at (-,-) = 54: raising A gives 44 (worse),...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does randomising the run order protect an experiment against drift you did not know about, while ABBA only protects against straight-line drift? What does randomisation cost?

Answer: ______________________________________________


**B. Numerical.** How many runs per group are needed to detect a difference d = 0.25 with sigma = 1.0 at 5 percent significance and 80 percent power? Compare with d = 0.5 (63 runs).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the interaction figure the two lines are not parallel. What does this say about the effect of factor A, and why does one-factor-at-a-time fail here?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: after calibration the offset uncertainty is 0.10 degrees C, the drift is 0.02 degrees C per day and the allowed error is 0.50 degrees C. How often must you recalibrate? What happens after 20 days? What if the tolerance were 0.10?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
