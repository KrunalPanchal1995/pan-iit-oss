# Activity sheet: openbatterycell, Session 4: A cold-proof lamp pack

Name: ____________________   Date: ____________

**Objectives**

- Compute how much a cell's internal resistance rises when it is cold, and what that does to the voltage at a load.
- Treat a series-parallel pack as one equivalent cell and compute the lamp voltage and runtime.
- Tell a pack that fails at the start from one that runs out early, and say what cures each.
- Search for the smallest pack that works at 0, 25 and 45 C, and validate the pack model with an independent solver.
- Compare design levers (a lower-resistance cell, a pack held warm) and say what each one costs.

## Before you start: predict
In your own words, what do you think will happen to the lamp voltage of the 20-cell pack when you move the ambient slider in the live app from 25 C to 0 C?

______________________________________________________________

## Worked example (fill in as you go)
The 10 x 2 pack of Session 3 feeds a 30 ohm lamp with a cutoff of 9 V. At 25 C it runs 5.95 h. Find what happens at 0 C and the smallest pack that works at 0, 25 and 45 C.

1. ______________________________  (hint: the factor at 0 C is exp(20000/8.3145 x (1/273.15 - 1/298.15)) = 2.093; r = 0.8 x 2.093 x 1.05 = 1.758 ohm)
2. ______________________________  (hint: the pack is one cell feeding R_eq = 30 x 2 / 10 = 6 ohm; the lamp voltage is 10 times its terminal voltage)
3. ______________________________  (hint: at 0 C, E = 1.1271 V and v = 10 x 1.1271 x 6 / (6 + 1.758) = 8.72 V)
4. ______________________________  (hint: 12 in series gives 10.01 V and 5.60 h at 0 C; no pack under 24 cells works at all three temperatures)
5. ______________________________  (hint: alone, 45 C needs 18 cells, 25 C needs 20, 0 C needs 24)

Final answer: ____________________

## Questions
**A. Conceptual.** A cold cell has almost the same open-circuit voltage as a warm one (1.127 V against 1.130 V), yet the 20-cell pack lights the lamp at 25 C and not at 0 C. What changes, which kind of failure is it, and what cures it?

Answer: ______________________________________________


**B. Numerical.** Find the internal resistance of a fresh cell at 0 C and the lamp voltage at the start of the 10 x 2 pack at 0 C (E = 1.1271 V at 0 C).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the right panel of the figure the 10 x 2 curve stays at 0 h up to about 5 C and then rises steeply, while the 12 x 2 curve rises earlier and then slowly falls above about 8 C. What limits each curve in those regions?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose one of (a) 24 plain cells, (b) 22 cells with a cell 30 percent lower in resistance, (c) 22 plain cells in an insulated box that holds them 5 K warm. Compare them at 0, 25 and 45 C, say which you would choose for a lamp used outdoors in winter, and say what the model leaves out for each.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happens: ____________________
