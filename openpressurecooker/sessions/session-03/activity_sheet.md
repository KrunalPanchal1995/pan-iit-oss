# Activity sheet: openpressurecooker, Session 3: Simulating heating, venting and cooking

Name: ____________________   Date: ____________

**Objectives**

- Build a lumped model of heating, venting at the regulator pressure and cooking progress.
- Validate it with an energy balance, a hand formula, a time-step test and Clausius-Clapeyron values.
- Compare an open pot with a cooker and test the sensitivity to valve pressure and heater power.
- Explain a blocked-vent failure case and why independent safety valves exist.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For 1 kg of water, a 1000 W heater at 80 percent efficiency, a pot heat capacity of 700 J/K, a 3 L headspace and a 100 kPa gauge regulator, find the hand heating time from 25 degrees C to boiling, the steam in the headspace, and compare with the simulation.

1. ______________________________  (hint: C = 1 x 4186 + 700 = 4886 J/K. T_b = 393.76 K = 120.61 degrees C, so t...)
2. ______________________________  (hint: Hand heating time = 4886 x 95.61 / (0.8 x 1000) = 584 s = 9.73 minutes...)
3. ______________________________  (hint: Steam in the headspace at 120.6 degrees C: m_s = 201325 x 0.003 x 0.01...)
4. ______________________________  (hint: Latent energy to make it: 3.32e-3 x 2.26e6 = 7.5 kJ, which takes 7.5e3...)
5. ______________________________  (hint: The simulation gives boiling at 9.90 minutes (594 s): 584 s + about 10...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the cooker plateau at about 120.6 degrees C instead of continuing to heat up, and what happens to the extra energy once it reaches the plateau?

Answer: ______________________________________________


**B. Numerical.** For 2 kg of water, a 1500 W heater at 80 percent efficiency, 700 J/K pot and a regulator at 100 kPa gauge, estimate the heating time with the hand formula, ignoring the headspace.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the doneness graph, estimate the slope of each pot's line after boiling starts, and use it to explain why the cooker finishes far sooner even though it boils later.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose a regulator setting and heater power so that the lentils are done in at most 20 minutes and the water loss stays below 60 g. Use the sensitivity tables from the lesson and state the trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
