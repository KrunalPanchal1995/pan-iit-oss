# Activity sheet: openledcontrol, Session 3: A controller you can trust: hysteresis, tolerances and logic

Name: ____________________   Date: ____________

**Objectives**

- Simulate the whole controller over a day and count its on-off switches with and without hysteresis.
- Check the simulated switching against hand-calculated thresholds and analytic switching times.
- Use a Monte Carlo run to see how part tolerance and supply voltage move the trip point.
- Build a two-condition alarm with gates, test its truth table on every input, and explain two failure cases.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For the divider with R = 6.8 kilo-ohm and Schmitt thresholds V_LO = 2.25 V and V_HI = 2.75 V, find the two light levels by hand, then the evening switch-on time and the LED on-hours of a day without clouds, and compare with the simulation.

1. ______________________________  (hint: At 2.25 V: R_ldr = 6 800 * (5 - 2.25) / 2.25 = 8 311 ohm, so lux = 10 ...)
2. ______________________________  (hint: At 2.75 V: R_ldr = 6 800 * (5 - 2.75) / 2.75 = 5 564 ohm, so lux = 10 ...)
3. ______________________________  (hint: Evening switch-on: s = (log10(13.0) - 1.3) / 3.2 = -0.058, arcsin s = ...)
4. ______________________________  (hint: Morning switch-off: s = (log10(23.1) - 1.3) / 3.2 = 0.0199, t = 6 + (2...)
5. ______________________________  (hint: On-hours = (24 - 18.22) + 6.08 = 11.86 h; the simulation (1 minute ste...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does hysteresis stop chatter without smoothing the light signal? And why is XOR the wrong gate for an alarm that must fire when either of two conditions is violated?

Answer: ______________________________________________


**B. Numerical.** A wider Schmitt band uses V_LO = 2.0 V and V_HI = 3.0 V with R = 6.8 kilo-ohm. Find the light levels for on and off. Compare the ratio of off-level to on-level with that of the 2.25 V and 2.75 V pair.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the day-simulation figure, why do all the extra switches of the single-threshold comparator cluster near dawn and dusk and none occur at noon or midnight?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a machine has two independent safety conditions, A (temperature too high) and B (pressure too high). The alarm must fire when either is violated. Write the truth table, choose the gate, and say how you would make a broken sensor wire fail safe. Then add a manual-override input for a maintenance person who may silence the alarm.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
