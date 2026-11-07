# Activity sheet: opendcmotor, Session 3: A motor in time: simulation, PWM and sizing a robot drive

Name: ____________________   Date: ____________

**Objectives**

- Write the coupled electrical and mechanical equations and solve them with RK4.
- Validate the simulation against the steady-state line, against the time-constant formulas and against energy conservation.
- Explain PWM speed control, the inrush current at start, and the stall failure case with numbers.
- Size a motor and gearbox for a robot climbing a slope, using a sweep and a time-domain check.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 12 V motor (R = 2.0 ohm, L = 5 mH, k = 0.05, b = 5e-5, J = 2e-4 kg m^2) starts from rest with no load. Find tau_e, tau_m, the steady speed and current, then check them against the RK4 simulation and the energy balance.

1. ______________________________  (hint: tau_e = L / R = 0.005 / 2 = 2.5 ms....)
2. ______________________________  (hint: tau_m = J R / (k^2 + b R) = 2e-4 x 2 / (0.0025 + 0.0001) = 4e-4 / 0.00...)
3. ______________________________  (hint: Steady speed = (k V / R) / (k^2/R + b) = 0.3 / 0.0013 = 230.77 rad/s; ...)
4. ______________________________  (hint: The first-order approximation says 63.2 percent of the final speed (14...)
5. ______________________________  (hint: Simulation (RK4, dt = 0.1 ms): the speed reaches 63.2 percent at 154.0...)
6. ______________________________  (hint: Energy: in one second the supply delivers 13.41 J; the sum of winding ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is the speed ripple in PWM almost zero while the current ripple is clearly visible?

Answer: ______________________________________________


**B. Numerical.** The load inertia is doubled to J = 4e-4 kg m^2. Find the new mechanical time constant, and the time for the speed to reach 63.2 percent. How does the steady speed change?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the PWM current graph, what happens to the ripple when you double the frequency from 1000 to 2000 Hz at D = 0.5? What does the hand estimate predict and why does it fall?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a 5 kg robot with the same wheels (radius 0.05 m, two driven wheels, c = 0.03) must climb 25 degrees at 0.5 m/s or more with at most 1.5 A per motor and a starting margin of at least 1.5. Which gear ratios work? Which would you choose?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
