# Activity sheet: openbatterycell, Session 3: A cell that runs down

Name: ____________________   Date: ____________

**Objectives**

- Use the Nernst equation to find how the voltage depends on the concentration ratio, and check it numerically.
- Simulate a discharge with internal resistance and read the terminal voltage curve against charge drawn.
- Show that power to a load is largest when R_load equals the internal resistance, with 50 percent efficiency.
- Validate the simulation against Faraday's law, an energy balance and a time-step test, and study temperature and a short circuit.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A Daniell cell starts with [Zn2+] = 0.10 mol/L and [Cu2+] = 1.0 mol/L at 25 C. Find its voltage, then the current, terminal voltage and powers when it drives a 10 ohm load (internal resistance 0.8 ohm, plus 0.05 x 0.8 from the depletion term at the start).

1. ______________________________  (hint: Q = 0.10 / 1.0 = 0.10, ln Q = -2.3026. R T / (n F) = 8.3145 x 298.15 /...)
2. ______________________________  (hint: E = 1.10 - 0.012847 x (-2.3026) = 1.10 + 0.02958 = 1.1296 V (slightly ...)
3. ______________________________  (hint: Internal resistance at the start: r = 0.8 x (1 + 0.05 x 1.0 / 1.0) = 0...)
4. ______________________________  (hint: Current I = 1.1296 / (10 + 0.84) = 0.1042 A. Terminal voltage V = 1.12...)
5. ______________________________  (hint: Power in the load = I^2 R = 0.1042^2 x 10 = 0.1086 W; heat in the cell...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is the power to the load greatest when R equals the internal resistance, yet the efficiency is then only 50 percent? What would you choose for a torch you want to run a long time?

Answer: ______________________________________________


**B. Numerical.** For E = 1.10 V and r = 0.8 ohm find the load for maximum power, the current, the load power, and the heat made inside the cell at that point.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the discharge curves for loads of 2, 10 and 40 ohm, which curve starts highest and which gives the most usable capacity (to a 10 percent drop in terminal voltage)? Explain the difference using V = E - I r.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design a short-circuit safety limit: a cell has E = 1.10 V and r = 0.05 ohm. A short gives I = 22 A and 24.2 W. Find the series resistance that limits the heat made inside the cell to 2 W, and say why this is not a substitute for a proper fuse.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
