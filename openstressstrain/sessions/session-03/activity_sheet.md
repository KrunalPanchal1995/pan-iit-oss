# Activity sheet: openstressstrain, Session 3: Elastic-plastic simulation, offset yield and uncertainty

Name: ____________________   Date: ____________

**Objectives**

- Simulate loading and unloading of an elastic-plastic metal with strain hardening, and explain permanent set.
- Validate a numerical curve against the analytic elastic slope, the hand-calculated permanent set and the 0.2 percent offset yield.
- Show how uncertainty in E and in yield strength changes stretch and factor of safety.
- Estimate E and yield from noisy (synthetic) tensile test data and state the error.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A bilinear metal has E = 70 000 MPa, yield 200 MPa and slope H = 7 000 MPa after yield. It is pulled to 2 percent strain and then unloaded. Find the peak stress and the permanent set, and compare with the solver.

1. ______________________________  (hint: Yield strain = 200 / 70 000 = 0.002857....)
2. ______________________________  (hint: Peak stress = 200 + 7000 * (0.02 - 0.002857) = 200 + 120 = 320 MPa....)
3. ______________________________  (hint: Unloading is elastic, so the elastic strain recovered is 320 / 70 000 ...)
4. ______________________________  (hint: Permanent set = 0.02 - 0.004571 = 0.015429 (1.54 percent)....)
5. ______________________________  (hint: The return-mapping solver gives 320.00 MPa at the top and zero stress ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do engineers use the 0.2 percent offset yield instead of the point where the curve first leaves the straight line?

Answer: ______________________________________________


**B. Numerical.** A bilinear metal with E = 70 000 MPa, yield 200 MPa and H = 7 000 MPa is pulled to 1 percent strain and unloaded. Find the peak stress and the permanent set.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** Read the sensitivity table for the steel bar (20 kN, 2 m, d = 16 mm). Which input matters for the stretch and which for the safety factor, and by how much for a 10 percent change?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the steel bar must still stretch no more than 1 mm if the real E is 10 percent below the table (180 GPa) and must keep FoS >= 2 if the real yield is 10 percent low (225 MPa). Choose the smallest whole-millimetre diameter and compare its mass with the 16 mm bar.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
