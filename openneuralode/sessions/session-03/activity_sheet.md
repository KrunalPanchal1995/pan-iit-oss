# Activity sheet: openneuralode, Session 3: A Neural ODE trained through the solver

Name: ____________________   Date: ____________

**Objectives**

- Train a network as the right-hand side of an ODE with a rollout loss, using hand-coded backpropagation through RK4.
- Compare one-step training and rollout training and show the error growth with prediction time.
- Validate the result against a known linear system: eigenvalues and trajectories.
- Explain and reproduce three failure cases (stiffness, extrapolation, overfitting) and the effect of noise and horizon.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A stiff system has x' = -1000 x. With RK4 and h = 0.01 s, what happens? What is the largest stable step, and what happens at h = 0.002 s?

1. ______________________________  (hint: z = lambda h = -1000 * 0.01 = -10....)
2. ______________________________  (hint: R(-10) = 1 - 10 + 50 - 166.67 + 416.67 = 291. Each step multiplies the...)
3. ______________________________  (hint: The stability limit on the negative real axis is z = -2.785, so h must...)
4. ______________________________  (hint: At h = 0.002: z = -2 and R(-2) = 1 - 2 + 2 - 1.3333 + 0.6667 = 1/3. Th...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does rollout training give better long predictions than one-step training when the data are noisy?

Answer: ______________________________________________


**B. Numerical.** For lambda = -500 per s, find the largest stable RK4 step. Does h = 0.01 s work? Give R(z) for h = 0.004 s and state the units.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the error view, set the horizon to 8 and the noise to 0.0, 0.05 and 0.1. What happens to the error after 6 s, and why does the curve not grow without bound over time?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the sensor noise is 0.1 and you need an error below 0.1 after 6 s. You can record 6 or 18 runs with the same 25 samples each. Which would you choose, and what are the trade-offs?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
