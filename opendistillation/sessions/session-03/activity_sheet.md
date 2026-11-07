# Activity sheet: opendistillation, Session 3: Design the column and validate it

Name: ____________________   Date: ____________

**Objectives**

- Write the rectifying and stripping operating lines and the q-line for a column with reflux.
- Step off equilibrium stages on the real x-y curve (McCabe-Thiele) and find the number of stages and the feed stage.
- Validate the stepping against Fenske (total reflux) and the material balances, and find the minimum reflux, including a tangent pinch.
- Choose a reflux ratio by trading the number of trays against the reboiler steam, and explain why the azeotrope caps the product.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Design the distillery column: F = 100 kmol/h, zF = 0.10 (saturated liquid), xD = 0.80, xB = 0.02, 1 atm. Find Rmin, the stages and feed stage at R = 1.5 Rmin, and the reboiler duty.

1. ______________________________  (hint: Material balance (Session 1): D = 100 x 0.08 / 0.78 = 10.26 kmol/h, B = 89....)
2. ______________________________  (hint: Pinch at the feed: the wash's vapour (Session 2) is y* = 0.440, so Rmin = (...)
3. ______________________________  (hint: R = 1.5 x 1.058 = 1.587. Rectifying line: y = 0.6135 x + 0.3092. L = 16.28,...)
4. ______________________________  (hint: Step from the top: x1 = 0.769, x2 = 0.739, ... x11 = 0.088 crosses zF, so s...)
5. ______________________________  (hint: Reboiler duty = 26.53 kmol/h x 40 kJ/mol x 1000 / 3600 = 294.8 kW.)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the column need more and more stages as the reflux ratio approaches Rmin, and why can it not run below Rmin at all?

Answer: ______________________________________________


**B. Numerical.** For the same column at R = 1.5 Rmin = 1.587, find L, V, L' and V' in kmol/h. Check that V' = L' - B and that the two operating lines meet at x = zF = 0.10.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the trade-off figure the number of stages falls in steps while the duty rises smoothly, and the cost curve is jagged. Why? Why does the cost rise sharply below about 1.2 Rmin?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a richer wash with zF = 0.20 arrives (same xD = 0.80, xB = 0.02, 100 kmol/h). The hand formula with y* = y_eq(0.20) = 0.535 gives Rmin = 0.789. Use `min_reflux` to check it, then design at 1.5 Rmin. What changes, and why?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
