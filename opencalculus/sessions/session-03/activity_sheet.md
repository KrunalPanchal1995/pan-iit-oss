# Activity sheet: opencalculus, Session 3: Numerical slopes and areas, and their errors

Name: ____________________   Date: ____________

**Objectives**

- Implement forward and central differences, the trapezoid rule and Simpson's rule.
- Measure the order of each method from a log-log plot of error against step size.
- Find and explain the round-off limit when the step is too small.
- Use an adaptive step to put small slices only where the function bends.
- Recognise failure cases: a corner and a narrow spike.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Find the forward and central difference of sin x at x = 1 with h = 0.1 and compare with the exact cos 1. Then find the trapezoid and Simpson areas of e^x on [0, 1] with n = 4 and compare with e - 1.

1. ______________________________  (hint: Exact: cos 1 = 0.540302. Values: sin 1 = 0.841471, sin 1.1 = 0.891207,...)
2. ______________________________  (hint: Forward: (0.891207 - 0.841471) / 0.1 = 0.49736, error -0.0429. Central...)
3. ______________________________  (hint: Areas: h = 0.25, values e^x = 1, 1.284025, 1.648721, 2.117000, 2.71828...)
4. ______________________________  (hint: Simpson: (0.25 / 3) * (1 + 4 * 1.284025 + 2 * 1.648721 + 4 * 2.117000 ...)
5. ______________________________  (hint: Pattern: with h = 0.01 the forward error is -0.0042 and the central er...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can making the step h smaller make a numerical derivative worse?

Answer: ______________________________________________


**B. Numerical.** The trapezoid rule for e^x on [0, 1] with n = 16 has an error of 5.6e-4. Predict the error with n = 32, and for Simpson's rule if its error at n = 16 is 1.5e-7.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On a log-log plot of error against h, a method's points lie on a line which falls 4 decades while h falls 1 decade. What is its order? Which of our four methods is it?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you must integrate a function with one very narrow spike (width 0.005) on [0, 1] to 1e-8. Compare a uniform Simpson rule with an adaptive one, and say what could go wrong with the adaptive rule.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
