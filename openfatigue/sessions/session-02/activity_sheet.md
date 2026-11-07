# Activity sheet: openfatigue, Session 2: The S-N curve as an equation: mean stress and notches

Name: ____________________   Date: ____________

**Objectives**

- Build the Basquin line S_a = A N^b for any S_u and S_e and invert it for life and for stress.
- Apply the Goodman line S_a / S_e + S_m / S_u = 1 and the equivalent amplitude for a load with mean stress.
- Explain stress concentration and use K_t = 3 for a hole in a wide plate.
- Size a rotating shaft for 10^6 cycles and beyond with a safety margin, and say what changes with a shoulder (K_t = 2).

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A shaft carries a steady bending moment M = 200 N m. Choose its diameter for 10^6 cycles and beyond with a safety factor n = 2 on stress, for a plain shaft (K_t = 1) and for a shaft with a shoulder (K_t = 2). The part endurance limit is 210 MPa.

1. ______________________________  (hint: Require K_t S_a <= S_e,part / n = 210 / 2 = 105 MPa for K_t = 1....)
2. ______________________________  (hint: d = (32 M n K_t / (pi S_e,part))^(1/3) = (32 x 200 x 2 x 1 / (pi x 210...)
3. ______________________________  (hint: Check the 27 mm shaft: S_a = 32 x 200 / (pi x 0.027^3) = 103.5 MPa, so...)
4. ______________________________  (hint: With a shoulder, K_t = 2: d = 26.87 x 2^(1/3) = 33.86 mm. A sharper co...)
5. ______________________________  (hint: Sanity check: a thinner 20 mm shaft has S_a = 254.6 MPa (above 210), s...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a tensile mean stress shorten fatigue life, and why is the same load safe for steel but not necessarily for aluminium when it lies below the endurance limit?

Answer: ______________________________________________


**B. Numerical.** A load has S_a = 240 MPa and S_m = 250 MPa on the illustrative steel (S_u = 600, S_e = 300). Find the Goodman equivalent amplitude and the life. What would the life be with zero mean?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the Goodman diagram the point (S_m, S_a) = (300, 150) MPa is plotted. Where is it, and what does the Goodman sum say? What happens if the amplitude rises slightly?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a shaft carries M = 150 N m, has a shoulder fillet with K_t = 1.5, and must have a safety factor of 2 on stress for indefinite life (part endurance limit 210 MPa). Choose a diameter, compare 25 mm and 28 mm, and say what happens at 22 mm. State the trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
