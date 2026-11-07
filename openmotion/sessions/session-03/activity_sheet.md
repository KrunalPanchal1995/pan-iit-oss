# Activity sheet: openmotion, Session 3: Differentiating and integrating noisy data

Name: ____________________   Date: ____________

**Objectives**

- Estimate velocity and acceleration from sampled positions with finite differences.
- Predict how measurement noise and the sampling step change the error, and check it against a known motion.
- Use a local polynomial fit to differentiate while smoothing, and choose its window.
- Explain why integrating is safe but differentiating magnifies noise, and find the limit where sampling is too coarse.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For dt = 0.05 s and sigma = 0.02 m, predict the velocity and acceleration errors of plain finite differences, then measure them on simulated data, then smooth with a 17-point cubic fit (h = 8).

1. ______________________________  (hint: Predicted velocity error: sigma / (sqrt(2) dt) = 0.02 / (1.414 * 0.05)...)
2. ______________________________  (hint: Predicted acceleration error: sqrt(6) sigma / dt^2 = 2.449 * 0.02 / 0....)
3. ______________________________  (hint: Measured on 401 simulated samples (seed 1): velocity RMS error 0.274 m...)
4. ______________________________  (hint: Truncation check without noise: the error stays below dt^2 / 6 * 3 * 1...)
5. ______________________________  (hint: Smoothing with h = 8 (window 0.85 s): velocity error 0.040 m/s and acc...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is differentiating noisy data much worse than integrating it? Explain with one sentence about what each operation does to random errors.

Answer: ______________________________________________


**B. Numerical.** For sigma = 0.02 m, predict the noise errors of the velocity and the acceleration if the sampling step is halved from 0.05 s to 0.025 s. By what factors do they change?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the error-against-step graph (velocity, central difference), why does the noisy curve have a minimum near dt = 0.3 s? What happens at dt = 2 s even without noise?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with sigma = 0.02 m and dt = 0.05 s, choose a window length for the local cubic fit so that the acceleration error is below 0.5 m/s^2. Which windows work, and what is the trade-off?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
