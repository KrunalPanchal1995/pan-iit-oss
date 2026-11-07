# Activity sheet: openpinn, Session 3: A network that solves the heat equation, and finds its diffusivity

Name: ____________________   Date: ____________

**Objectives**

- State the heat equation with its boundary and initial conditions and its exact solution.
- Derive and verify the formulas for u_t and u_xx of a one-hidden-layer tanh network, and train it with Adam on residual, boundary and initial losses.
- Validate against the exact solution and against an explicit finite-difference solver, and report the relative L2 error honestly.
- Study the failure cases (too few collocation points, a badly weighted loss, a higher-frequency solution) and compare cost with a classical solver.
- Recover the diffusivity from noisy readings by making it a trainable parameter, and judge when the estimate can be trusted.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For alpha = 0.1 find the exact temperature at the rod centre at t = 1 and the half-life, then compare the trained network and the finite-difference scheme (20 intervals, r = 0.4) with it.

1. ______________________________  (hint: u(0.5, 1) = sin(pi / 2) exp(-0.1 pi^2) = exp(-0.987) = 0.3727....)
2. ______________________________  (hint: Half-life: t = ln 2 / (0.1 pi^2) = 0.693 / 0.987 = 0.702, so the centr...)
3. ______________________________  (hint: The trained network (20 units, 200 points, 1000 steps) gives a value w...)
4. ______________________________  (hint: Finite differences: dx = 0.05 and r = 0.4 give dt = r dx^2 / alpha = 0...)
5. ______________________________  (hint: Cost: finite differences need 100 steps of 19 updates, i.e. 1900 updat...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can both a too small and a too large weight of the residual term w_res make the network worse?

Answer: ______________________________________________


**B. Numerical.** The diffusivity is doubled to 0.2. Find the centre temperature at t = 1 and compare with alpha = 0.1. For dx = 0.05 and dt = 0.01, what is r now, and is the explicit scheme stable?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the loss figure, which piece starts the largest and how far do the pieces fall? What does the profile panel show about the time t = 1?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you want a relative L2 error below 0.03 at the smallest training cost by changing the number of collocation points. Which of N = 5, 20 and 200 would you choose, and what is the risk of N = 5?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
