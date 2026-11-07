# Activity sheet: openbeam, Session 2: Stiffness and strength: second moment of area, deflection and stress

Name: ____________________   Date: ____________

**Objectives**

- Compute the second moment of area I for a rectangle and an I-section, and say why depth matters most.
- Compute the deflection of a point-loaded beam and compare it with a limit such as L/360.
- Compute the bending stress sigma = M y / I and compare it with an allowable stress.
- Solve a design problem: the lightest rectangle that passes both the deflection and the stress test.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A timber beam (E = 10 GPa) spans L = 4 m with a 10 kN load at mid-span. The section is 100 mm wide and 200 mm deep. Find I, the maximum deflection, the maximum stress, and compare with L/360 and 12 MPa.

1. ______________________________  (hint: I = b h^3 / 12 = 0.100 x 0.200^3 / 12 = 6.667 x 10^-5 m^4 (66.67 x 10^...)
2. ______________________________  (hint: Deflection = P L^3 / (48 E I) = 10 000 x 64 / (48 x 10 x 10^9 x 6.667 ...)
3. ______________________________  (hint: Limit L/360 = 4 / 360 = 11.1 mm. The beam sags too much....)
4. ______________________________  (hint: M max = P L / 4 = 10 x 4 / 4 = 10 kN m. Stress = M (h/2) / I = 10 000 ...)
5. ______________________________  (hint: Fix by depth: deflection scales as 1/h^3, so we need h >= 200 x (20 / ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does increasing a beam's depth often improve bending stiffness more effectively than adding the same amount of material near the neutral axis?

Answer: ______________________________________________


**B. Numerical.** A timber beam 50 mm wide and 150 mm deep, E = 12 GPa, spans 3 m with a 5 kN load at mid-span. Find the maximum deflection and stress, with units, and compare with L/360 and 12 MPa.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the demand graph (demand divided by limit against depth) the blue curve crosses 1 at about 243 mm and the green curve at about 224 mm. Which limit governs and what does it mean for the designer?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with E = 10 GPa, L = 4 m and the 10 kN centre load, compare two ways of reaching the required stiffness: keep the width at 100 mm and increase the depth, or keep the depth at 200 mm and increase the width. Which uses less material, and by how much?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
