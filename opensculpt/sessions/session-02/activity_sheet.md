# Activity sheet: opensculpt, Session 2: CAD operations on distance functions: a parametric mug

Name: ____________________   Date: ____________

**Objectives**

- Build intersection, subtraction, offset, shell and smooth union from signed distances.
- Use the smooth minimum and verify that it equals min when the shapes are far apart.
- Build a parametric mug cross-section and count its area on a grid.
- Solve a design problem: choose the radius for 300 mL from the volume of revolution.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Find the outer radius of a mug of height 9 cm and wall 0.5 cm that holds exactly 300 mL, and the volume of material in the body.

1. ______________________________  (hint: Capacity = pi (R - t)^2 (H - t), with H - t = 9 - 0.5 = 8.5 cm....)
2. ______________________________  (hint: (R - t)^2 = 300 / (pi * 8.5) = 11.23, so R - t = 3.352 cm....)
3. ______________________________  (hint: R = 0.5 + 3.352 = 3.852 cm....)
4. ______________________________  (hint: Material = pi R^2 H - 300 = pi * 3.852^2 * 9 - 300 = 419.5 - 300 = 119...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the smooth union add material only near the place where the two shapes come close, and not everywhere?

Answer: ______________________________________________


**B. Numerical.** Find the outer radius for a mug of height 10 cm and wall 0.4 cm that holds 300 mL.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the smooth-min graph with blend radius k = 2 cm, how far below min(a, b) is the blended value at a = b?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for H = 9 cm and 300 mL, compare walls of 0.4 cm and 0.8 cm. Give the radius and the volume of material for each, and say which you would choose for a mug that is dropped often, and why.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
