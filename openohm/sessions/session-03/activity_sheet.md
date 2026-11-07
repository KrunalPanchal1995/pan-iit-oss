# Activity sheet: openohm, Session 3: A non-ohmic LED: solve it numerically and validate

Name: ____________________   Date: ____________

**Objectives**

- Explain why an LED does not obey Ohm's law and why it needs a series resistor.
- Solve the circuit equation numerically with Newton's method and with bisection.
- Validate the solver against a reference, the ohmic limit and a hand calculation.
- Measure how the current changes with the supply voltage and choose a resistor within a power budget.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 5 V supply feeds a 150 ohm resistor in series with the LED. Find the operating point, check it against Kirchhoff's law, and compare with the ohmic shortcut.

1. ______________________________  (hint: Guess that the LED drops about 2.0 V (the tuned point). The resistor t...)
2. ______________________________  (hint: I = 3 / 150 = 0.020 A = 20 mA, which is exactly the current at which t...)
3. ______________________________  (hint: Newton's method started from 2.5 V reaches Vd = 2.000 V, I = 20.00 mA ...)
4. ______________________________  (hint: Kirchhoff check: I R + Vd = 0.020 x 150 + 2.0 = 5.0 V = Vs....)
5. ______________________________  (hint: Powers: resistor 0.020^2 x 150 = 0.060 W, LED 2.0 x 0.020 = 0.040 W, t...)
6. ______________________________  (hint: The ohmic shortcut Vs / R = 5 / 150 = 33.3 mA is 67 percent too high, ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does an LED need a series resistor, but an ordinary resistor does not?

Answer: ______________________________________________


**B. Numerical.** For Vs = 5 V and R = 150 ohm use the sensitivity formula to estimate how much the LED current changes if the supply rises by 0.5 V. Compare with the value from the model (23.3 mA at 5.5 V).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the load-line figure the three operating points have LED voltages between 1.99 and 2.01 V but currents between 16.7 and 23.3 mA. What does that say about which part controls the current?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a 5 V supply (4.5 to 5.5 V) must give 10 to 25 mA in the LED and use at most 0.12 W in total at 5.5 V. Choose from the E12 series and justify.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
