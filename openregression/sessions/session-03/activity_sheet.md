# Activity sheet: openregression, Session 3: Overfitting, ridge and honest validation

Name: ____________________   Date: ____________

**Objectives**

- Measure training and test error against polynomial degree and find the best degree.
- Use ridge regression (closed form) and k-fold cross-validation, written by you, to choose a setting honestly.
- Measure bias and variance by refitting on many resampled data sets.
- Recognise and handle outliers, confounders and collinear inputs, and audit a model with a prediction interval.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Three points x = -1, 0, 1 with y = 0, 1, 5. Compute the ridge slope by hand for lambda = 0 and lambda = 3 (standardise x first), and convert back to the original units.

1. ______________________________  (hint: x-bar = 0 and the standard deviation (dividing by n) is sqrt(2/3) = 0....)
2. ______________________________  (hint: y-bar = 2, so the centred y are -2, -1, 3. X^T X = 3 (sum of squares o...)
3. ______________________________  (hint: Ridge slope = 6.1237 / (3 + lambda). For lambda = 0 this is 2.0412; fo...)
4. ______________________________  (hint: Back to original units divide by 0.8165: 2.5 for lambda = 0 (the ordin...)

Final answer: ____________________

## Questions
**A. Conceptual.** A colleague picks the polynomial degree with the smallest training error and reports it. Why is that wrong, and what should be done instead?

Answer: ______________________________________________


**B. Numerical.** For the three points x = -1, 0, 1 with y = 0, 1, 5, find the ridge slope in original units for lambda = 6.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the app, at degree 9, compare the expected test error at log10 lambda = -4 and at -1. What does each tell you about the fit?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for the farm data set of the mini-project, you can deploy the mean only, rain only, the three inputs, or the too-flexible model. Choose by cross-validation and give the forecast for 550 mm, 60 kg/ha, 25 degrees C with its interval. What do you tell the farmer about it?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
