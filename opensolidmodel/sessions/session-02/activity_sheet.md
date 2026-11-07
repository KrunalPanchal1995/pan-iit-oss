# Activity sheet: opensolidmodel, Session 2: From an outline to the properties of a solid: area, centroid and stiffness

Name: ____________________   Date: ____________

**Objectives**

- Compute the area, centroid and second moments of area of a polygon from its corner points.
- Combine several shapes, adding material and removing holes, with the parallel-axis rule.
- Explain why the second moment of area, and not the area alone, decides how stiff a section is in bending.
- Extrude a section to a solid and find its mass and the bending stress in it.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
An L-section has a horizontal leg b = 60 mm, a vertical leg h = 40 mm and a thickness t = 10 mm. Find the area, the centroid, Ixx and Iyy, and the mass of a 300 mm length of steel.

1. ______________________________  (hint: Split it into two rectangles: the horizontal leg 60 x 10 (area 600...)
2. ______________________________  (hint: Area: 600 + 300 = 900 mm2.)
3. ______________________________  (hint: Centroid: Cx = (600 x 30 + 300 x 5) / 900 = 21.67 mm and Cy = (600...)
4. ______________________________  (hint: Ixx: 60 x 10^3 / 12 + 600 x (11.67 - 5)^2 + 10 x 30^3 / 12 + 300 x...)
5. ______________________________  (hint: Iyy: 10 x 60^3 / 12 + 600 x (30 - 21.67)^2 + 30 x 10^3 / 12 + 300 x...)
6. ______________________________  (hint: Mass: 7850 x 900 x 300 x 1e-9 = 2.12 kg. The lesson code, which use...)

Final answer: ____________________

## Questions
**A. Conceptual.** Two sections have the same area. Why can one be much stiffer in bending than the other?

Answer: ______________________________________________

**B. Numerical.** A flat steel plate is 100 mm wide and 20 mm thick, with a 10 mm hole at its centre. Find its area and Ixx about the horizontal line through the centre.

Answer: ______________________________________________

**C. Graph and simulation interpretation.** On the graph of Ixx against the area, compare three L-sections with a 50 mm horizontal leg and vertical legs of 30, 50 and 80 mm, all with the area 475 mm2. Which is stiffest, and by how much?

Answer: ______________________________________________

**D. Design and optimisation challenge.** Design: a 50 x 50 mm L-section needs Ixx of at least 150 000 mm4. Find the smallest thickness, and say what the extra stiffness costs in material.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
