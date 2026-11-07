# Activity sheet: openreactionrate, Session 3: Reaction networks as ODEs, and when they bite back

Name: ____________________   Date: ____________

**Objectives**

- Write a reaction network as dc/dt = S r(c) with a stoichiometry matrix S and solve it with your own RK4.
- Validate the solver against an exact first-order solution and check that the conserved sums stay constant.
- Compare the quasi-steady-state (Michaelis-Menten) approximation with the full enzyme cycle and see how the error depends on the enzyme-to-substrate ratio.
- Find the rate-determining step of a chain, and recognise stiffness and the failure of an explicit step that is too large.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For the enzyme cycle with k1 = 10 L/(mol s), km1 = 5 1/s, k2 = 1 1/s and E0 = 0.1 mol/L, find Km and Vmax and the Michaelis-Menten rate at S = 1.0 mol/L. Then compare with the full model.

1. ______________________________  (hint: Km = (km1 + k2) / k1 = (5 + 1) / 10 = 0.6 mol/L....)
2. ______________________________  (hint: Vmax = k2 E0 = 1 * 0.1 = 0.1 mol/(L s)....)
3. ______________________________  (hint: v(S = 1.0) = Vmax S / (Km + S) = 0.1 * 1.0 / 1.6 = 0.0625 mol/(L s). A...)
4. ______________________________  (hint: Run the full four-species RK4 (h = 0.005 s). At t = 1 s the model has ...)
5. ______________________________  (hint: The QSSA rate at that same S is 0.1 * 0.8837 / (0.6 + 0.8837) = 0.0595...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is it useful that the sum of the concentrations (or E + ES and S + ES + P) stays constant in a simulation? What would it tell you if one drifted?

Answer: ______________________________________________


**B. Numerical.** For E0/S0 = 0.1 and 1.0 the largest QSSA error in the product is 0.022 and 0.201 times S0. For which ratio would you trust the Michaelis-Menten equation to within 1 percent of S0? How can you check without running the full model?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the stiffness graph, explicit RK4 with h = 1e-3 blows up and h = 1e-4 does not. Explain the numbers using the fastest rate constant 10000 1/s and the limit h k of about 2.8.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: in the chain A -> B -> C -> D with k = 0.8, 0.05 and 0.6 1/s a catalyst can speed up only one step. You want the yield of D at 10 s to at least double (0.295 to 0.59 mol/L). Which step, and what factor? Why can the other two steps not do it?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
