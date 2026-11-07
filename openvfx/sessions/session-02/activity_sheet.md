# Activity sheet: openvfx, Session 2: Bones rotate about joints, and joints chain

Name: ____________________   Date: ____________

**Objectives**

- Rotate points about a joint that is not at the origin.
- Compute where the elbow and hand are from two joint angles.
- Use the reach formula to find the longest and shortest reach of the arm.
- Solve the inverse problem: which angles put the hand on a target?

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
With L1 = 0.30 m, L2 = 0.25 m, a = 40 degrees and b = 50 degrees, find the elbow, the hand and the shoulder-to-hand distance.

1. ______________________________  (hint: Elbow = 0.30 * (cos 40, sin 40) = 0.30 * (0.766, 0.643) = (0.230, 0.19...)
2. ______________________________  (hint: The forearm points at a + b = 90 degrees, so its offset is 0.25 * (cos...)
3. ______________________________  (hint: Hand = elbow + offset = (0.230, 0.443) m....)
4. ______________________________  (hint: Check with the reach formula: |h|^2 = 0.09 + 0.0625 + 2*0.30*0.25*cos ...)
5. ______________________________  (hint: Check with the coordinates: sqrt(0.230^2 + 0.443^2) = 0.499 m. The two...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the forearm point at angle a + b rather than just b?

Answer: ______________________________________________


**B. Numerical.** For L1 = 0.30 m, L2 = 0.25 m, a = 90 degrees and b = -90 degrees, find the hand position and its distance from the shoulder.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the reach graph, what are the largest and smallest shoulder-to-hand distances, and at which elbow angles?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: find joint angles that put the hand on (0.35, 0.20) m. How many solutions are there? Is (1.0, 0.0) m reachable?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
