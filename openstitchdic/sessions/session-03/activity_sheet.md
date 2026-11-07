# Activity sheet: openstitchdic, Session 3: A mini stereo-DIC pipeline, validated against a known motion

Name: ____________________   Date: ____________

**Objectives**

- Build a pipeline: camera model, homography to a common grid, subset correlation, time alignment, merge.
- Measure displacement with ZNCC and a parabola, and state its error against a known truth.
- Quantify how skipping the homography or the time alignment inflates the error.
- Handle edge cases: extrapolation outside the sampled time range and occlusion at the picture border.
- Use your own pictures through the data folder.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A subset's ZNCC scores at whole-pixel shifts 2, 3 and 4 are 0.80, 0.95 and 0.90. What sub-pixel shift does the parabola give? And is the pipeline's whole recipe, camera model plus homography, consistent for the synthetic pair?

1. ______________________________  (hint: The best whole-pixel shift is 3 (score 0.95); its neighbours are c(-1)...)
2. ______________________________  (hint: delta = (0.80 - 0.90) / (2 * (0.80 - 2 * 0.95 + 0.90)) = (-0.10) / (2 ...)
3. ______________________________  (hint: The shift is 3 + 0.25 = 3.25 px....)
4. ______________________________  (hint: For the synthetic pair, warping picture B onto A's pixel grid with the...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does correlating each frame with the previous frame and adding up the steps give a larger error than correlating each frame with frame 0?

Answer: ______________________________________________


**B. Numerical.** ZNCC scores 0.60, 0.90 and 0.85 at shifts 4, 5 and 6. Find the sub-pixel shift. Give the unit.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the error-budget bar chart (step-like motion), read the five errors: homography with Makima, homography with nearest, affine with Makima, and resize with nearest. What does each bar tell you to fix first?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: part of the sample leaves camera B's picture, so 3 of the 9 subsets cannot be measured in B. What do you do with the missing pixels, and what do you do about times where only one camera has data? Justify with the numbers.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
