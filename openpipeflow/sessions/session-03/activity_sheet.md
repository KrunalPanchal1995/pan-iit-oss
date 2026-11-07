# Activity sheet: openpipeflow, Session 3: A town network, solved and validated

Name: ____________________   Date: ____________

**Objectives**

- Describe a looped pipe network by its pipes, nodes, heads and demands.
- Solve the flows with the Hardy Cross loop correction (Newton's method) and compute the pressure at every node.
- Validate the solver: single-pipe agreement, mass conservation at nodes, zero head change around the loop, symmetry and an analytic laminar result.
- Test the sensitivity to roughness and viscosity and find a failure case.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The tank (level 70 m) feeds node A through a 1200 m, 200 mm main (roughness 0.15 mm). Pipes 2, 3 and 4 are 125 mm. The town takes 30 L/s (18 L/s at B, 12 L/s at C). Find the main-pipe loss and the pressure head at A by hand, then check the numerical flows and pressure at the other nodes.

1. ______________________________  (hint: Main pipe: Q = 0.030 m^3/s, D = 0.200 m, v = 4(0.030) / (pi (0.2)^2) =...)
2. ______________________________  (hint: Re = 0.955 x 0.2 / 1.0e-6 = 190 986 and e/D = 0.00075, so Swamee-Jain ...)
3. ______________________________  (hint: h1 = f (L/D) v^2 / (2 g) = 0.02021 x (1200 / 0.2) x 0.04648 = 5.64 m....)
4. ______________________________  (hint: Head at A = 70 - 5.64 = 64.36 m; street level 20 m, so the pressure he...)
5. ______________________________  (hint: The program's Hardy Cross finds the loop flow in 4 iterations: Q2 = 16...)
6. ______________________________  (hint: Checks: at node B the inflow is 16.17 + 1.83 = 18.00 L/s, equal to its...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why must the head losses around a closed loop add up to zero, and what does the sign of the flow in the cross pipe (pipe 4) tell you?

Answer: ______________________________________________


**B. Numerical.** For the default network at 30 L/s, the flow in pipe 3 is 13.83 L/s and in pipe 2 is 16.17 L/s. Check the continuity at node A and find the speed in pipe 3 (125 mm).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the pressure-against-demand graph, where does the worst node pressure cross the 20 m target with the default pipes, and what does the shape of the curve say?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the town must serve 50 L/s with every node at 20 m or more. With 200 mm main and 125 mm branches, does it work? Choose a main from 200, 220, 250 mm and a branch from 125, 150 mm and justify.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
