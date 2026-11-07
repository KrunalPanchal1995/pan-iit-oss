# Activity sheet: openairfoil, Session 3: A panel method for lift, and an estimate of drag

Name: ____________________   Date: ____________

**Objectives**

- Build a source-and-vortex (Hess-Smith) panel method and solve it as a linear system.
- Validate it: the exact flow past a circle, lift from pressure against lift from circulation, panel convergence.
- Compare the panel CL with thin-airfoil theory and explain the effect of thickness.
- Add a skin-friction drag estimate and choose a wing section for a small aircraft.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Solve NACA 0012 at 5 degrees with 160 panels. Compare CL with thin-airfoil theory and with its thickness-corrected value 2 pi (1 + 0.77 t/c) alpha. Then estimate the drag for a 1.5 m chord at 50 m/s and the section L/D.

1. ______________________________  (hint: Build the outline (80 points per side, cosine spacing) and solve the 161 x ...)
2. ______________________________  (hint: Panel results: CL from pressure = 0.6025, from circulation = 0.6052 (they a...)
3. ______________________________  (hint: Thin-airfoil theory: 2 pi x 5 x pi / 180 = 0.548. Thickness-corrected: 0.54...)
4. ______________________________  (hint: Re = 50 x 1.5 / 1.5e-5 = 5 x 10^6. Re^0.2 = 21.87, so Cf = 0.074 / 21.87 = ...)
5. ______________________________  (hint: Form factor = 1 + 0.24 + 60 x 0.12^4 = 1.252; cd = 2 x 0.00338 x 1.252 = 0....)
6. ______________________________  (hint: Section L/D = 0.6025 / 0.00848 = 71.)

Final answer: ____________________

## Questions
**A. Conceptual.** The panel method gives almost zero drag on the airfoil. Is the code wrong? Where does the real drag come from?

Answer: ______________________________________________


**B. Numerical.** A model aircraft wing has a chord of 1.2 m and flies at 30 m/s. Find Re, Cf and the drag estimate cd for a 15 percent thick section.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the pressure figure for NACA 2412 at 4 degrees, where is the lowest pressure, what is its Cp, and which surface contributes most of the lift?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the 1000 kg aircraft needs CL = 0.40 at 50 m/s (chord 1.5 m), a section at least 12 percent thick for the spar, and an angle of 0 to 3 degrees. Compare NACA 2408, 2412, 2415, 4412 and 0012 and choose one. What does the choice trade off?

Answer: ______________________________________________


## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
