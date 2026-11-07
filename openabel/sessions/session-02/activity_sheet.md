# Activity sheet: openabel, Session 2: From a radial recipe to a photo: the forward Abel transform

Name: ____________________   Date: ____________

**Objectives**

- Write the forward Abel transform of a radial emission profile as an integral along a line of sight.
- Compute it by numerical integration and check it against the exact pair Gaussian to Gaussian.
- Build the ring (matrix) version of the transform and explain why the matrix has zeros below the diagonal.
- Estimate how many pixels across a flame are needed for a given accuracy.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For a Gaussian flame with a = 1 mm, what brightness does the camera record at y = 1 mm? Check it with numerical integration.

1. ______________________________  (hint: Use I(y) = sqrt(pi) a exp(-y^2 / a^2) with a = 1 and y = 1....)
2. ______________________________  (hint: The exponent is -1^2 / 1^2 = -1, and exp(-1) = 0.3679....)
3. ______________________________  (hint: sqrt(pi) = 1.7725, so I = 1.7725 * 0.3679 = 0.652 a.u....)
4. ______________________________  (hint: Numerical check: integrate 2 exp(-(1 + u^2)) over u from 0 to 3 with t...)
5. ______________________________  (hint: Sanity check: the peak (y = 0) is sqrt(pi) = 1.77 a.u., so 0.652 is sm...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why must the ring matrix W be zero below its diagonal? What does that mean for solving the inverse problem?

Answer: ______________________________________________


**B. Numerical.** A Gaussian flame has width a = 0.5 mm. What is the brightness at y = 0 and at y = 0.5 mm? Give the units and a sanity check.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the plot of ring-model error against N, how does the error change from N = 10 to N = 40 for a = 1 mm? Read the numbers and say what happens when the flame is narrower.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a camera images a region 8 mm wide in total (R = 4 mm on each side of the axis). The flame is a Gaussian with a = 0.7 mm and you want the ring model accurate to 1 percent of the peak. How many pixels across the whole image (both sides) and what pixel size do you need? What happens if the flame is half as wide?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
