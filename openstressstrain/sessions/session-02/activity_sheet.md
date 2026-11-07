# Activity sheet: openstressstrain, Session 2: Hooke's law, strength and a safe design

Name: ____________________   Date: ____________

**Objectives**

- Use Hooke's law sigma = E * eps and the extension formula dL = F L / (A E).
- Tell apart stiffness (E), yield strength and ultimate strength.
- Compute a factor of safety and use it to size a bar.
- Choose a material and diameter that meet both a strength limit and a stretch limit, and say which limit governs.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A steel bar (E = 200 000 MPa, yield 250 MPa, density 7850 kg/m^3) of length 2 m carries 20 kN. Find the smallest whole-millimetre diameter with FoS >= 2 and extension <= 1 mm, and check it.

1. ______________________________  (hint: Strength: A >= 20 000 * 2 / 250 = 160 mm^2, so d >= 14.27 mm....)
2. ______________________________  (hint: Stiffness: A >= 20 000 * 2000 / (200 000 * 1) = 200 mm^2, so d >= 15.9...)
3. ______________________________  (hint: The larger diameter governs (stiffness), so d = 16 mm (next whole mill...)
4. ______________________________  (hint: Check: stress = 20 000 / 201.06 = 99.5 MPa; FoS = 250 / 99.5 = 2.51; e...)
5. ______________________________  (hint: Mass = 7850 * 201.06e-6 * 2 = 3.16 kg....)

Final answer: ____________________

## Questions
**A. Conceptual.** Steel and the aluminium alloy in the table have almost the same yield strength, yet the aluminium bar must be much thicker to meet the 1 mm limit. Why?

Answer: ______________________________________________


**B. Numerical.** An aluminium bar (E = 70 000 MPa, yield 240 MPa) of diameter 27 mm and length 2 m carries 20 kN. Find the stress, the extension and the factor of safety.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the first figure (stress against strain lines), which material is stiffest and which stretches most at its own yield point? Give the strain values.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the allowed extension is relaxed from 1 mm to 2 mm for the same 20 kN, 2 m, FoS 2. Which of the four materials gives the lightest bar, with a whole-millimetre diameter, and what are its diameter and mass?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
