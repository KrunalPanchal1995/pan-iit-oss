# Activity sheet: openabel, Session 5: Where is the axis? Finding the flame's symmetry axis from the photo

Name: ____________________   Date: ____________

**Objectives**

- Say what a wrong axis position costs the recovered flame, with and without noise, in pixels and millimetres.
- Build the ring matrix for pixels at any offset from the axis, so that a photo never has to be resampled.
- Find the axis from the photo alone with two finders (the centroid and mirror matching) and grade them against a photo whose true axis you moved yourself.
- Explain why interpolating a noisy photo can fool a finder ("pixel locking"), and fix it by smoothing first.
- Show that finding the axis and then using both halves of the photo reaches the roadmap's 0.045, while one half does not.

## Before you start: predict
In your own words, what do you think happens to the recovered flame when the real axis is two pixels away from the middle of the photo and you do not notice?

______________________________________________________________

## Worked example (fill in as you go)
One row of a photo has seven pixel values I = 0, 2, 6, 9, 7, 3, 1 at positions x = 0, 1, ..., 6. Find the axis with both finders.

1. ______________________________  (hint: centroid = sum(x I) / sum(I) = 90 / 28.)
2. ______________________________  (hint: mirror cost at c = 3 is 6 / 7 = 0.86; at c = 3.5 it is 28 / 6 = 4.67; at c = 2.5 it is 86 / 6 = 14.33.)
3. ______________________________  (hint: a parabola through the three lowest points, spacing 0.5, has its lowest point at 3 + 0.5 (14.33 - 4.67) / (2 [14.33 - 1.71 + 4.67]) = 3.14.)

Final answer: ____________________  (centroid 3.21, mirror matching 3.14)

## Questions
**A. Conceptual.** Why is the brightest pixel a poor estimate of the flame's axis?

Answer: ______________________________________________


**B. Numerical.** A row has the values I = 1, 4, 8, 6, 2 at positions x = 0, 1, 2, 3, 4. Compute the centroid, and the mirror cost at c = 1.5, 2 and 2.5, using only pixels that have a partner inside the row. What does each finder say?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the right panel of the second figure, the boxes "mirror, one half" and "mirror, both halves" use the same axis, yet the first is higher. What does this tell you?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for a candle photo with 3 percent noise and the axis 0.5, 1 and 2 pixels from the middle, run `compare_axis_methods(shift)` and report the mean worst-row error of "assume the middle (one half)", of "mirror axis, both halves" and of "true axis, both halves". When can you skip the axis search?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happens: ____________________
