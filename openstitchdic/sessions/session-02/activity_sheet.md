# Activity sheet: openstitchdic, Session 2: One pixel grid and one time base

Name: ____________________   Date: ____________

**Objectives**

- Solve a homography from four point pairs and apply it by inverse mapping with bilinear sampling.
- Compare letterbox, crop and stretch when fitting one aspect ratio into another, and compute the cost of each.
- Quantify how resampling blurs a speckle pattern.
- Derive and implement Makima interpolation and compare it with linear and cubic spline on smooth and step-like motion.
- Recover a known timing offset between two cameras by cross-correlation.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A homography has H = [[1, 0.2, 10], [0, 1, 5], [0.001, 0, 1]]. Where does the pixel (100, 50) go, and does the inverse bring it back?

1. ______________________________  (hint: Compute the denominator: w = 0.001 * 100 + 0 * 50 + 1 = 1.1....)
2. ______________________________  (hint: Numerator for x: 1 * 100 + 0.2 * 50 + 10 = 120, so x' = 120 / 1.1 = 10...)
3. ______________________________  (hint: Numerator for y: 0 * 100 + 1 * 50 + 5 = 55, so y' = 55 / 1.1 = 50.00....)
4. ______________________________  (hint: The inverse matrix applied to (109.09, 50.00) returns (100, 50) (the c...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do we build a warped picture by looking up, for each output pixel, where it came from, instead of moving each source pixel forward?

Answer: ______________________________________________


**B. Numerical.** Fit a 1280 x 720 camera picture into a 640 x 480 grid. How many rows of the grid stay empty with letterbox, and what fraction of the source is lost with crop?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the interpolation figure, which curve overshoots the step, by how much, and why does RMS error alone not show this?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: camera A is 4:3 and camera B is 16:9; the grid is 4:3 and you cannot afford to lose any of the sample's field of view, but the shape of speckle dots must stay round. Which fit do you choose? And which B frame rate (30 or 60) would you choose if you could?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
