# Activity sheet: openarrhenius, Session 3: How sure are we about k where we did not measure?

Name: ____________________   Date: ____________

**Objectives**

- Compute the covariance of (ln A, Ea) from the regression and explain why they are strongly correlated.
- Draw a confidence band for ln k(T) and explain why it flares outside the data.
- Predict k at an unmeasured temperature with Monte Carlo and check it against the formula.
- Validate the whole method on synthetic data with a coverage test, and recognise two failure cases (narrow range, curved plot).

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Nine temperatures from 600 to 1000 K in steps of 50 K, synthetic data with 5 percent error, true A = 1e13 per s and Ea = 150 kJ/mol (seed 4). Fit, give Ea and ln A with errors and their correlation, and predict k at 2000 K with a 95 percent interval. Does it contain the truth?

1. ______________________________  (hint: x = 1000/T has mean 1.2841 (T = 778.7 K) and Sxx = 0.4113....)
2. ______________________________  (hint: The regression gives s = 0.0535 on 7 degrees of freedom; Ea = 149.43 +...)
3. ______________________________  (hint: At 2000 K, x = 0.5: se = s sqrt(1/9 + (0.5 - 1.2841)^2 / 0.4113) = 0.0...)
4. ______________________________  (hint: t for 7 degrees of freedom = 2.365, so the factor is exp(2.365 x 0.067...)
5. ______________________________  (hint: The true k(2000 K) = 1.209e9 per s lies inside the interval. Check ins...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the confidence band get wider outside the data, and why is it widest on the side of the extrapolation?

Answer: ______________________________________________


**B. Numerical.** With s = 0.0535, n = 9, xbar = 1.2841 and Sxx = 0.4113 find the standard error of ln k at 800 K (x = 1.25) by hand and the 95 percent factor with t = 2.365.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the right panel of the figure, the straight-line fit has a band that does not contain the truth at 2000 K. What number from the fit warns you that the straight line is wrong?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you can add measurements to the 600 to 1000 K data to get k(2000 K) with a factor of at most 1.15. What do you change first, the number of points or the range, and why? Test the cases in the app.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
