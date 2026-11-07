# Activity sheet: openpathplanner, Session 3: Continuous space: RRT, RRT* and validation

Name: ____________________   Date: ____________

**Objectives**

- Test whether a segment collides with a circle or a rectangle, and verify the tests on known cases.
- Build an RRT with a seeded random generator and smooth its path by shortcutting.
- Validate planners against the exact shortest path around a wall (a polyline through its corners).
- Measure a failure case (narrow passage) and the effect of step size and iterations.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A thin wall (x from 4.8 to 5.2) rises from below the map to a height of 6 m. The robot starts at (1, 1) and the goal is at (9, 1). Find the exact shortest path and compare it with the straight line.

1. ______________________________  (hint: The shortest path over the top is a polyline: start, left top corner (...)
2. ______________________________  (hint: First leg: dx = 4.8 - 1 = 3.8 and dy = 6 - 1 = 5, so length = sqrt(3.8...)
3. ______________________________  (hint: Last leg is the mirror image: 6.280 m. The segment between the corners...)
4. ______________________________  (hint: Total = 2 * 6.280 + 0.4 = 12.960 m. A visibility-graph Dijkstra in the...)
5. ______________________________  (hint: The straight line is 8 m, so the wall adds 4.960 m. Grid A* with 0.1 m...)

Final answer: ____________________

## Questions
**A. Conceptual.** RRT is probabilistically complete but not optimal; A* is optimal on the grid. Explain what each statement means and why neither planner gives both properties for free.

Answer: ______________________________________________


**B. Numerical.** A thin wall (x from 4.8 to 5.2, height 6 m) has the start at (1, 3) and goal at (9, 3). Compute the exact shortest path length. Check it against the 8 m straight line.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the RRT* cost graph, what happens to the best path length between 500 and 3000 iterations, and can it ever go below the red dashed line?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the narrow-passage map has a wall with a gap. Over 100 seeds with 1000 iterations and step 0.5 m, RRT succeeds 12 times for a 0.05 m gap, 33 for 0.1 m, 82 for 0.3 m and 100 for 1 m. A robot needs a gap of at least 0.3 m anyway. Which settings would you choose and what does the failure rate tell you about trusting RRT?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
