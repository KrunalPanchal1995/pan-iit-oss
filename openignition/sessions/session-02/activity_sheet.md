# Activity sheet: openignition, Session 2: The one-step model and the ignition-delay law

Name: ____________________   Date: ____________

**Objectives**

- Reduce the two coupled equations to one using the heat balance T = T0 + DT_AD (1 - c).
- Compute the ignition delay as an integral, and compare it with the Frank-Kamenetskii estimate.
- Show that ln(delay) against 1000/T0 is nearly a straight line, and read its slope.
- Solve the inverse problem: what start temperature gives a chosen delay?

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For T0 = 1000 K, estimate the delay with the Frank-Kamenetskii formula by hand, and compare it with the integral computed by the code.

1. ______________________________  (hint: k(T0) = 2.5e9 * exp(-18.04) = 36.514 per second (Session 1)....)
2. ______________________________  (hint: R T0^2 = 8.314 * 1 000 000 = 8.314e6 J/mol....)
3. ______________________________  (hint: Ea DT_AD k(T0) = 150000 * 1500 * 36.514 = 8.216e9 J/mol per second....)
4. ______________________________  (hint: tau_FK = 8.314e6 / 8.216e9 = 1.012e-3 s = 1.01 ms....)
5. ______________________________  (hint: The integral evaluated by the code gives 1.192 ms, so the estimate is ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is ln(delay) against 1000/T0 nearly a straight line, and why is its slope smaller than Ea / (1000 R)?

Answer: ______________________________________________


**B. Numerical.** Use the Frank-Kamenetskii formula by hand to estimate the delay at 1100 K, and compare it with the exact value 0.2829 ms.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the ln(delay) plot, read the slope between the points at 900 K and 1100 K. Is it equal to the fitted slope 15.96? Why can it differ?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the charge can only be heated to 950 K, but you need a 1 ms delay. Using a catalyst-like additive that multiplies the pre-exponential factor A, by what factor must A grow? Name one other lever and its cost.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
