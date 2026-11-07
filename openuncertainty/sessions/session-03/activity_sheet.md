# Activity sheet: openuncertainty, Session 3: Monte Carlo propagation and where linear fails

Name: ____________________   Date: ____________

**Objectives**

- Propagate uncertainty by Monte Carlo (seeded, N = 100000) and read a 95 percent interval from percentiles.
- Compute a derivative by central differences and choose the step size.
- Combine uncertainties the GUM way, including a uniform resolution term LSB / sqrt(12), and report with k = 2.
- Show that the linear formula fails for a ratio with a large denominator error and at a maximum, and explain why.
- Build and report an error budget for a measured density.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
x = 10.0 +- 0.5 and y = 5.0 +- 1.5 (a 30 percent error). Find x / y with the linear formula and with Monte Carlo, and say whether the linear 95 percent interval is trustworthy.

1. ______________________________  (hint: x / y = 10.0 / 5.0 = 2.0. Relative errors: 0.5 / 10 = 5 percent and 1....)
2. ______________________________  (hint: Linear: u = 2.0 * sqrt(0.05^2 + 0.30^2) = 2.0 * 0.304 = 0.61. The 95 p...)
3. ______________________________  (hint: Monte Carlo: draw 100000 pairs, divide, take the 2.5th and 97.5th perc...)
4. ______________________________  (hint: The Monte Carlo interval is lopsided: 0.76 below 2.0 but 2.85 above. S...)
5. ______________________________  (hint: The linear interval holds only about 89 percent of the outcomes instea...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the linear formula fail for a ratio when the denominator has a large relative error, and why is the true interval skewed to the right?

Answer: ______________________________________________


**B. Numerical.** A digital caliper shows steps of 0.1 mm. Find the standard uncertainty from the resolution and the expanded uncertainty with k = 2.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the first figure, estimate by eye where the upper 95 percent end is for the histogram and for the Gaussian. What does the difference mean for a lab report?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for the ratio x / y with a 5 percent error in x, at which relative errors of y is the linear upper end within 5 percent of the Monte Carlo upper end? Test 10 percent and 30 percent.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
