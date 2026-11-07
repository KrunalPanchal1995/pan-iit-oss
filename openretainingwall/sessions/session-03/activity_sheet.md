# Activity sheet: openretainingwall, Session 3: Sliding, overturning, the middle third and water

Name: ____________________   Date: ____________

**Objectives**

- Compute the factor of safety against sliding and against overturning for a gravity wall, with its stated assumptions.
- Find the position of the resultant on the base, the eccentricity and the base pressure, and apply the middle-third rule.
- Validate the model against closed forms, numerical integration and moment equilibrium.
- Sweep width, friction, friction angle and backfill slope, and explain how water in the backfill makes the factors of safety fall below 1.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A wall 4 m high and 2 m wide (concrete 24 kN/m^3) holds dry soil (gamma = 18 kN/m^3, phi = 30 degrees), with base friction 0.5. Find both factors of safety, the eccentricity and the base pressures. Then fill the backfill with water to the top.

1. ______________________________  (hint: Pa = 0.5 x (1/3) x 18 x 16 = 48 kN/m at 1.33 m, so M_ot = 48 x 1.333 =...)
2. ______________________________  (hint: FS_slide = 0.5 x 192 / 48 = 2.00. FS_ot = 192 / 64 = 3.00. Both are ab...)
3. ______________________________  (hint: x = (192 - 64) / 192 = 0.667 m from the toe, so e = 1.0 - 0.667 = 0.33...)
4. ______________________________  (hint: q_toe = (192 / 2) x (1 + 6 x 0.333 / 2) = 96 x 2 = 192 kPa and q_heel ...)
5. ______________________________  (hint: Saturated to the top: soil 27.17 kN/m plus water 78.48 kN/m give Ph = ...)
6. ______________________________  (hint: M_ot = 105.65 x 1.333 + 39.24 x 1.333 = 193.19 kN m/m, so FS_ot = 192 ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does water in the backfill reduce both the sliding and the overturning factors, and why is drainage behind a wall so important?

Answer: ______________________________________________


**B. Numerical.** A wall 3 m high and 1.6 m wide (concrete 24 kN/m^3) holds dry soil (gamma = 18, phi = 30 degrees), base friction 0.5. Find FS_slide, FS_ot, the eccentricity and whether the resultant is in the middle third.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the right panel of the first figure (a 2 m wide wall), at what water levels does the sliding factor fall below 1.5 and 1? At what level does the overturning factor fall below 2 and 1? Which factor fails first?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for a 4 m wall with base friction 0.5 (phi = 30 degrees), find the smallest width in steps of 0.05 m that passes all three checks (FS_slide >= 1.5, FS_ot >= 2.0, e <= B/6) for a dry backfill, and with water 2 m deep. Discuss the cost of poor drainage.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
