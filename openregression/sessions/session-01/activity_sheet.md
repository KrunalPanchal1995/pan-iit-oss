# Activity sheet: openregression, Session 1: The line that misses least

Name: ____________________   Date: ____________

**Objectives**

- Draw a line through rainfall and yield dots and read a forecast from it.
- Compute a residual (the vertical miss of one dot) and the total squared miss.
- Explain why the best line is the one with the smallest total squared miss.
- Find the best line by formula and check it by trying many other lines.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Three dots (rain, yield) are (1, 2), (2, 2) and (3, 5). Find the least-squares line and its total squared miss by hand.

1. ______________________________  (hint: Means: x-bar = (1 + 2 + 3) / 3 = 2 and y-bar = (2 + 2 + 5) / 3 = 3....)
2. ______________________________  (hint: Sum of (x - 2)(y - 3) = (-1)(-1) + (0)(-1) + (1)(2) = 1 + 0 + 2 = 3. S...)
3. ______________________________  (hint: Slope b = 3 / 2 = 1.5. Intercept a = 3 - 1.5 * 2 = 0....)
4. ______________________________  (hint: Predictions: 1.5, 3.0, 4.5. Residuals: 2 - 1.5 = 0.5, 2 - 3 = -1, 5 - ...)
5. ______________________________  (hint: SSE = 0.25 + 1 + 0.25 = 1.5. Check: the residuals add up to 0.5 - 1 + ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do we square the residuals instead of just adding them up? What would happen to the line 'sum of residuals = 0' test?

Answer: ______________________________________________


**B. Numerical.** Find the least-squares line for the dots (0, 2), (1, 1) and (2, 6), and its total squared miss.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the bowl view, at which slope is the green curve lowest, and what is its value there? Why is the blue curve never below the green one?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: using the best line of the farm data, how much rain gives an expected yield of 3.5 t/ha? Is the answer inside the range of the data? What should you worry about?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
