# Activity sheet: openpathplanner, Session 2: Graphs, Dijkstra and A*

Name: ____________________   Date: ____________

**Objectives**

- Turn a grid into a graph with edge costs 1 and sqrt 2 (4- or 8-connected).
- Write BFS and Dijkstra (with heapq) and check them on hand-checkable grids.
- Explain why an admissible heuristic keeps A* optimal, and check admissibility numerically.
- Compare nodes expanded by Dijkstra and A*, and use the comparison to solve a design problem.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
On the 5 by 3 grid with a wall in column 2 (gap only in the bottom row), the robot at (0, 0) must reach (4, 1). Find the cheapest cost with 4 moves and with 8 moves, and compare with the Manhattan lower bound.

1. ______________________________  (hint: Grid rows: 'S.#..', '..#.G', '.....'. Only row 2 passes the wall at co...)
2. ______________________________  (hint: Manhattan distance from (0, 0) to (4, 1) is 4 + 1 = 5. This is a lower...)
3. ______________________________  (hint: 4 moves: go down 2 rows to (0, 2), right 4 to (4, 2), up 1 to (4, 1): ...)
4. ______________________________  (hint: 8 moves: (0, 0) down to (0, 1) costs 1, diagonal to (1, 2) costs sqrt ...)
5. ______________________________  (hint: Total = 1 + sqrt 2 + 1 + 1 + sqrt 2 = 3 + 2 sqrt 2 = 5.828. The diagon...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does an admissible heuristic keep A* optimal, and what goes wrong if h overestimates?

Answer: ______________________________________________


**B. Numerical.** For a goal dx = 3 columns and dy = 1 row away on an empty 8-connected floor, compute the Manhattan, octile and straight-line distances and say which are admissible.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the density graph, how does the work of Dijkstra change as the density of obstacles grows, and why does A* expand fewer nodes at every density?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: in the 30 by 25 serpentine warehouse you need at least 200 shelf cells and a path cost of at most 170. Which aisle width (1 to 5 cells) do you choose, and what is the trade-off?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
