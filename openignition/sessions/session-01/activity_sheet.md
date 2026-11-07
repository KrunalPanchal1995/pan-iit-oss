# Activity sheet: openignition, Session 1: Why a mixture waits, then suddenly ignites

Name: ____________________   Date: ____________

**Objectives**

- Explain thermal runaway: heat release speeds up the reaction, which releases more heat.
- Compute an Arrhenius rate constant by hand and in Python.
- Read the ignition delay from a temperature-time curve that is flat and then jumps.
- Predict, from a graph, how a hotter start shortens the delay.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
At a start temperature of 1000 K, find the rate constant k. If there were no heat feedback, how much fuel would be gone after 1 ms? Compare with the fuel burnt at the moment of ignition when the feedback is on.

1. ______________________________  (hint: Ea / (R T) = 150000 / (8.314 * 1000) = 18.04....)
2. ______________________________  (hint: k = 2.5e9 * exp(-18.04) = 36.5 per second....)
3. ______________________________  (hint: Without feedback the temperature stays at 1000 K, so after 1 ms c = ex...)
4. ______________________________  (hint: With feedback, ignition means T has risen by 400 K. Burning all the fu...)
5. ______________________________  (hint: The simulation gives the ignition delay at 1000 K as 1.19 ms....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the mixture wait for a long time and then ignite almost instantly, even though the chemistry is the same all the time? Why does the box without heat feedback never ignite?

Answer: ______________________________________________


**B. Numerical.** Find the rate constant at 1100 K. By what factor is it bigger than at 1000 K? If 10 percent of the fuel burns, by how many kelvin does the box heat up?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the right-hand figure, by what factor does the delay shrink when the start temperature rises from 1000 K to 1050 K? What does the steepness of the curve tell you about the rate?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you need ignition within 0.5 ms. Find the lowest start temperature (in steps of 10 K) that works with a heat release of 1500 K. Then find out whether a richer mixture with 2000 K heat release lets you start cooler, and say what you give up.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
