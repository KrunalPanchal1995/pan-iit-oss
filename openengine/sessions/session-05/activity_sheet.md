# Activity sheet: openengine, Session 5: The dual cycle

Name: ____________________   Date: ____________

**Objectives**

- Describe the five processes of the dual (Seiliger) cycle and split its heat into a constant-volume and a constant-pressure part.
- Compute the dual-cycle temperatures, pressure ratio, cut-off ratio and efficiency, and show that it becomes Otto or Diesel in the limits.
- Explain why the efficiency of the dual cycle lies between the Diesel and Otto values at the same compression ratio and heat.
- Choose the heat split that gives the best efficiency under a peak-pressure limit.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A dual cycle with r = 18, T1 = 300 K, P1 = 100 kPa takes q_in = 1100 kJ/kg, half at constant volume and half at constant pressure. Find the temperatures, alpha, rho, the peak pressure and the efficiency, and check the result with the closed-form formula.

1. ______________________________  (hint: Compression: 18^0.4 = 3.1777, so T2 = 300 x 3.1777 = 953.3 K and P2 = 100 x 18 x...)
2. ______________________________  (hint: Constant volume: T3 = 953.3 + 550 / 0.7175 = 953.3 + 766.6 = 1719.9 K, so alpha ...)
3. ______________________________  (hint: Constant pressure: T4 = 1719.9 + 550 / 1.0045 = 1719.9 + 547.5 = 2267.4 K, so rh...)
4. ______________________________  (hint: Expansion from rho v2 to r v2: T5 = 2267.4 x (1.318 / 18)^0.4 = 2267.4 x 0.3515 ...)
5. ______________________________  (hint: Formula: alpha rho^1.4 - 1 = 1.804 x 1.4725 - 1 = 1.6565 and (alpha - 1) + 1.4 a...)

Final answer: ____________________

## Questions
**A. Conceptual.** At the same r and the same heat, why does moving heat from constant pressure to constant volume raise the efficiency, and why is that not free?

Answer: ______________________________________________


**B. Numerical.** A dual cycle has r = 16, q_in = 1000 kJ/kg and x = 0.4 (T1 = 300 K, gamma = 1.4). Find T2, T3, T4, alpha, rho and the efficiency.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the efficiency figure the curve rises quickly for small x and flattens near x = 1, while the peak pressure rises in a straight line. What does that mean for the last 10 percent of heat moved to constant volume?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the cylinder head of a diesel engine allows a peak pressure of 9000 kPa. With q_in = 1100 kJ/kg, find the largest constant-volume share x and the resulting efficiency at r = 16, 18 and 20. Which r would you choose, and what limits r from above?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
