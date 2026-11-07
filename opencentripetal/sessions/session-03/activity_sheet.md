# Activity sheet: opencentripetal, Session 3: A simulated car on a curve, checked against the formulas

Name: ____________________   Date: ____________

**Objectives**

- Build a time-stepping simulation of a car whose tyre force is limited by a friction circle.
- Validate it against the analytic limits (flat, banked, with and without friction) and against energy conservation.
- Explain the effect of braking or accelerating in a bend, and of dry, wet and icy roads, using the simulation.
- Reproduce the minimum speed at the top of a roller-coaster loop, sqrt(g r), and set a speed limit with a safety margin.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For a flat wet curve (mu = 0.4, R = 100 m) predict the top speed by hand, then find it with the simulation, and decide whether the simulation is trustworthy. Then predict where a car entering 30 percent too fast ends up after 6 s.

1. ______________________________  (hint: Hand calculation: v = sqrt(mu g R) = sqrt(0.4 * 9.81 * 100) = 19.81 m/...)
2. ______________________________  (hint: Simulation: `sim_limit(100, 0.4, 0.0, 'max')` bisects on the start spe...)
3. ______________________________  (hint: Banked check: for a 30 degree bank with mu = 0.3 the simulation gives ...)
4. ______________________________  (hint: Energy check: with mu = 0 on a 20 degree bank the energy per kg stays ...)
5. ______________________________  (hint: Failure case: entering at 1.3 times the limit, 92.7 km/h = 25.75 m/s, ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does braking in the middle of a bend make a slide more likely, even though braking reduces the speed?

Answer: ______________________________________________


**B. Numerical.** A road with mu = 0.4 has a flat curve of radius 100 m. Find the speed at which a car accelerating at 2 m/s^2 loses grip. Compare with the speed without acceleration.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the radius graph, the dry, wet and ice lines are curves that rise with radius. By what factor does the limit change if the radius is multiplied by 4, and if mu is divided by 4 (wet to ice)?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a loop of a roller coaster has radius 10 m. What minimum speed is needed at the top and at the bottom? Choose a design speed at the bottom with a 10 percent margin and say what the passengers feel at the top.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
