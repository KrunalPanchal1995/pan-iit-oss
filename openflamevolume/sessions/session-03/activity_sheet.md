# Activity sheet: openflamevolume, Session 3: From many photos to one 3D flame

Name: ____________________   Date: ____________

**Objectives**

- Build a multi-view reconstruction: render, match, triangulate and merge several stereo pairs into a 3D point cloud.
- Slice the cloud, find each slice's area with the shoelace formula and add the slices up to a volume.
- Validate against a flame whose shape and volume are known exactly (point residuals and volume error).
- Explain why too few views give a biased volume and what error remains however many views you use.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The test flame has A0 = 15 mm, B0 = 10 mm and H = 60 mm. Find its exact volume and the area of the slice at z = 2.5 mm, and show that 12 slices of 5 mm add up to the exact volume. Then compare the reconstruction from four pairs with it.

1. ______________________________  (hint: Exact volume V = pi A0 B0 H / 2 = pi x 15 x 10 x 60 / 2 = 14...)
2. ______________________________  (hint: Slice area at z = 2.5 mm: pi x 15 x 10 x (1 - 2.5 / 60) = 47...)
3. ______________________________  (hint: Midpoints of 12 slices: sum of (1 - (k + 0.5) / 12) over k =...)
4. ______________________________  (hint: Reconstruction from four pairs (1315 points): sliced volume ...)
5. ______________________________  (hint: The slicing alone, applied to perfect surface points, gives ...)

Final answer: ____________________

## Questions
**A. Conceptual.** A single stereo pair gives 243 points in this simulation, and still the volume is 92 percent too small. Why? What does a second and third pair fix?

Answer: ______________________________________________


**B. Numerical.** A flame with A0 = 12 mm, B0 = 8 mm and H = 50 mm has the same shape family. Find its exact volume and the exact slice area at z = 25 mm.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In Figure 3 the error is -92, -29, -7.0, -5.2 and -4.5 percent for 1, 2, 3, 4 and 6 pairs. Which steps are worth the cost? Why does the curve not reach the dashed line at -0.7 percent?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a lab can buy 4 cameras (2 pairs) or 6 cameras (3 pairs). The target is a volume within 10 percent. Which do you buy? Also find the depth uncertainty of one pair at D = 0.30 m, B = 0.03 m, f = 1000 px, sigma_d = 0.5 px.

Answer: ______________________________________________


## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
