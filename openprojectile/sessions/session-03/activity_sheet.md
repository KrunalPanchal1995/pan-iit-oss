# Activity sheet: openprojectile, Session 3: Air drag: an RK4 simulation, validated

Name: ____________________   Date: ____________

**Objectives**

- Write the equations of motion with quadratic air drag and say what each term means.
- Solve them with a Runge-Kutta (RK4) step and validate the solver against the exact no-drag results and an energy balance.
- Find numerically the launch angle for the longest range and explain why drag lowers it below 45 degrees.
- Use terminal speed, the drag coefficient and wind to judge how sensitive a shot is, and recognise a failure of a large step with explicit Euler.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A cricket ball (m = 0.16 kg, d = 0.07 m, Cd = 0.4, approximate) is hit from 1 m at 35 m/s and 40 degrees. Find k, the terminal speed, the drag deceleration at launch, and then the range from the RK4 solver.

1. ______________________________  (hint: A = pi * 0.07^2 / 4 = 0.003848 m^2....)
2. ______________________________  (hint: k = 0.5 * 1.2 * 0.4 * 0.003848 = 9.24e-4 kg/m, so k/m = 9.24e-4 / 0.16...)
3. ______________________________  (hint: Terminal speed v_t = sqrt(2 * 0.16 * 9.81 / (1.2 * 0.4 * 0.003848)) = ...)
4. ______________________________  (hint: Drag deceleration at launch = (k/m) v^2 = 0.00577 * 35^2 = 7.07 m/s^2,...)
5. ______________________________  (hint: RK4 (dt = 0.01 s) gives a range of 83.5 m, a flight of 4.14 s and a pe...)
6. ______________________________  (hint: Energy check: E + W_drag differs from E(0) by a relative 2e-12 along t...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does air drag lower the best launch angle below 45 degrees? Think about what a high, long flight costs.

Answer: ______________________________________________


**B. Numerical.** For a slightly rougher ball with Cd = 0.5 (same mass and diameter), find k, the terminal speed, and the drag deceleration at 30 m/s as a multiple of g.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the range-versus-angle graph at 35 m/s from 1 m, the dashed (no drag) curve peaks at 44.8 degrees and 125.9 m, the solid curve at 41.5 degrees and 83.6 m. What percentage of the range does drag remove and what happens to the shape of the peak?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the rope is 70 m from the batter and the ball is struck from 1.0 m. Find the lowest speed that makes a six in still air, and say what speed and angle you would plan for a 5 m/s headwind. Comment on the margin.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
