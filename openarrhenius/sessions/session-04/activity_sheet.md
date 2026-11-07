# Activity sheet: openarrhenius, Session 4: Fit a curved Arrhenius plot

Name: ____________________   Date: ____________

**Objectives**

- Write the two-channel model k = k1(T) + k2(T) and explain why it bends the Arrhenius plot.
- Fit it by nonlinear least squares (Levenberg-Marquardt) and say why a start guess matters.
- Report the four parameters with their covariance, and explain why they are poorly known one by one while the prediction at 2000 K is well known.
- Decide between one and two channels with the corrected Akaike criterion (AICc) and the residual pattern.
- Validate the method by repeated experiments and say how hot the data must go.

## Before you start: predict
In your own words, what do you think will happen to the prediction at 2000 K when you lower the hottest temperature in the live app from 1600 K to 900 K?

______________________________________________________________

## Worked example (fill in as you go)
Twelve temperatures from 500 to 1600 K in steps of 100 K, synthetic data with 3 percent error from lnA1 = 16.118, E1 = 50 kJ/mol, lnA2 = 32.236, E2 = 200 kJ/mol (seed 0). Fit one line and two channels, report the parameters with errors, and predict k at 2000 K with a 95 percent interval. Does it hold the true 5.98e8 per s?

1. ______________________________  (hint: the straight line has s = 1.267, residuals in 3 runs, and predicts 1.18e7 per s)
2. ______________________________  (hint: the fit gives E1 = 50.05 +- 0.228 and E2 = 198.51 +- 1.19 kJ/mol, s = 0.0217 on 8 degrees of freedom)
3. ______________________________  (hint: lnA and E of one channel are correlated, 0.974 and 0.995; crossover 1118 K)
4. ______________________________  (hint: at 2000 K se(ln k) = 0.0317 and t = 2.306 for 8 degrees of freedom)
5. ______________________________  (hint: AICc is 8.8 for the line and -83.1 for two channels)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does adding two Arrhenius terms bend the plot of ln k against 1000/T, and why does the hot end follow the channel with the larger Ea?

Answer: ______________________________________________


**B. Numerical.** For the true law (lnA1 = 16.118, E1 = 50 kJ/mol, lnA2 = 32.236, E2 = 200 kJ/mol) find the crossover temperature.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the right panel of the figure, the share of correct predictions is about 1 percent when the data stop at 900 K, yet the 95 percent band is narrow there (a factor 1.26). Which number from the fit says that the straight line is enough, and why can that number not rescue the prediction?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you have 12 points from 500 K at 3 percent error and may choose the hottest temperature. How hot must you go so that at least 95 percent of repeated experiments predict k(2000 K) within a factor 1.5 of the truth? Test the cases in the app.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
