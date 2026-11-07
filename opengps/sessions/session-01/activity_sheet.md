# Activity sheet: opengps, Session 1: Two circles meet at two points, three at one

Name: ____________________   Date: ____________

**Objectives**

- Explain why one distance gives a circle, two give two points and three give one.
- Compute the two points where two circles meet.
- Use a third distance to choose the right point.
- Describe what a small error in one distance does to the answer.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Beacons B1 = (0, 40), B2 = (120, 40), B3 = (60, 95) km. A receiver measures d1 = 47.43 km, d2 = 76.49 km and d3 = 71.59 km. Where is it?

1. ______________________________  (hint: d = distance between B1 and B2 = 120 km. Squares of the ranges: r1^2 =...)
2. ______________________________  (hint: a = (120^2 + 2250 - 5850) / (2 x 120) = 10800 / 240 = 45 km....)
3. ______________________________  (hint: h = sqrt(2250 - 45^2) = sqrt(2250 - 2025) = sqrt(225) = 15 km....)
4. ______________________________  (hint: The centres lie on the line y = 40, so the two candidates are (45, 40 ...)
5. ______________________________  (hint: Distance from (45, 55) to B3 is sqrt(15^2 + 40^2) = 42.72 km but r3 = ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do two circles give two points and not one? What would a single extra circle have to avoid to be useful?

Answer: ______________________________________________


**B. Numerical.** A receiver is sqrt(4500) = 67.08 km from both B1 = (0, 40) and B2 = (120, 40). Find the two candidate positions. Then use B3 = (60, 95) with r3 = 25 km to choose.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the distance graph (receiver moving along x at y = 25 km), where do the curves for B1 and B2 cross, and what is the distance there?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you can put the third beacon at (60, 40), (60, 95) or (130, 40) km, with B1 = (0, 40) and B2 = (120, 40). Which choices let a receiver at (45, 25) tell itself from its mirror image (45, 55)? Explain the trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
