# Activity sheet: openlinkage, Session 2: The four-bar linkage as equations

Name: ____________________   Date: ____________

**Objectives**

- Apply Grashof's rule to classify a four-bar linkage and verify it by brute force.
- Solve the position problem two ways (circle-circle and loop closure with Newton's method) and compare.
- Compute and interpret the transmission angle, and say what the 40 to 140 degree guideline means.
- Solve a design problem: choose link lengths so the rocker swings through a given angle.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For (a, b, c, d) = (4, 1, 4, 5) and a crank angle of 90 degrees find B, the transmission angle, and check Grashof's rule.

1. ______________________________  (hint: Grashof: s = 1, l = 5, p + q = 4 + 4 = 8, and s + l = 6 <= 8. The shor...)
2. ______________________________  (hint: At 90 degrees A = (0, 1) and O4 = (4, 0), so D^2 = 16 + 1 = 17 and D =...)
3. ______________________________  (hint: x = (c^2 - d^2 + D^2)/(2D) = (16 - 25 + 17)/8.2462 = 0.9701 and h = sq...)
4. ______________________________  (hint: B = A + x e + h n = (0.9412 + 0.9412, 1 - 0.2353 + 3.7647) = (1.882, 4...)
5. ______________________________  (hint: Transmission angle: cos(mu) = (c^2 + d^2 - D^2)/(2cd) = (16 + 25 - 17)...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a linkage that satisfies Grashof's rule with the shortest bar as the coupler not let the crank turn a full circle?

Answer: ______________________________________________


**B. Numerical.** Classify the linkage (a, b, c, d) = (2, 5, 4, 6) with Grashof's rule. Which bar can turn fully?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the transmission-angle graph for d = 5 (crank 1.346) the lowest point is 31.91 degrees. At which crank angle does it occur, and does the linkage meet the 40 to 140 degree guideline?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with a = 4 and c = 4 you may choose the rocker length d = 5 or d = 3.5. In each case find the crank length for a 40 degree swing, and choose one. Justify your choice.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
