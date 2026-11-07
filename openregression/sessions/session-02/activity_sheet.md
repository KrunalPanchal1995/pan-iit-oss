# Activity sheet: openregression, Session 2: Least squares, R squared and honest uncertainty

Name: ____________________   Date: ____________

**Objectives**

- Derive the normal equations and solve them to get the best line and check it against numpy.polyfit.
- Compute and interpret R squared, and read a residual plot for warning signs.
- Fit two inputs with numpy.linalg.lstsq and verify that the normal equations hold.
- Build a 95 percent prediction interval, test its coverage by simulation, and use it to answer a design question.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For the dots (1, 2), (2, 2), (3, 5) compute R squared by hand, then predict the yield at x = 4.

1. ______________________________  (hint: From Session 1 the line is y = 0 + 1.5 x with residuals 0.5, -1, 0.5, ...)
2. ______________________________  (hint: The mean of y is 3, so SS_tot = (2 - 3)^2 + (2 - 3)^2 + (5 - 3)^2 = 1 ...)
3. ______________________________  (hint: R squared = 1 - 1.5 / 6 = 0.75....)
4. ______________________________  (hint: Check with the correlation: r = Sxy / sqrt(Sxx Syy) = 3 / sqrt(2 * 6) ...)
5. ______________________________  (hint: Prediction at x = 4: 0 + 1.5 * 4 = 6.0. This is extrapolation (the dat...)

Final answer: ____________________

## Questions
**A. Conceptual.** A line fitted to curved data has R squared 0.837. Is it a good model? What does the residual plot show, and what would you do?

Answer: ______________________________________________


**B. Numerical.** For the dots (1, 2), (2, 2), (3, 5) the best line is y = 1.5 x. Show that the normal equations hold, i.e. that X^T e = 0 for the residuals e = (0.5, -1, 0.5).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the app (noise 0.30 t/ha, 20 seasons) the band is narrowest at 600 mm. What is the half-width there, and what is it at 1100 mm? Why is it larger?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with 20 farm seasons, how much rain is needed for a 3.5 t/ha yield on average, and how much so that the lower end of the 95 percent prediction interval reaches 3.5 t/ha? Comment on the trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
