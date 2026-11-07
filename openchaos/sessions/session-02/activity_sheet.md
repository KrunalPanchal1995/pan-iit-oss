# Activity sheet: openchaos, Session 2: Equations, energy and a trustworthy simulation

Name: ____________________   Date: ____________

**Objectives**

- Write the two angular accelerations of a double pendulum for general masses and lengths.
- Compute the kinetic, potential and total energy and use energy drift to test a simulation.
- Compute the two normal-mode frequencies of the linearised system and compare them with the simulation.
- Choose a time step so that the energy drift stays below a tolerance.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For equal masses (1 kg) and equal rods (1 m), find the two small-swing frequencies and periods, and check them against a simulation of amplitude 0.001 rad.

1. ______________________________  (hint: For equal masses and rods w^2 = (g / l)(2 -/+ sqrt 2) with g / l = 9.8...)
2. ______________________________  (hint: Slow mode: w^2 = 9.81 x 0.5858 = 5.747 s^-2, so w = 2.397 rad/s and th...)
3. ______________________________  (hint: Fast mode: w^2 = 9.81 x 3.4142 = 33.49 s^-2, so w = 5.787 rad/s and th...)
4. ______________________________  (hint: Mode shapes: theta2 / theta1 = +1.414 for the slow mode and -1.414 for...)
5. ______________________________  (hint: Start the simulation at rest with theta1 = 0.001 rad and theta2 = 0.00...)

Final answer: ____________________

## Questions
**A. Conceptual.** If a simulation keeps the total energy constant to 1e-9, does that prove it is correct? What else would you test?

Answer: ______________________________________________


**B. Numerical.** Find the total energy of a double pendulum with m1 = m2 = 1 kg, l1 = l2 = 1 m, released from rest with both rods at 60 degrees. Then repeat for 90 degrees. Give units and say whether the signs make sense.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the drift-versus-step graph, which of the tested steps keeps the energy error below 1e-5 over 20 s, and by about what factor does the error fall when you halve h from 0.01 s to 0.005 s?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose a step for a 20 s run released at 120 degrees with energy error below 1e-6. Compare the cost with the step that gives 1e-5. State the trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
