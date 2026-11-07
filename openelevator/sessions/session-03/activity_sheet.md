# Activity sheet: openelevator, Session 3: Simulating the whole lift: torque limit, comfort and energy

Name: ____________________   Date: ____________

**Objectives**

- Simulate a cable-counterweight lift step by step with a motor force limit.
- Measure comfort by the peak acceleration and the peak jerk the passengers actually feel.
- Validate the simulation against the exact travel-time formula and an energy balance, including regeneration.
- Study how load and counterweight balance change energy and comfort, and choose a motor for a building.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A half-loaded car (400 kg of passengers) rides 31.5 m up with maximum speed 2.5 m/s, acceleration 1.0 m/s^2 and jerk limit 1.5 m/s^3. (1) What travel time does the formula give and what does the simulation give? (2) What mechanical work should the motor do, and does the simulation agree? (3) A full car (800 kg) goes down the same 31.5 m: how much energy is fed back?

1. ______________________________  (hint: Formula: T = d / v + v / a + a / j = 31.5 / 2.5 + 2.5 / 1.0 + 1.0 / 1....)
2. ______________________________  (hint: Unbalanced mass = 1000 + 400 - 1360 = 40 kg. Work = 40 * 9.81 * 31.5 =...)
3. ______________________________  (hint: Full car going down: unbalanced mass = 1000 + 800 - 1360 = 440 kg, so ...)
4. ______________________________  (hint: Energy fed back = eta * 136.0 kJ = 0.85 * 136.0 = 115.6 kJ, which is w...)
5. ______________________________  (hint: Comfort check: the simulated peak acceleration is 1.04 m/s^2 and the p...)

Final answer: ____________________

## Questions
**A. Conceptual.** The trapezoid plan never asks for more than 1.0 m/s^2, yet the simulated trapezoid ride peaks at 1.41 m/s^2 with a very large jerk. Why?

Answer: ______________________________________________


**B. Numerical.** A car carrying 200 kg goes up 31.5 m. Use the energy balance to find the mechanical work, and say whether the grid draws or receives energy over the whole ride.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the energy-against-load figure, why does the 'up' curve for the 1360 kg counterweight cross zero at a load of 360 kg, and what does a lighter counterweight do?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for the 10-storey building (31.5 m), the car has 1000 kg, the rated load is 800 kg, the counterweight is 1360 kg. Choose the smallest motor force limit from 6000, 7000, 7500, 8000 and 9000 N and the profile, so that the comfort score is below 1 and the motor never saturates. Give the peak electrical power and one trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
