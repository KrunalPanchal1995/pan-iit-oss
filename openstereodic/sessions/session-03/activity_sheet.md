# Activity sheet: openstereodic, Session 3: Digital image correlation on speckle images, validated

Name: ____________________   Date: ____________

**Objectives**

- Generate a speckle image of a known deformation and match subsets to sub-pixel accuracy with an affine shape function.
- Turn a displacement field into strain with a least-squares plane fit.
- Validate displacement and strain against the exact values of the synthetic field.
- Predict and measure the effect of image noise and subset size, including a bias-versus-noise trade-off.
- Use the same tools on a stereo pair of a stretched strip (mini-project).

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For u = 0.02 (x - 80) + 1e-4 (x - 80)^2 find u at x = 56 and x = 104, the strain at x = 80 from these two points, and the random displacement error for noise 4 grey levels, h = 10 and G2 = 471.

1. ______________________________  (hint: u(56) = 0.02 * (-24) + 1e-4 * 576 = -0.48 + 0.0576 = -0.4224 px....)
2. ______________________________  (hint: u(104) = 0.02 * 24 + 1e-4 * 576 = 0.48 + 0.0576 = 0.5376 px....)
3. ______________________________  (hint: Strain = (0.5376 - (-0.4224)) / (104 - 56) = 0.96 / 48 = 0.0200. The c...)
4. ______________________________  (hint: Subset size N = (2 * 10 + 1)^2 = 441 pixels, so sigma_u = sqrt(2) * 4 ...)
5. ______________________________  (hint: Measured noise-only error in the code: 0.0118 px, within 5 percent of ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is the speckle pattern random and high-contrast, and why can the image change brightness without hurting the match?

Answer: ______________________________________________


**B. Numerical.** For noise 6 grey levels, subset half-size h = 14 and G2 = 471, find the random displacement error, and the strain error from noise for a window half-size w = 2 with grid spacing 8 px.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the plot of displacement error against subset size, why does each curve have a minimum, and what moves it?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with noise 6 grey levels and G2 = 471, choose the smallest strain window (w = 1, 2 or 3, grid spacing 8 px, h = 14) so the strain error from noise stays below 0.001. What do you lose with a larger window?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
