# Activity sheet: openabel, Session 1: A photo adds up the light along every line of sight

Name: ____________________   Date: ____________

**Objectives**

- Explain why one camera pixel records a sum along a whole line of sight, not one point.
- Compute the chord length through a ball and the brightness profile of a uniformly glowing ball.
- Check a formula against a brute-force sum along a ray.
- Explain why a hollow glowing shell looks brightest near its edge.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A solid ball of radius R = 3 cm has emission eps0 = 2 a.u. per cm. What does the camera record on a line of sight at y = 1.8 cm?

1. ______________________________  (hint: Square the numbers: R^2 = 9 and y^2 = 3.24....)
2. ______________________________  (hint: R^2 - y^2 = 5.76 and its square root is 2.4 cm....)
3. ______________________________  (hint: The chord is 2 * 2.4 = 4.8 cm....)
4. ______________________________  (hint: Brightness = eps0 * chord = 2 a.u. per cm * 4.8 cm = 9.6 a.u....)
5. ______________________________  (hint: Sanity check: the centre line would give 2 * 3 * 2 = 12 a.u., larger t...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is the middle of a solid glowing ball the brightest pixel, and why can a hollow shell be brighter at its edge than in the middle?

Answer: ______________________________________________


**B. Numerical.** A solid ball has R = 2.5 cm and eps0 = 1.2 a.u. per cm. Find the chord and the brightness at y = 1.5 cm, and at y = 0. Check the units.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the profile of the hollow shell (R = 3 cm, r_in = 2 cm), where is the brightest point and what value does it have? Why is the centre only 2 a.u.?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a glowing shell has outer radius 3 cm. Choose the inner radius so that the centre brightness is at most half of the brightest brightness. Is a hole of radius 1 cm enough? Justify with a calculation.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
