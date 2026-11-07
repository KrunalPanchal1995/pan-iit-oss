# Activity sheet: openvfx, Session 3: Skin that follows the bones

Name: ____________________   Date: ____________

**Objectives**

- Explain linear blend skinning: a weighted average of bone motions.
- Measure two skinning defects: cracks (largest gap) and thinning (elbow width).
- Predict the thinning at any bend with a hand calculation, cos(b/2).
- Choose a blend zone and bend range that meet a quality limit.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For a bend of 90 degrees and half thickness h = 0.15, find the blended elbow width and compare it with the hand-calculation cos(b/2).

1. ______________________________  (hint: At the elbow x = 1 the weight is w = 1/2. Bone 1 keeps the top point a...)
2. ______________________________  (hint: Blended top point = average = (0.925, 0.075). In the same way the bott...)
3. ______________________________  (hint: Width = distance between them = sqrt(0.15^2 + 0.15^2) = 0.212....)
4. ______________________________  (hint: Rest width = 2h = 0.30, so the ratio is 0.212 / 0.30 = 0.707....)
5. ______________________________  (hint: Hand calculation: cos(90 / 2) = cos 45 = 0.707. They agree....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does averaging the positions from two bones make the elbow thinner, while following a single bone does not?

Answer: ______________________________________________


**B. Numerical.** Use the hand calculation to find the elbow width ratio at a bend of 120 degrees. What width is that for an arm 0.30 thick?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the width graph, at about which bend does the blue curve cross the red 80 percent line? What does that tell an animator?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose a blend zone and the largest whole-degree bend so that the elbow keeps at least 80 percent width and the largest gap stays below 0.08. Justify your choice.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
