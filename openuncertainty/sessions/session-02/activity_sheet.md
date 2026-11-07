# Activity sheet: openuncertainty, Session 2: The propagation formula and the error budget

Name: ____________________   Date: ____________

**Objectives**

- Use the standard deviation and the standard error of the mean s / sqrt(n) of repeated readings.
- Propagate uncertainty through f(x, y) with the first-order formula and check it by Monte Carlo.
- Apply the special cases for sums, products and powers, and the reporting rule of one significant figure.
- Build an error budget (variance shares) and use it to decide which measurement to improve.
- Explain how a shared calibration error (correlation) changes the answer.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For L = 1.000 +- 0.005 m and T = 2.007 +- 0.010 s, find g, its uncertainty, the variance shares of L and T, and the reported value.

1. ______________________________  (hint: g = 4 pi^2 * 1.000 / 2.007^2 = 9.801 m/s^2....)
2. ______________________________  (hint: Relative uncertainty of L: 0.005 / 1.000 = 0.50 percent. Of T: 0.010 /...)
3. ______________________________  (hint: Combine in quadrature: sqrt(0.50^2 + 0.995^2) = 1.115 percent, so u_g ...)
4. ______________________________  (hint: Variance shares: L gives 0.25 / 1.24 = 20 percent and T gives 80 perce...)
5. ______________________________  (hint: One significant figure of uncertainty: 0.109 rounds to 0.1, so the val...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do we add uncertainties in quadrature (square, add, square root) instead of adding them directly? When would adding them directly be right?

Answer: ______________________________________________


**B. Numerical.** A pendulum has L = 0.500 +- 0.002 m and T = 1.419 +- 0.005 s. Find g and its uncertainty, and say which input dominates.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the correlation figure, read the uncertainty of x - y and of x + y at rho = 0.9 for two inputs with u = 0.1 cm. What does a shared calibration error do?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the target is a relative uncertainty of g of 0.6 percent or less. The stopwatch error for one swing is 0.1 s, so timing n swings and dividing gives u_T = 0.1 / n s. Choose n and the ruler error to meet the target. Is improving only the ruler enough?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
