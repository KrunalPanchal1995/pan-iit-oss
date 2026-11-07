# Activity sheet: opengps, Session 3: Solve for position and clock together, and check the geometry

Name: ____________________   Date: ____________

**Objectives**

- Set up the pseudorange model with an unknown receiver clock bias and solve it by Gauss-Newton.
- Compute dilution of precision (DOP) from the geometry and use it to predict the position error.
- Validate the solver against a known true position with noise, and show that it matches sigma x PDOP.
- Compute the special and general relativity offsets of a satellite clock from their formulas, and explain why they matter.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Compute the relativity offsets of a GPS satellite clock at r = 26,560 km from the Earth's centre (ground at 6371 km), and the range error if left uncorrected for one day.

1. ______________________________  (hint: GM/c^2 = 3.986004e14 / 8.98755e16 = 4.4350e-3 m. 1/R_E = 1.5696e-7 per...)
2. ______________________________  (hint: Gravity: fractional rate = 4.4350e-3 x 1.1931e-7 = 5.2915e-10. Per day...)
3. ______________________________  (hint: Motion: v^2 = GM / r_s = 1.5008e7 m^2/s^2 (v = 3874 m/s). Fraction = v...)
4. ______________________________  (hint: Net = 45.7 - 7.2 = +38.5 microseconds per day (the clock runs fast)....)
5. ______________________________  (hint: Range: c x 38.5e-6 s = 11.5 km per day. After 10 days: 115 km....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a 3D GPS fix need four satellites even when the satellites are known exactly and the Earth's radius is known?

Answer: ______________________________________________


**B. Numerical.** Range noise has sigma = 3 m and the satellites give PDOP = 3.48. What rms 3D position error do you expect? And with PDOP = 1.89?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the DOP-validation figure the dots lie on the line sigma x PDOP. What does that say about the simulation and about DOP? What would it mean if the dots were far above the line?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a phone has eight toy satellites in view but can use only four. There are 70 choices. Which four would you use, and why? What does the worst four do?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
