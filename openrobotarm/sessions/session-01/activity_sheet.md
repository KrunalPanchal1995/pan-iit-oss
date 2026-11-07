# Activity sheet: openrobotarm, Session 1: A robot arm is a chain of links and joints

Name: ____________________   Date: ____________

**Objectives**

- Describe a planar arm by its link lengths and joint angles.
- Explain why joint angles add up down the chain (cumulative angles).
- Compute the gripper position and tool angle from three joint angles, by hand and in Python.
- State the longest reach and decide whether a block can be touched.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Find the gripper position, the tool angle and the distance from the base for q = (30, 40, -20) degrees with L = (0.30, 0.25, 0.15) m.

1. ______________________________  (hint: Cumulative angles: c1 = 30, c2 = 30 + 40 = 70, c3 = 70 - 20 = 50 degre...)
2. ______________________________  (hint: Link 1: 0.30 * (cos 30, sin 30) = 0.30 * (0.866, 0.500) = (0.2598, 0.1...)
3. ______________________________  (hint: Link 2: 0.25 * (cos 70, sin 70) = 0.25 * (0.3420, 0.9397) = (0.0855, 0...)
4. ______________________________  (hint: Link 3: 0.15 * (cos 50, sin 50) = 0.15 * (0.6428, 0.7660) = (0.0964, 0...)
5. ______________________________  (hint: Add the three: x = 0.2598 + 0.0855 + 0.0964 = 0.4417 m and y = 0.1500 ...)
6. ______________________________  (hint: Distance from the base: sqrt(0.4417^2 + 0.4998^2) = 0.667 m, below the...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is the tool angle q1 + q2 + q3, and not just q3? What would the gripper do if only joint 1 turned by 10 degrees?

Answer: ______________________________________________


**B. Numerical.** For q = (90, -90, 0) degrees find the gripper position. Is it on the block at (0.40, 0.30) m?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the second figure, how large is the radius of the circle the gripper runs round, and at which shoulder angle is the gripper's x largest?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a supplier sells 3-link arms with total link length 0.45, 0.60, 0.70 and 0.85 m. The block is 0.50 m from the base and you want at least 0.10 m of spare reach. Which arm do you choose, and what do you give up with a longer one?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
