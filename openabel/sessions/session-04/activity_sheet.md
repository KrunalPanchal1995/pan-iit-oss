# Activity sheet: openabel, Session 4: No peeking at the truth: choosing the smoothing from the photo alone

Name: ____________________   Date: ____________

**Objectives**

- Estimate the noise size sigma from the photo alone, and check the estimate against the truth in a simulation.
- Compute three truth-free scores for the smoothing strength: the discrepancy principle, unbiased predictive risk (UPRE) and generalised cross-validation (GCV).
- Verify the leave-one-out shortcut by honest refitting, and verify that UPRE is unbiased by Monte Carlo.
- Explain why one lam chosen from all rows of a photo beats one lam per row.
- Say honestly how close a truth-free rule gets to the best possible choice, and why no rule can beat the noise.

## Before you start: predict
In your own words, what do you think will happen to the chosen smoothing strength when you raise the noise level in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For the height-8 row of the 3 percent candle photo (N = 40), the noise from all rows is sigma = 0.150 (sigma squared 0.0224, N sigma squared 0.896). With lam = 0.3, 3 and 15.8 the fit leaves rss = 0.596, 0.829 and 0.921 with df = 16.76, 10.11 and 7.27. Score the three values with all three rules.

1. ______________________________  (hint: UPRE = rss + 2 sigma^2 df - N sigma^2: 0.596 + 0.751 - 0.896 = 0.451 for lam = 0.3, then 0.386 for lam = 3 and 0.351 for lam = 15.8.)
2. ______________________________  (hint: GCV = N rss / (N - df)^2: 40 x 0.596 / 23.24^2 = 0.0441, then 0.0371 and 0.0344.)
3. ______________________________  (hint: Discrepancy: rss / N = 0.0149, 0.0207, 0.0230 against sigma^2 = 0.0224; the largest that passes is lam = 3.)
4. ______________________________  (hint: UPRE and GCV pick the smallest score, lam = 15.8. Truth: the emission errors are 0.060, 0.044 and 0.047.)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can we not choose lam by making the residual |I - A I| as small as possible?

Answer: ______________________________________________


**B. Numerical.** A photo has N = 50 pixels and noise sigma = 0.2. Smoothing with lam1 leaves rss = 1.5 with df = 15; lam2 leaves rss = 1.9 with df = 9. Compute UPRE, GCV and the discrepancy test for both, and say which lam each rule prefers.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the top right panel of the first figure, the residual of the fit reaches the dashed noise line only at lam of about 80, while the best lam is about 5. What does this tell you about the discrepancy rule?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for the candle photo at 1, 3 and 6 percent noise, run compare_methods(clean_candle(), frac) and report the mean worst-row error of UPRE on all rows, of the oracle and of the fixed lam = 3. Which rule would you ship, and how does the chosen lam change with the noise?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happens: ____________________
