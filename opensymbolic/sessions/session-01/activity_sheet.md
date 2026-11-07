# Activity sheet: opensymbolic, Session 1: Data that follow a law: can a computer guess the formula?

Name: ____________________   Date: ____________

**Objectives**

- Explain what it means for measured data to follow a law, and why measurements never match it exactly.
- Fit the one unknown constant c in d = c t^n by least squares.
- Score a candidate formula by its mean squared error and rank candidates.
- Read an error-versus-exponent curve and explain why its lowest point is a good guess for the law.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Fit d = c t^2 to the six measured distances for the falling ball (times 0.5, 1, 1.5, 2, 2.5, 3 s) and estimate g.

1. ______________________________  (hint: Measured distances are 1.251, 4.758, 11.147, 19.228, 31.576 and 43.704...)
2. ______________________________  (hint: The shapes f = t^2 are 0.25, 1, 2.25, 4, 6.25 and 9. Their squares sum...)
3. ______________________________  (hint: Multiply each shape by its distance and add: sum(f d) = 697.742....)
4. ______________________________  (hint: c = 697.742 / 142.1875 = 4.907 m/s^2....)
5. ______________________________  (hint: The mean squared error is 0.205 m^2, and g = 2c = 9.81 m/s^2, the know...)

Final answer: ____________________

## Questions
**A. Conceptual.** Two exponents, n = 1.9 and n = 2.1, give errors of 0.37 and 0.48 m^2, close to the 0.20 m^2 of n = 2. Can the data prove that n is exactly 2?

Answer: ______________________________________________


**B. Numerical.** A shape f = (1, 2) is fitted to the data d = (3, 5) with d = c f. Find c and the MSE by hand.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the error-versus-exponent curve, the error at n = 1 is 34.39 m^2 and at n = 3 it is 15.73 m^2. Which wrong guess is worse, and where is the minimum?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you can time only four drops with a stopwatch accurate to about 0.1 s. Choose the drop times (or heights) and say how you would decide between n = 1.5, 2 and 3, and what would make your decision more reliable.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
