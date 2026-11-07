# Activity sheet: opensculpt, Session 3: A 3D mug on a voxel grid: measure it and check it

Name: ____________________   Date: ____________

**Objectives**

- Sample a 3D signed distance function on a voxel grid and estimate volume by counting.
- Measure how the volume error falls as the grid is refined, and fit its rate.
- Extract a contour with marching squares and check its length converges to 2 pi r.
- Use the gradient for the surface normal, check the Eikonal property, and render a cut-away.
- Check d(volume)/d(thickness) against the surface area, and find two failure modes.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For the 300 mL mug (R = 3.852 cm, H = 9 cm, t = 0.5 cm), find the exact volume of the body and of the torus handle, and the mass of the whole mug in a ceramic of density 2.4 g/cm^3.

1. ______________________________  (hint: Body volume = pi R^2 H - pi (R - t)^2 (H - t) = 419.5 - 300.0 = 119.49...)
2. ______________________________  (hint: Torus volume = 2 pi^2 Rh r^2 = 2 pi^2 * 2.0 * 0.45^2 = 7.99 cm^3 (full...)
3. ______________________________  (hint: Body mass = 2.4 * 119.49 = 286.8 g....)
4. ______________________________  (hint: For the handle and its overlap we use the voxel volume of the whole mu...)
5. ______________________________  (hint: Check: the handle adds about 14 g, which is below the 7.99 cm^3 * 2.4 ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the volume error of a voxel count depend on the surface area, and why does it fall about like 1 / N?

Answer: ______________________________________________


**B. Numerical.** The cavity wall and floor have area 2 pi (R - t)(H - t) + pi (R - t)^2. Compute it for R = 3.852, t = 0.5, H = 9 cm and use it to estimate the change in body volume when the wall grows from 0.5 to 0.6 cm (R and H fixed).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the blend-radius results: the empty cavity is 300 mL with no blend, about 294 mL with k = 2 cm, about 166 mL with k = 8 cm and 0 with k = 16 cm. Explain what happens physically and what blend radius you would allow.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose the thickest wall in steps of 0.05 cm from 0.30 to 0.80 for a 300 mL mug of height 9 cm that must weigh less than 320 g (ceramic 2.4 g/cm^3, blend 0.5 cm). Justify with the numbers and state what the model leaves out.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
