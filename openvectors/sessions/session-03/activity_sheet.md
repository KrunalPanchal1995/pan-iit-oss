# Activity sheet: openvectors, Session 3: A river that changes, and a boat that corrects itself

Name: ____________________   Date: ____________

**Objectives**

- Simulate a boat in small time steps with a current that depends on position.
- Compare a fixed heading with a feedback heading that corrects to a target line.
- Validate the simulation against the exact formulas, and test how the answer changes with the time step and the current.
- Find and explain the failure case: a current that is faster than the boat.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Boat 4 m/s, parabolic current with a 3 m/s peak, no wind, fixed heading straight across a 60 m river. Predict the drift and the time exactly, then compare with the simulation. Then add a 0.5 m/s wind.

1. ______________________________  (hint: Time: T = 60 / 4 = 15 s for any current, because the across speed is 4...)
2. ______________________________  (hint: The average current is (2/3) * 3 = 2 m/s, so the drift is 2 * 15 = 30 ...)
3. ______________________________  (hint: Simulation with dt = 0.05 s and Runge-Kutta: 30.000 m after 15.000 s....)
4. ______________________________  (hint: With a 0.5 m/s wind the extra drift is 0.5 * 15 = 7.5 m, so the exact ...)
5. ______________________________  (hint: Simulation versus the exact formula over 21 headings from -40 to 60 de...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the feedback pilot use an integral term (the running sum of the error) as well as the proportional term K x?

Answer: ______________________________________________


**B. Numerical.** Using the exact formula, find the drift of a 4 m/s boat that points straight across a 60 m river with a parabolic current of peak 5 m/s and no wind. Check it against the sensitivity graph.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the sensitivity graph, what is the feedback landing point for peak currents of 3, 5 and 6 m/s, and why does it get worse above 4 m/s?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for the 4 m/s boat, the parabolic current with a 3 m/s peak and a 0.5 m/s wind, choose the gain K (in steps of 0.5) so that the landing is within 2 m and the crossing takes at most 21 s. Justify your choice.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
