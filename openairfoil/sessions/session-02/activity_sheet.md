# Activity sheet: openairfoil, Session 2: Airfoil shape, thin-airfoil theory and the drag polar

Name: ____________________   Date: ____________

**Objectives**

- Build the outline of any NACA 4-digit airfoil from its camber line and thickness.
- Use thin-airfoil theory, CL = 2 pi (alpha - alpha_L0), and explain why camber shifts the lift line.
- Write the drag polar CD = CD0 + CL^2 / (pi e AR) and explain induced drag.
- Find the best lift-to-drag ratio and the angle a wing needs for a given CL.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For NACA 2412 find m, p and t, the zero-lift angle, CL at 4 degrees and the angle needed for CL = 0.40 (thin-airfoil theory). The aircraft has AR = 8, e = 0.8 and CD0 = 0.025: find k, CD and L/D at CL = 0.40, and the best L/D.

1. ______________________________  (hint: NACA 2412: m = 0.02, p = 0.4, t = 0.12.)
2. ______________________________  (hint: The integral of the camber slope (computed in `alpha_zero_lift`) gives alph...)
3. ______________________________  (hint: CL(4 degrees) = 2 pi x (4 + 2.077) x pi / 180 = 6.283 x 0.10606 = 0.666.)
4. ______________________________  (hint: Angle for CL 0.40: 0.40 / (2 pi) = 0.0637 rad = 3.65 degrees above alpha_L0...)
5. ______________________________  (hint: k = 1 / (pi x 0.8 x 8) = 1 / 20.11 = 0.04974. CD = 0.025 + 0.04974 x 0.16 =...)
6. ______________________________  (hint: Best: CL* = sqrt(0.025 / 0.04974) = 0.709, (L/D)max = 1 / (2 sqrt(0.025 x 0...)

Final answer: ____________________

## Questions
**A. Conceptual.** Two airfoils have the same thickness but one is symmetric and one is cambered. According to thin-airfoil theory, how do their lift lines differ, and which one needs the smaller angle to give CL = 0.40?

Answer: ______________________________________________


**B. Numerical.** NACA 4412 has twice the camber of NACA 2412. Find its zero-lift angle and its CL at 2 degrees from thin-airfoil theory. Show the working.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the L/D figure, how do the best L/D and the CL where it occurs change when the aspect ratio rises from 6 to 12? Explain the shape of each curve.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with CD0 = 0.025 and e = 0.8, what aspect ratio gives a best L/D of at least 15? For a 16 m2 wing, what span is that? Name two reasons not to choose a much larger AR.

Answer: ______________________________________________


## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
