# Activity sheet: openledcontrol, Session 1: A sensor, a decision and a switch

Name: ____________________   Date: ____________

**Objectives**

- Explain how a light dependent resistor (LDR) senses light.
- Draw and label the block diagram of a light-activated LED controller.
- Use the illustrative LDR curve to find its resistance at a given light level.
- Decide, with a threshold, when the LED should be on, and read this from a graph.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
At 2 lux, what is the LDR resistance with the illustrative curve, and is the LED on with a 20 lux threshold?

1. ______________________________  (hint: Light divided by 10: 2 / 10 = 0.2....)
2. ______________________________  (hint: R = 10 000 * 0.2 ^ (-0.7). Since 0.2 ^ (-0.7) = 5 ^ 0.7 = 3.085, R = 1...)
3. ______________________________  (hint: Compare with the threshold: 2 lux is below 20 lux, so the room is dark...)
4. ______________________________  (hint: The comparator says 'dark', the transistor closes and the LED is ON....)
5. ______________________________  (hint: Sanity check: 2 lux is darker than the 10 lux anchor, so the resistanc...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is a sensor whose resistance changes useful for a controller? Why do we also need a separate 'decision' block instead of connecting the LDR straight to the LED?

Answer: ______________________________________________


**B. Numerical.** Using R = 10 000 * (lux / 10) ^ (-0.7), find the LDR resistance at 1 lux and at 1 000 lux. By what factor do they differ? Sanity check the factor.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the app's graph, the curve is steep on the left and nearly flat on the right. What does that say about how well an LDR distinguishes 5 lux from 15 lux compared with 405 lux from 415 lux?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a path light should turn on at dusk. Compare thresholds of 5 lux and 50 lux. Which would you choose and why? Give the LDR resistance at each threshold.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
