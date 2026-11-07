# Activity sheet: openneuralode, Session 2: Solvers, least squares and a first neural network

Name: ____________________   Date: ____________

**Objectives**

- Measure the order of accuracy of Euler (1) and RK4 (4) from an error against step size graph.
- Fit a linear rule from noisy data with least squares, using derivatives estimated from the data.
- Train a one-hidden-layer tanh network on one-step differences with hand-written backpropagation and Adam.
- Answer a design question: how many runs and how little noise give an accurate fit?

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
From the state (1 m, 0) with k = 4 and c = 0.4, take one step of h = 0.1 s with Euler and with RK4, and compare with the exact state.

1. ______________________________  (hint: Euler: the arrow at (1, 0) is (0, -4), so the new state is (1, 0) + 0....)
2. ______________________________  (hint: RK4 stage 1: k1 = (0, -4). Stage 2 at (1, 0) + 0.05 * k1 = (1, -0.2): ...)
3. ______________________________  (hint: RK4 stage 4 at (1, 0) + 0.1 * k3 = (0.9804, -0.38816): k4 = (-0.38816,...)
4. ______________________________  (hint: Blend: (0.1 / 6) * (k1 + 2 k2 + 2 k3 + k4) = (0.1 / 6) * (-1.18016, -2...)
5. ______________________________  (hint: The exact state at t = 0.1 s is (0.9803, -0.3895). Euler is off by abo...)

Final answer: ____________________

## Questions
**A. Conceptual.** With noise 0.2 the fit error stays above 0.3 even with 30 runs, while with noise 0.01 a handful of runs is enough. Why does more data not fix the noisy case?

Answer: ______________________________________________


**B. Numerical.** The Euler error at 2 s is 0.575 for h = 0.1. Predict the error for h = 0.025 using the order p = 1, then compare with the measured value 0.128. What would an order-4 method predict from its error 4.3e-5 at h = 0.1?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the error graph, how do you read the order of a method, and what would a slope of 2 mean? What happens to RK4 if h becomes extremely small?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the sensor noise can be 0.01, 0.05 or 0.2 and you can record K = 1, 3, 10 or 30 runs of 20 samples. You need a fit error (|A_hat - A|) below 0.1. Which combinations work, and which sensor and how many runs would you choose?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
