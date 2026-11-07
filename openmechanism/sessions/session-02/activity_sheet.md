# Activity sheet: openmechanism, Session 2: Arrhenius, the 1000/T plot, and which rate an experiment feels

Name: ____________________   Date: ____________

**Objectives**

- Use the Arrhenius form k = A T^n exp(-Ea / R T) and state the unit of each symbol.
- Explain why log k plotted against 1000/T is a straight line whose slope gives Ea.
- Compute the sensitivity d ln(tau) / d ln(k) of an experiment output to each rate constant by finite differences, and check it against calculus.
- Solve a design problem: choose experiment temperatures that pin down the most uncertain rate constants.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A reaction has Ea = 80 kJ/mol and n = 0. By what factor does k increase from 1000 K to 1200 K? Then find the toy ignition delay at 1000 K from the formula.

1. ______________________________  (hint: Ratio = exp(Ea / R x (1/1000 - 1/1200)) = exp(80000 / 8.3145 x 1.6667e...)
2. ______________________________  (hint: 80000 / 8.3145 = 9621.8; times 1.6667e-4 = 1.6036; exp(1.6036) = 4.97....)
3. ______________________________  (hint: Toy ignition delay at 1000 K: k1 = 0.002 per s, k2 = 30 L/(mol s), k3 ...)
4. ______________________________  (hint: tau = ln(1 + 20 / (2 x 0.002)) / 20 = ln(5001) / 20 = 8.517 / 20 = 0.4...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is a plot of log k against 1000/T a straight line for the simple Arrhenius form, and what physical quantity does its slope give?

Answer: ______________________________________________


**B. Numerical.** A reaction has Ea = 120 kJ/mol (n = 0). Find the factor by which k grows from 1000 K to 1100 K, and the slope of ln k against 1000/T.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** Look at the sensitivity graph. Which rate constant does the ignition delay feel most at 900 K, and at 1400 K? What does a negative or a positive sign mean?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you can run two experiments at two of the temperatures 900, 1000, 1100, 1200, 1300, 1400 K (5 percent noise) to learn the scale factors of k1 and k2. Which pair do you choose, which pair is worst, and why?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
