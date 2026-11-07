# Activity sheet: openheights, Session 3: Simulating noisy readings, hills and averages

Name: ____________________   Date: ____________

**Objectives**

- Simulate noisy phone readings from exact geometry and recover the height.
- Average n readings and report a standard error s / sqrt(n).
- Validate the error formulas for one and two angles against a Monte Carlo simulation.
- Correct a measurement made on a slope, and identify the failure near 90 degrees.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
(a) A 30 m tower stands 30 m (horizontal) up a 10 degree slope from you, eye height 1.6 m. The true top angle is 48.32 degrees. Find the height ignoring the slope and with the slope correction. (b) The flagpole data (12 readings at 18.0 m, eye 1.55 m) give heights with a mean of 9.38 m and a standard error of 0.035 m. How big is the tape error contribution for a 0.1 m tape error, and what is the combined uncertainty?

1. ______________________________  (hint: (a) Slope distance s = 30 / cos 10 degrees = 30.46 m. Ignoring the slo...)
2. ______________________________  (hint: (a) With the correction: 30 x (tan 48.32 - tan 10) + 1.6 = 30 x (1.123...)
3. ______________________________  (hint: (b) The tape error enters like a distance error: 0.1 m x tan(mean angl...)
4. ______________________________  (hint: (b) Combine in quadrature: sqrt(0.035^2 + 0.0435^2) = 0.056 m....)
5. ______________________________  (hint: (b) Report: 9.38 +/- 0.06 m....)

Final answer: ____________________

## Questions
**A. Conceptual.** Your phone is tilted so that every reading is 1 degree too large. Does averaging 100 readings fix it? What would?

Answer: ______________________________________________


**B. Numerical.** At 45 degrees and 28.4 m, one reading gives a height error of 0.496 m. How many readings must you average to bring the standard error to 0.1 m or below? What do you get with 25?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the Monte Carlo results for far reading at 40 m, the one-angle standard deviation is 0.52 m while the two-angle method gives 2.64 m for a 10 m walk and 0.74 m for a 30 m walk. Explain what the graph shows and when the two-angle method is worth using.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a 30 m tower on a 10 degree slope, a clinometer good to 0.5 degrees, and a limit of 0.15 m on the uncertainty of the mean. Choose the horizontal distance and the number of readings. What could go wrong at 3 m?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
