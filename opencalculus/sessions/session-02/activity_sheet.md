# Activity sheet: opencalculus, Session 2: Derivative and integral as limits

Name: ____________________   Date: ____________

**Objectives**

- Compute a secant slope, shrink the gap and see it settle on the derivative.
- Differentiate polynomials, sin and exp by the rules, and check a rule with finite differences.
- Approximate an integral by thin rectangles and see the error shrink as they get thinner.
- State the fundamental theorem and use it to check units and answers.
- Solve a design problem: the stopping distance of a braking car.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For x(t) = 3 t^2 + 2 t (metres), find the velocity and acceleration at t = 2 s with units, check the derivative with secant slopes, and check the fundamental theorem on [0, 2] with rectangles.

1. ______________________________  (hint: Position: x(2) = 3 * 4 + 2 * 2 = 12 + 4 = 16 m....)
2. ______________________________  (hint: Velocity by the rule: v(t) = 6 t + 2, so v(2) = 14 m/s. Units: 6 is m/...)
3. ______________________________  (hint: Acceleration: a = v' = 6 m/s^2, constant....)
4. ______________________________  (hint: Secant check at t = 2: slope = (x(2 + h) - x(2)) / h = 14 + 3 h, so h ...)
5. ______________________________  (hint: Fundamental theorem: the integral of v from 0 to 2 equals x(2) - x(0) ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the secant slope never equal the tangent slope exactly for h > 0, and why is it still useful to compute it?

Answer: ______________________________________________


**B. Numerical.** For x(t) = 5 t^2 + 4 t (metres), find x, the velocity and the acceleration at t = 3 s, with units, and check that the units of the two coefficients make sense.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the position view with A = 3, B = 2, t = 2, the secant slope with gap h = 2 s is shown. What value do you read, and what happens when you reduce h to 0.1?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a driver has a reaction time of 0.75 s and the car brakes at a steady 6 m/s^2. What is the stopping distance from 25 m/s (90 km/h)? What is the largest speed that stops within 40 m? State two things this simple model leaves out.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
