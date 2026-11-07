# Activity sheet: openneuralode, Session 1: A rule for change: dx/dt = f(x)

Name: ____________________   Date: ____________

**Objectives**

- Explain what the rule dx/dt = f(x) says and draw it as a field of arrows.
- Follow the arrows step by step to get a path.
- Read the arrows back from recorded points, which is the idea behind learning f from data.
- Read a spiral in the position-velocity plane as a mass that loses energy to friction.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For k = 4 and c = 0.4, find the arrow at the state (x, v) = (1 m, 0) and at (0, 2 m/s), and take one step of 0.1 s along the first arrow.

1. ______________________________  (hint: At (1, 0): dx/dt = v = 0 and dv/dt = -4 * 1 - 0.4 * 0 = -4 m/s^2. The ...)
2. ______________________________  (hint: At (0, 2): dx/dt = 2 m/s and dv/dt = -4 * 0 - 0.4 * 2 = -0.8 m/s^2. Th...)
3. ______________________________  (hint: One step of 0.1 s from (1, 0): new state = (1, 0) + 0.1 * (0, -4) = (1...)
4. ______________________________  (hint: Check by thought: after 0.1 s the mass has barely moved (still about 1...)

Final answer: ____________________

## Questions
**A. Conceptual.** At the state (1 m, 0) the arrow is (0, -4). Why is the first number zero even though the mass is about to move?

Answer: ______________________________________________


**B. Numerical.** For k = 4 and c = 0.4, find the arrow at (0, 2 m/s) and the state after one step of 0.1 s along it. Give units and check that the answer is reasonable.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the phase view, why does the path spiral inwards when friction c is above 0 and form a closed loop when c = 0? Where would the path end?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you record the mass with a sensor that gives a snapshot every dt seconds, and you want the arrows read from neighbouring snapshots to be within 1 percent of the true rule. Is dt = 0.25 s good enough? Is 0.1 s?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
