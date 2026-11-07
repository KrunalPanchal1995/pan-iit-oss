# Activity sheet: openportfolio, Session 2: Return, risk and correlation of two assets

Name: ____________________   Date: ____________

**Objectives**

- Measure the mean return and the risk (standard deviation) of a simulated asset.
- Use the two-asset formulas for expected return and variance, and verify them on sampled portfolios.
- Explain what correlation does: no benefit at +1, risk that can vanish at -1.
- Derive and check the minimum-variance weight, and solve a small design problem.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Put half the money in each asset (w = 0.5) with correlation rho = 0.3. Find the expected return, the variance and the risk, and check against a simulated portfolio of 100000 years.

1. ______________________________  (hint: Expected return = 0.5 * 0.10 + 0.5 * 0.06 = 0.08, that is 8 percent....)
2. ______________________________  (hint: Variance = 0.25 * 0.04 + 0.25 * 0.01 + 2 * 0.25 * 0.3 * 0.2 * 0.1 = 0....)
3. ______________________________  (hint: Risk = sqrt(0.0155) = 0.1245, that is 12.45 percent....)
4. ______________________________  (hint: Simulation (seed 7, 100000 years, correlation 0.3): the sampled portfo...)
5. ______________________________  (hint: Compare with the single assets: 20 percent and 10 percent. The mix has...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a correlation of +1 give no diversification benefit, while a correlation of -1 can remove the risk completely?

Answer: ______________________________________________


**B. Numerical.** Assets 1 and 2 are uncorrelated (rho = 0). Find the weight with the least risk, that risk, and the expected return there.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the first figure, at rho = 0.3 where is the minimum of the risk curve, and is it lower than the risk of the safer asset (10 percent)? What would happen at rho = 1?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you want an expected return of at least 8 percent and a risk of at most 11 percent from these two assets. What weight do you need and how low must the correlation be? Is rho = 0.3 enough? What can you do if not?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
