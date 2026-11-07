# Activity sheet: openemwave, Session 2: The numbers: Coulomb, superposition and the wave equation

Name: ____________________   Date: ____________

**Objectives**

- Compute the field of a point charge from Coulomb's law and add fields by superposition.
- Compute the field of a dipole on a grid and compare it with the far-field formula.
- Use y = A sin(k x - w t), find k, w and the speed w / k, and compute the wavelength of a wifi signal.
- Design the length of a half-wave dipole antenna from a frequency, and explain polarisation.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 2.4 GHz wifi wave: find lambda, k, w and check that w / k = c. Then find the half-wave antenna length. Finally compute the field of a 1 nC charge at 0.5 m.

1. ______________________________  (hint: lambda = c / f = 2.998e8 / 2.4e9 = 0.1249 m = 12.5 cm....)
2. ______________________________  (hint: k = 2 pi / lambda = 6.283 / 0.1249 = 50.3 rad/m....)
3. ______________________________  (hint: w = 2 pi f = 6.283 x 2.4e9 = 1.508e10 rad/s....)
4. ______________________________  (hint: Check: w / k = 1.508e10 / 50.3 = 3.00e8 m/s, which is c....)
5. ______________________________  (hint: Half-wave antenna: L = lambda / 2 = 0.0625 m = 6.2 cm....)
6. ______________________________  (hint: Coulomb: E = K q / r^2 = 8.99e9 x 1e-9 / 0.5^2 = 8.99 / 0.25 = 35.96 V...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the field of a dipole fall off as 1/r^3 while the field of a single charge falls off as 1/r^2? What would happen if the two charges had the same sign?

Answer: ______________________________________________


**B. Numerical.** A 2 nC charge. Find the field 0.3 m away. Then find the field if the distance is doubled, and sanity-check the ratio.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the log-log graph of dipole field against distance, the curves for the exact dipole and for 2 K q d / r^3 touch at large r but separate at small r. Where do they separate and why? Which line is steeper, the dipole or the single charge?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose the length of a half-wave dipole for an FM station at 100 MHz. A rod can be bought only in whole centimetres and your radio case is 1.2 m long. What length do you choose, and what trade-off does a shorter rod cause?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
