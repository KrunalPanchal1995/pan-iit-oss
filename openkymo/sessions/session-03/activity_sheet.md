# Activity sheet: openkymo, Session 3: Synthetic kymographs: measure, break and validate

Name: ____________________   Date: ____________

**Objectives**

- Generate synthetic kymographs (blobs, several stripes, a speckled belt) with a known speed.
- Measure speed with two estimators: gradients (LS and TLS) and a ridge tracker with a straight-line fit.
- Measure error and scatter against noise and against speed with a Monte Carlo experiment, and check the line-fit scatter against a formula.
- Predict and observe aliasing: a camera cannot tell a shift d from d minus a wavelength.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A cosine pattern of wavelength 8 px moves 5 px/frame to the right. What shift does the camera report, and what is the standard deviation of a slope fitted through 60 tracked points with scatter 0.26 px?

1. ______________________________  (hint: Apparent shift = 5 folded into -4 .. +4: 5 - 8 = -3 px/frame. The patt...)
2. ______________________________  (hint: Check by the program: the gradient estimator on this synthetic pattern...)
3. ______________________________  (hint: Slope scatter = 0.26 * sqrt(12 / (60 * (60^2 - 1))) = 0.26 * sqrt(12 /...)
4. ______________________________  (hint: Simulation with 2000 noisy fits gives 0.0019 as well....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does noise bias the least-squares speed towards zero, and why does the total least-squares (structure tensor) speed not suffer from this bias?

Answer: ______________________________________________


**B. Numerical.** A ridge tracker gives 40 centre points with scatter 0.3 px about the fitted line. What is the standard deviation of the fitted slope in px/frame, and how large is it relative to a true speed of 0.5 px/frame?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the right panel of the error figure, up to which shift per frame are both methods exact for this blob (width 1.5 px), what happens first, and which method fails first?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a belt moves at 0.8 m/s and each pixel covers 2 mm. From the conveyor experiment (worst error over 5 seeds: 18.5 percent at 100 fps, at most 0.2 percent from 200 fps up) choose a frame rate for production. Justify it and say what you give up.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
