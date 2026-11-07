# Activity sheet: openfoundation, Session 2: From soil strength to footing size

Name: ____________________   Date: ____________

**Objectives**

- Size a square footing for a column load including the footing's own weight.
- Use Terzaghi's equation to get the ultimate bearing capacity of a strip footing on clay and divide by a factor of safety.
- Apply the middle-third rule to an off-centre load and compute the edge pressures.
- Solve a design problem and say how eccentricity changes the footing size.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Design a square footing for a 600 kN column on soil with allowable pressure 150 kPa, thickness 0.6 m, built in 0.05 m steps. Then find the allowable pressure of a strip footing on clay with c = 50 kPa and FS = 3, and the edge pressures of a 2 m wide strip carrying 300 kN/m with e = 0.2 m.

1. ______________________________  (hint: Footing weight per m2 = 24 * 0.6 = 14.4 kPa. The column may use 150 - ...)
2. ______________________________  (hint: B = sqrt(600 / 135.6) = 2.104 m, rounded up to 2.15 m. Check: q = 600 ...)
3. ______________________________  (hint: Terzaghi, phi = 0: q_ult = 5.7 * 50 = 285 kPa. With FS = 3, q_allow = ...)
4. ______________________________  (hint: Eccentric strip: mean pressure = 300 / 2 = 150 kPa; 6 e / B = 6 * 0.2 ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why must the eccentricity stay within the middle third (e at most B / 6) for a footing on soil? What happens if it does not?

Answer: ______________________________________________


**B. Numerical.** A strip footing carries 200 kN/m on clay with c = 50 kPa. Using phi = 0, a factor of safety of 3 and ignoring the footing weight, what width is needed? Give the width you would build in 0.05 m steps.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the required-width graph, what happens to the footing side for a 600 kN column when the allowable pressure falls from 150 kPa to 75 kPa? Compute it.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the 600 kN column in the worked example also carries a moment that makes the load act 0.2 m off-centre in a square footing (t = 0.6 m, 150 kPa allowable including the footing weight). Find the smallest side in 0.05 m steps with e at most B / 6 and a peak pressure no greater than 150 kPa. How much more plan area does the eccentricity cost?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
