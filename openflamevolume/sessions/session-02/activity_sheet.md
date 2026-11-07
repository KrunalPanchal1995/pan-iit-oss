# Activity sheet: openflamevolume, Session 2: Find the same spot in two photos

Name: ____________________   Date: ____________

**Objectives**

- Compute the zero-mean normalised cross-correlation (ZNCC) of two image windows and explain why it ignores brightness.
- Search along a row for the best whole-pixel match and refine it to a sub-pixel value with a parabola.
- Tell bias from spread and measure both with a Monte Carlo experiment on images with a known shift.
- Explain how window size and camera noise change the spread of the answer.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Compute the ZNCC of f = [2, 4, 6] and g = [11, 12, 13]. Then the scores at disparities 39, 40 and 41 px are 0.80, 0.95 and 0.90. Find the sub-pixel disparity and the depth (f = 800 px, B = 0.10 m), and compare with using d = 40 px.

1. ______________________________  (hint: Means: mean f = 4, mean g = 12, so f - mean f = [-2, 0, 2] a...)
2. ______________________________  (hint: Numerator = 2 + 0 + 2 = 4. Denominator = sqrt(8 x 2) = 4. ZN...)
3. ______________________________  (hint: delta = (0.80 - 0.90) / (2 (0.80 - 2 x 0.95 + 0.90)) = (-0.1...)
4. ______________________________  (hint: Sub-pixel disparity d = 40 + 0.25 = 40.25 px, so Z = 800 x 0...)
5. ______________________________  (hint: Using the whole-pixel d = 40 px would give 2.000 m: rounding...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does ZNCC subtract the window mean and divide by the spread, instead of simply summing the squared differences of the pixels?

Answer: ______________________________________________


**B. Numerical.** Scores at d = 51, 52 and 53 px are 0.70, 0.90 and 0.85. Find the sub-pixel disparity and the depth for f = 800 px and B = 0.10 m. Also find the ZNCC of [1, 3, 5] with [2, 6, 10].

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the right panel of Figure 2 (noise 0.06) the spread is 0.95 px for a 7 px window and 0.15 px for a 15 px window. By what factor does it fall? Why not simply use a 50 px window?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: at Z = 2 m with f = 800 px and B = 0.10 m the depth uncertainty must be at most 2 cm. What spread sigma_d is allowed? With a noise of 0.06, which of the window sizes 7, 11, 15 and 21 px in Figure 2 meet it, and which is the smallest?

Answer: ______________________________________________


## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
