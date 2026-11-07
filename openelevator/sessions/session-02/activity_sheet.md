# Activity sheet: openelevator, Session 2: Motion profiles, comfort limits and motor power

Name: ____________________   Date: ____________

**Objectives**

- Compute the travel time of a trapezoid profile and of a jerk-limited S-curve profile.
- Explain jerk and why limiting it makes a ride feel smoother but a little slower.
- Compute the motor power with a counterweight, P = (m_car + m_load - m_cw) g v / efficiency.
- Design the fastest comfortable ride between two floors, then for a 20-floor express.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Two floors are 3.5 m apart. With a maximum speed of 2.5 m/s, acceleration limit 1.0 m/s^2 and jerk limit 1.5 m/s^3, find the S-curve travel time and the cruise speed reached. Then find the motor power at that speed for a full car (1000 kg car, 800 kg load, 1360 kg counterweight, eta = 0.85).

1. ______________________________  (hint: Check the full speed first: reaching 2.5 m/s needs Ta = 2.5 / 1.0 + 1....)
2. ______________________________  (hint: Assume the acceleration reaches 1.0 m/s^2. Then v^2 + (a^2 / j) v - a ...)
3. ______________________________  (hint: v = (-0.6667 + sqrt(0.4444 + 14)) / 2 = (-0.6667 + 3.8006) / 2 = 1.567...)
4. ______________________________  (hint: Ta = 1.567 / 1.0 + 1.0 / 1.5 = 2.234 s and, with no cruise, T = 2 Ta =...)
5. ______________________________  (hint: Unbalanced mass = 1000 + 800 - 1360 = 440 kg. P = 440 * 9.81 * 1.567 /...)

Final answer: ____________________

## Questions
**A. Conceptual.** A trapezoid ride and an S-curve ride have the same peak acceleration. Why does the S-curve feel better, and what does it cost?

Answer: ______________________________________________


**B. Numerical.** For a 14 m ride with maximum speed 2.0 m/s, a = 1.0 m/s^2 and j = 1.5 m/s^3, find the S-curve travel time. Compare with the trapezoid.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the time-versus-distance figure, why does the gap between the two curves stay constant for long rides but the S-curve is relatively slower for short rides?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: (1) What is the fastest ride between two floors 3.5 m apart if the comfort limits are a <= 1.5 m/s^2 and j <= 2.0 m/s^3? (2) For the 20-floor express (66.5 m) with a top speed of 4 m/s and the original limits (1.0 and 1.5), find the ride time and the cruise motor power for a full car. State one trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
