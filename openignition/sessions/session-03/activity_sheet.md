# Activity sheet: openignition, Session 3: Stiffness: explicit versus implicit, and how to trust the answer

Name: ____________________   Date: ____________

**Objectives**

- Explain stiffness with the Jacobian: a very fast mode forces explicit steps to stay tiny even when nothing happens.
- Write an explicit RK4 and an implicit trapezoid solver with Newton iteration, both adaptive, and compare their cost and accuracy.
- Validate the delay against an exact quadrature and the Semenov criterion, and show convergence with tolerance.
- Measure normalised sensitivities and a pressure law, and recognise a failing step size.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For T0 = 1000 K find the fast decay rate after ignition and the largest stable RK4 step. Then check it by running RK4 just below and just above that step.

1. ______________________________  (hint: After ignition T = 1000 + 1500 = 2500 K and c is almost zero, so the f...)
2. ______________________________  (hint: Ea / (R T) = 150000 / (8.314 * 2500) = 7.217, exp(-7.217) = 7.34e-4, s...)
3. ______________________________  (hint: The RK4 stability limit is 2.785 / 1.84e6 = 1.52e-6 s = 1.52 microseco...)
4. ______________________________  (hint: RK4 with a step of 1.45 microseconds ends correctly at 2500 K with the...)
5. ______________________________  (hint: RK4 with 1.6 microseconds stays finite but ends wrong (the temperature...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why must an explicit method keep taking microsecond steps after the ignition is over, when the temperature is no longer changing? Why can an implicit method take huge steps there?

Answer: ______________________________________________


**B. Numerical.** For a run started at 900 K, find the final temperature, the decay rate k(final T) and the RK4 stability limit.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the steps-against-tolerance figure, why is the RK4 curve flat while the trapezoid curve rises? What does that mean for the choice of solver at a loose or a tight tolerance?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you must compute the delay to within 0.1 percent for a large number of cells over 30 ms each. Which solver and tolerance do you choose, and how much does it save? State the assumption.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
