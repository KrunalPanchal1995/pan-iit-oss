# Activity sheet: openfractal, Session 1: Complex numbers are points that move, and some escape

Name: ____________________   Date: ____________

**Objectives**

- Plot a complex number a + b i as a point (a, b) on a plane.
- Explain addition as a slide and multiplication by i as a quarter turn.
- Iterate z -> z^2 + c by hand and in Python and list the orbit.
- Decide whether an orbit escapes (distance from 0 above 2) or stays.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For c = 0.5 + 0.5i, find z1 to z5 and the step at which the orbit escapes.

1. ______________________________  (hint: z1 = 0*0 + c = 0.5 + 0.5i....)
2. ______________________________  (hint: z2 = z1^2 + c. Now (0.5 + 0.5i)^2 = 0.25 + 0.5i + 0.25 i^2 = 0.5i, so ...)
3. ______________________________  (hint: z3 = (0.5 + 1.0i)^2 + c = (0.25 - 1 + 1.0i) + c = -0.75 + 1.0i + 0.5 +...)
4. ______________________________  (hint: z4 = (-0.25 + 1.5i)^2 + c = (0.0625 - 2.25 - 0.75i) + c = -2.1875 - 0....)
5. ______________________________  (hint: z5 = (-1.6875 - 0.25i)^2 + c = (2.8477 - 0.0625 + 0.84375i) + c = 3.28...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does multiplying by i turn a point by a quarter turn and never change its distance from 0?

Answer: ______________________________________________


**B. Numerical.** For c = 1 compute z1, z2, z3 and z4 by hand. At which step does the orbit first have distance above 2? Give the distances.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the distance graph for c = -1, what pattern do you see, and why does the orbit never escape?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: on the real axis (c with zero imaginary part), find by experiment the largest c for which the orbit still stays within 2 for 50 steps, to two decimal places, and the smallest negative c that does. What do you notice about the stay set?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
