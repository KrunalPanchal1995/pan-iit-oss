# Activity sheet: openfractal, Session 2: Modulus, argument and the escape-time algorithm

Name: ____________________   Date: ____________

**Objectives**

- Compute the modulus and argument of a complex number and use them to multiply.
- Explain why an orbit beyond distance 2 can never return.
- Write the escape-time algorithm and use it to draw the Mandelbrot set and a Julia set.
- Choose the iteration limit for a given zoom with a measured error.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For z = 3 + 4i and w = 1 + i, find the modulus and argument of z, w and z*w, and check the multiplication rule.

1. ______________________________  (hint: |z| = sqrt(3^2 + 4^2) = 5 and arg z = atan2(4, 3) = 53.13 degrees....)
2. ______________________________  (hint: |w| = sqrt(2) = 1.414 and arg w = 45 degrees....)
3. ______________________________  (hint: z * w = (3 + 4i)(1 + i) = 3 + 3i + 4i + 4 i^2 = -1 + 7i....)
4. ______________________________  (hint: |z w| = sqrt(1 + 49) = sqrt(50) = 7.071, and |z| |w| = 5 * 1.414 = 7.0...)
5. ______________________________  (hint: arg(z w) = atan2(7, -1) = 98.13 degrees, and arg z + arg w = 53.13 + 4...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is it safe to stop iterating as soon as |z| > 2, but not safe to conclude 'stays' after any finite number of steps?

Answer: ______________________________________________


**B. Numerical.** Compute |z^2| and arg(z^2) for z = 3 + 4i, from the modulus and argument. Check by multiplying out.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the iteration-error graph, why does each curve fall, and why is the curve for width 0.005 above the curve for width 0.5 at max_iter = 100?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a zoom video moves from width 0.5 to width 0.005 at the seahorse valley. Choose max_iter for the first and last frame from the ladder 25, 50, 100, 200, 400, 800 with at most 1 percent wrong pixels, and say what you would do in between.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
