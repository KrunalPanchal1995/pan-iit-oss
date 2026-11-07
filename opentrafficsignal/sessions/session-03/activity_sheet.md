# Activity sheet: opentrafficsignal, Session 3: A junction simulator, checked against the formula

Name: ____________________   Date: ____________

**Objectives**

- Simulate a junction with seeded random (Poisson) arrivals, a fixed plan and a simple actuated rule.
- Validate the simulation against the uniform-delay formula (even arrivals) and against conservation of cars.
- Measure how average delay depends on cycle length and on arrival rates, and compare with Webster's optimum cycle.
- Produce and explain a failure case: oversaturation, where queues grow without bound.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Two roads with q = (0.20, 0.10) cars per second, s = 0.5, a fixed plan of 27 s + 27 s of green (C = 60 s). Validate the simulator: (1) even arrivals against the formula of Session 2, (2) conservation, (3) Little's law. Then show how random arrivals change the answer.

1. ______________________________  (hint: Formula from Session 2: 13.86 s average delay per car (15.125 s for th...)
2. ______________________________  (hint: Simulation with even arrivals over 2 hours: 13.44 s, 3.1 percent below...)
3. ______________________________  (hint: Conservation: 1440 + 720 cars arrived, 1433 + 720 departed and 7 + 0 a...)
4. ______________________________  (hint: Little's law: the car delays add up to 29033 car-seconds and the area ...)
5. ______________________________  (hint: Poisson arrivals, 12 seeds: 19.50 s average delay and 18.5 cars larges...)

Final answer: ____________________

## Questions
**A. Conceptual.** Even and Poisson arrivals have the same average flow, yet Poisson arrivals give more delay and longer queues. Why? Could random arrivals ever give less delay than even ones on average?

Answer: ______________________________________________


**B. Numerical.** A two-phase junction has q = (0.25, 0.15) cars per second, s = 0.5 and L = 6 s. Find Y, Webster's cycle and the two greens. One simulation run reports 720 cars arrived on road 2 and 719 departed. How many are still waiting?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the delay-against-cycle graph (q = 0.20 and 0.10, Webster C = 35 s), describe the curve on the left and on the right of its minimum and say what the simulation finds as the best cycle.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the junction of the worked example (q = 0.20 and 0.10) was timed with Webster's cycle for its own demand (C = 35 s). In the evening the demand rises to 1.4 times (q = 0.28 and 0.14). The simulation gives 68.5 s average delay with the old plan. Re-time it with Webster's formula, give the new cycle and greens, and say when you would prefer an actuated rule.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
