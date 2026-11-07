# Activity sheet: openpinn, Session 1: A flexible curve that can also obey a law

Name: ____________________   Date: ____________

**Objectives**

- Explain how a network output is a weighted sum of smooth bumps, and why more bumps make the curve more flexible.
- Fit that curve to six noisy readings by least squares and see where it goes wrong between and beyond the readings.
- Add a physics law as extra rows in the same fit and measure the improvement over the whole range.
- Describe the trade-off in the strength of the law and in the number of bumps.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Fit 12 bumps to the six readings, first with the data only and then with the law (lam = 1). Compare the rms error against exp(-x) over x from 0 to 2, and the largest value of |u' + u|.

1. ______________________________  (hint: The readings are y = exp(-x) + noise at x = 0, 0.2, ..., 1.0. For exam...)
2. ______________________________  (hint: Data only: 13 weights (12 bumps and the constant) must fit 6 numbers, ...)
3. ______________________________  (hint: With the law (21 law rows on 0 to 2, lam = 1): the rms error drops bel...)
4. ______________________________  (hint: The largest |u' + u| is above 2 without the law and below 0.03 with it...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can a curve that passes within 0.05 of all six readings still be a poor prediction for the second minute?

Answer: ______________________________________________


**B. Numerical.** A candidate curve is u = exp(-0.9 x). Compute the law residual u' + u at x = 1. Is the candidate a solution of u' = -u?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the app, with 6 units, compare the red and green curves at x = 2. What does the difference tell you, and what is the error with the law on?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you can afford 6 units at most and want the rms error below 0.01. Choose the law weight, and say what happens if it is too large or if you use only 3 units.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
