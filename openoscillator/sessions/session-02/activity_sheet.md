# Activity sheet: openoscillator, Session 2: Simple harmonic motion, energy and damping

Name: ____________________   Date: ____________

**Objectives**

- Write x = A cos(w t) with w = sqrt(k / m), and explain what each symbol means.
- Follow the exchange of energy between kinetic and potential energy during a swing.
- Tell underdamped, critically damped and overdamped motion apart, and compute the decay envelope.
- Solve a design problem: choose L, k or b to reach a target period or a target decay.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 0.50 kg mass on a spring must swing with a period of 1.0 s. Find k. Then add damping b = 0.5 kg/s and find the damped period, the damping ratio and what fraction of the swing is left after 5 s. Finally find the length of the 'seconds pendulum' with a full period of 2 s.

1. ______________________________  (hint: w = 2 pi / T = 6.283 rad/s, so k = m w^2 = 0.50 * 39.48 = 19.74 N/m....)
2. ______________________________  (hint: Damping b = 0.5 kg/s: gamma = b / (2 m) = 0.5 / 1.0 = 0.5 1/s. Then wd...)
3. ______________________________  (hint: Critical damping is 2 sqrt(k m) = 2 sqrt(19.74 * 0.5) = 6.283 kg/s, so...)
4. ______________________________  (hint: After 5 s the envelope is exp(-gamma * 5) = exp(-2.5) = 0.082, or 8.2 ...)
5. ______________________________  (hint: Seconds pendulum: L = g (T / 2 pi)^2 = 9.81 * (2 / 6.283)^2 = 9.81 * 0...)

Final answer: ____________________

## Questions
**A. Conceptual.** With no damping, the total energy stays constant while kinetic and potential energy change. Where is the energy at the end of the swing and where at the middle? When damping is switched on, where does the lost energy go?

Answer: ______________________________________________


**B. Numerical.** A sensor of mass 0.20 kg must oscillate at 2 Hz on a spring. What stiffness is needed? What pendulum length would give a period of 1.5 s?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the displacement graph for m = 0.5 kg, k = 20 N/m, b = 0.5 kg/s, read the time at which the envelope has fallen to half of its starting value, and compare with the formula.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for the m = 0.5 kg, k = 20 N/m spring, choose a damping b so that the swing is at most 5 percent of its start after 3 s. Compare with critical damping and say what you would pick for a car suspension.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
