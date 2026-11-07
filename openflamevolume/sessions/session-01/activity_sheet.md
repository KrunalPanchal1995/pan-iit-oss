# Activity sheet: openflamevolume, Session 1: Two eyes see depth

Name: ____________________   Date: ____________

**Objectives**

- Say where a 3D point lands in a photo (pinhole camera) and why one photo cannot tell its depth.
- Compute the disparity between two cameras and turn it into a depth in metres (triangulation).
- Explain why the depth error grows with the square of the distance and shrinks with a longer baseline.
- Check a first-order error formula against a Monte Carlo experiment.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A stereo pair has f = 800 px and B = 10 cm. A flame tip appears at x_L = 120 px, x_R = 80 px, row y = 60 px (all from the image centre). Find its 3D position and the depth uncertainty for sigma_d = 0.5 px. Then find the uncertainty at 4 m.

1. ______________________________  (hint: Disparity d = 120 - 80 = 40 px.)
2. ______________________________  (hint: Depth Z = f B / d = 800 x 0.10 / 40 = 2.00 m.)
3. ______________________________  (hint: X = x_L Z / f = 120 x 2.00 / 800 = 0.30 m and Y = y Z / f = ...)
4. ______________________________  (hint: Uncertainty sigma_Z = Z^2 sigma_d / (f B) = 2.00^2 x 0.5 / (...)
5. ______________________________  (hint: At Z = 4 m the same formula gives 16 x 0.5 / 80 = 0.10 m = 1...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can one photo not tell you how far away a flame point is, and why does a second camera fix this?

Answer: ______________________________________________


**B. Numerical.** f = 1000 px, B = 0.12 m, and a point has disparity d = 60 px and x_L = 90 px. Find Z and X, and the depth uncertainty for sigma_d = 0.3 px. Check units and that the answer is reasonable.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the disparity graph (f = 800 px, B = 0.10 m) the disparity is 80, 40 and 20 px at 1, 2 and 4 m. The same 0.5 px error is made at 2 m and at 4 m. Which depth error is larger and by what factor? Explain from the shape of the curve.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you must measure a flame at Z = 3 m with a depth uncertainty of at most 1 cm. The matching error is 0.5 px and f = 1000 px. What baseline do you need? What if you can double the focal length? Name one practical drawback of a wide baseline.

Answer: ______________________________________________


## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
