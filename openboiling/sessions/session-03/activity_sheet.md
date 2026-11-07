# Activity sheet: openboiling, Session 3: A heated plate, the burnout and the growing bubble

Name: ____________________   Date: ____________

**Objectives**

- Step a lumped plate through time with a piecewise boiling curve and see the transitions between regimes.
- Show that power-controlled heating burns out above the critical heat flux while temperature-controlled heating does not, and describe the hysteresis.
- Validate the solver against an exact solution and against energy conservation.
- Check that a bubble grows as the square root of time with a log-log fit, and use a simulation to choose a safe heater power.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Apply a heat flux of 600 kW/m2 to the reference plate. Find the steady wall superheat by hand and check it against the simulation; then check the stepper against the exact solution for a constant 3000 W/m2.

1. ______________________________  (hint: At steady state q_in = C dT^3 with C = 1.1e6 / 30^3 = 40.74 W/(m2 K3)....)
2. ______________________________  (hint: dT = (600 000 / 40.74)^(1/3) = 14 727^(1/3) = 24.5 K, so the plate is ...)
3. ______________________________  (hint: Simulation: after a 60 s run with the heat flux ramped in over 10 s, d...)
4. ______________________________  (hint: For q_in = 3000 W/m2 the plate is in natural convection and the exact ...)
5. ______________________________  (hint: The stepper's maximum error over 60 s is 0.0002 K; the energy in, out ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a power-controlled heater burn out when the heat flux exceeds the critical heat flux, while a temperature-controlled one does not?

Answer: ______________________________________________


**B. Numerical.** Use the hand calculation to find the steady superheat for 1000 kW/m2 on the reference surface and for the same flux on the fouled surface (factor 0.6). What happens on the fouled surface?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the hysteresis figure the jump up is at about 1100 kW/m2 and the return at about 13 kW/m2. What does this tell an operator who sees the plate burn out and then reduces the power by 20 percent?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a 0.04 m2 heater must be safe on a new and a fouled surface with a 20 percent power overshoot, at most 60 percent of the CHF and at most 25 K superheat. Find the largest safe power on a 1 kW grid. Is 60 percent of the CHF alone sufficient?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
