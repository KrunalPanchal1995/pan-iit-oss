# Activity sheet: openparametric, Session 1: From a requirement to a size: a rule and a standard size

Name: ____________________   Date: ____________

**Objectives**

- Write the stress rule for a round shaft in torsion and solve it for the smallest safe diameter.
- Round up to a standard R10 size and say why rounding to the nearest is not allowed.
- Check the result: the stress and the safety factor of the shaft that is really bought.
- Explain how one rule feeds the next, and how the whole chain responds when the requirement changes.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A shaft must carry 200 N m. The steel has a tensile yield strength of 350 MPa and the safety factor is 2.5. Find the smallest safe diameter, the standard size, and the stress and safety factor of that shaft.

1. ______________________________  (hint: Allowable shear stress: tau_allow = 0.577 x 350 / 2.5 = 80.8 MPa.)
2. ______________________________  (hint: Smallest diameter: d_min = (16 x 200 000 / (pi x 80.8))^(1/3) = 23....)
3. ______________________________  (hint: Standard size: the next R10 size not below 23.28 mm is 25 mm (the o...)
4. ______________________________  (hint: Check: tau = 16 x 200 000 / (pi x 25^3) = 65.2 MPa, which is below...)
5. ______________________________  (hint: Safety factor actually obtained: 0.577 x 350 / 65.2 = 3.10, a littl...)
6. ______________________________  (hint: Mass per metre of the shaft: 7850 x pi / 4 x 0.025^2 = 3.85 kg/m.)

Final answer: ____________________

## Questions
**A. Conceptual.** A shaft must carry 135 N m with the same steel and safety factor (yield 350 MPa, SF 2.5), so d_min = 20.4 mm. The nearest standard size is 20 mm. Why is 20 mm not acceptable? Show it with the safety factor.

Answer: ______________________________________________

**B. Numerical.** A 15 kW motor runs at 1450 rpm. Find the torque, the smallest safe shaft diameter (yield 350 MPa, SF 2.5) and the standard size.

Answer: ______________________________________________

**C. Graph and simulation interpretation.** If the torque is doubled, by what factor does d_min grow, and by what factor does the mass per metre of the minimum shaft grow? Check with the torques 200 and 400 N m.

Answer: ______________________________________________

**D. Design and optimisation challenge.** Design: a 22 kW motor at 960 rpm drives a machine that needs a safety factor of 3 (yield 350 MPa). Find the standard shaft, how much it is oversize, and the stress if we had wrongly rounded down to the size below.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
