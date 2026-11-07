# Activity sheet: openstereodic, Session 2: From matched pixels to millimetres: triangulation and sub-pixel matching

Name: ____________________   Date: ____________

**Objectives**

- Triangulate a matched pixel pair into a 3D point with a calibrated camera pair.
- Turn a disparity error into a depth error with dZ = Z^2 dd / (f B).
- Find the match of a small patch by zero-normalised cross-correlation.
- Refine the match to a fraction of a pixel and measure the bias of that refinement.
- Choose a baseline for a required depth accuracy (inverse problem).

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
With f = 1000 px, B = 0.04 m and principal point (160, 80): a matched pair is uL = 200, vL = 100, uR = 120. Find the 3D point. If the disparity is uncertain by 0.05 px, what is the depth uncertainty?

1. ______________________________  (hint: Disparity d = 200 - 120 = 80 px....)
2. ______________________________  (hint: Z = f B / d = 1000 * 0.04 / 80 = 0.5 m....)
3. ______________________________  (hint: X = (200 - 160) * 0.5 / 1000 = 0.02 m and Y = (100 - 80) * 0.5 / 1000 ...)
4. ______________________________  (hint: Depth error dZ = Z^2 dd / (f B) = 0.25 * 0.05 / 40 = 0.0003125 m = 0.3...)
5. ______________________________  (hint: For comparison, whole-pixel matching (dd = 0.5 px) gives 3.125 mm....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do we match patches of random dots rather than single pixels, and what goes wrong on a blank patch?

Answer: ______________________________________________


**B. Numerical.** At Z = 1.2 m with f = 1000 px and B = 0.04 m, what depth error comes from a disparity error of 0.1 px?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the sub-pixel bias graph, at which fractional shifts is the error zero, and why is it largest in between?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose a baseline so that the depth error at 0.5 m is at most 0.2 mm when sub-pixel matching gives dd = 0.05 px. What changes if matching is only good to 0.1 px?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
