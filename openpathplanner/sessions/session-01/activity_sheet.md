# Activity sheet: openpathplanner, Session 1: The shortest path is not the straight line

Name: ____________________   Date: ____________

**Objectives**

- Describe a warehouse floor as a grid of free and blocked cells.
- Explain why the best route around a wall is longer than the straight line.
- Find a shortest route by breadth-first search (BFS) and read off its length in steps.
- Read a graph of route length against the position of the door in a wall.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The door is in row 6 and the shelf is in row 2. Find the number of steps, the straight-line distance and the extra steps caused by the wall.

1. ______________________________  (hint: The robot starts at column 1, row 1. The shelf is at column 10, row 2....)
2. ______________________________  (hint: To pass the wall it must stand in row 6: from row 1 down to row 6 is |...)
3. ______________________________  (hint: After the door it must go from row 6 to the shelf row 2: |6 - 2| = 4 s...)
4. ______________________________  (hint: Total = 9 + 5 + 4 = 18 steps. BFS in the checkpoint also returns 18....)
5. ______________________________  (hint: Straight line = sqrt(9^2 + 1^2) = sqrt(82) = 9.06 cells. On an empty f...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is the shortest route to the shelf longer than the straight line, and why can BFS stop as soon as it reaches the shelf?

Answer: ______________________________________________


**B. Numerical.** The door is in row 4 and the shelf is in row 2. How many steps is the route, and what is the straight-line distance? Check that the route is not shorter than the straight line.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the graph of route length against door row (shelf in row 2), which door rows give the shortest route, what is that length, and why is it not smaller?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: two kinds of orders go to shelves in row 2 and row 6, equally often. Choose the door row that minimises the total steps of one trip to each shelf. What is the total? What real-world factor does this model ignore that might change your choice?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
