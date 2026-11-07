# Activity sheet: openchaos, Session 4: A fourth-order symplectic solver

Name: ____________________   Date: ____________

**Objectives**

- Build a fourth-order symplectic solver from three steps of the midpoint rule and explain where the sizes 1.3512 and -1.7024 come from.
- Measure the order of a solver from the ratio of its errors when the step is halved.
- Compare solvers by the work they need (rate evaluations) instead of by their step size.
- Find the step size at which an implicit solver stops converging and say why the fourth-order solver gives up first.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Find the three step sizes of the triple jump for h = 0.02 s and check the two order conditions.

1. ______________________________  (hint: 2^(1/3) = 1.259921, so 2 - 2^(1/3) = 0.740079.)
2. ______________________________  (hint: gamma1 = 1 / 0.740079 = 1.351207.)
3. ______________________________  (hint: gamma0 = -2^(1/3) gamma1 = -1.259921 x 1.351207 = -1.702414.)
4. ______________________________  (hint: Sum: 2 x 1.351207 - 1.702414 = 1.000000. Cubes: gamma1^3 = 2.467, so 2 gamm...)
5. ______________________________  (hint: For h = 0.02 s the sub-steps are 0.027024 s, -0.034048 s and 0.027024 s, wh...)

Final answer: ____________________

## Questions
**A. Conceptual.** A classmate says: "The fourth-order solver is simply better than the midpoint rule: it is just as symplectic and much more accurate." Give two reasons why this is too simple.

Answer: ______________________________________________


**B. Numerical.** At h = 0.05 s the composition's state error after 0.4 s is 2.75e-4. Predict the error at h = 0.0125 s, and compare the number of midpoint solves per second of simulated time at the two steps. Give a sanity check.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** Figure 3 (left) gives, for the typical largest energy error over 60 s, 43,328 evaluations for the midpoint rule and 121,330 for the composition at 1e-2, and for 1e-4 only the composition (192,125). Which solver would you choose for each limit? Why does the composition's curve fall so much faster as the work grows?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you need the typical largest energy error of the 120 degree release over 60 s to stay below 1e-4 of E_ref, with a budget of 200,000 rate evaluations. Choose a solver and a step, check your margin against the step at which the solver fails, and say what you would re-test if the pendulum were released from 150 degrees.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
