# Activity sheet: openmapproject, Session 3: Measuring distortion with the Jacobian

Name: ____________________   Date: ____________

**Objectives**

- Compute the Jacobian of a map projection by finite differences.
- Read scale factors, area scale and angle error from the singular values of the Jacobian.
- Validate the numerical result against formulas and against the area of the sphere, 4 pi R^2.
- Compare the shortest route with the straight line on Mercator, and explain why Mercator fails at the poles.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Find the scale factors, area scale and angle error of the Lambert cylindrical equal-area projection at 60 degrees north, by hand and by the finite-difference Jacobian. Then compare the great circle and the Mercator straight line from London (51.5 N, 0.1 W) to New York (40.7 N, 74.0 W).

1. ______________________________  (hint: Lambert cylindrical: x = lambda, y = sin phi. So x_lambda = 1, x_phi =...)
2. ______________________________  (hint: J = [[1 / cos 60, 0], [0, cos 60]] = [[2, 0], [0, 0.5]]. The singular ...)
3. ______________________________  (hint: Area scale = 2 x 0.5 = 1 (equal-area), and omega = 2 arcsin(1.5 / 2.5)...)
4. ______________________________  (hint: The finite-difference Jacobian in Python gives s1 = 2.000, s2 = 0.500,...)
5. ______________________________  (hint: Routes (R = 6371 km): great circle 5573 km; the straight line on a Mer...)

Final answer: ____________________

## Questions
**A. Conceptual.** A map has an angle error of omega = 0 at every point. What does this say about its Tissot ellipses, and does it say that areas are right?

Answer: ______________________________________________


**B. Numerical.** For the equirectangular map at 60 degrees north, compute the Jacobian by hand, the area scale and the angle error omega.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the area graph, which projections lie on the line 1 and which do not? What is the reading of the Mercator curve at 80 degrees, and what happens at 90 degrees?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for a country in lat 8 to 37, lon 68 to 97, you need an equal-area map (area spread at most 1.05). Then, separately, you need a map for navigation (angle error at most 1 degree). Which projection do you choose in each case and what do you give up?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
