# Activity sheet: opengears, Session 3: Search, losses, backlash and a planetary set

Name: ____________________   Date: ____________

**Objectives**

- Search every tooth combination with numpy for a target ratio, a tolerance and an in-line constraint.
- Model mesh losses and simulate a two-stage train with backlash, checked against momentum and energy balance.
- Verify the planetary (Willis) relation and the ratio 1 + Nr / Ns with code.
- Detect failing designs: non-integer teeth, undercut pinions, unequal centre distances, a box that is too small.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Search 17 to 90 teeth for an in-line two-stage 1:20 within 1 percent and take the design with the fewest teeth. Then, for input and load inertias J1 = 1e-4, middle shaft 2e-4 and load 0.05 kg m^2, find J_eff, the input speed after a 0.2 N m pulse of 0.05 s, and the output speed.

1. ______________________________  (hint: No exact in-line 1:20 exists in this range, but 19 designs lie within ...)
2. ______________________________  (hint: Both stages have N + N = 93, so the centre distances are equal and the...)
3. ______________________________  (hint: rho for the shafts: 1, 17 / 76 = 0.2237, and 0.2237^2 = 0.0500....)
4. ______________________________  (hint: J_eff = 1e-4 + 2e-4 * 0.0500 + 0.05 * 0.0500^2 = 1.0e-4 + 1.0e-5 + 1.2...)
5. ______________________________  (hint: Impulse = 0.2 * 0.05 = 0.01 N m s, so the input turns at 0.01 / 2.352e...)
6. ______________________________  (hint: Output speed = 42.5 * 0.0500 = 2.13 rad/s = 20.3 rpm. At 98 percent pe...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does backlash make the start-up impact harder, and why is the final speed hardly affected?

Answer: ______________________________________________


**B. Numerical.** A planetary set has Ns = 24 and Nr = 72. With the ring fixed and the sun at 900 rpm, find the planet teeth, the ratio and the carrier speed. Then a four-mesh spur train takes 500 W: how much power is lost at 98 percent per mesh?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the mesh-torque view, the peak mesh torque is 0.172 N m for no backlash and 0.447 N m for 0.02 rad. At 0.04 rad it is 0.588 N m. What is the trend and what does it mean for gear wear?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: find the in-line two-stage gearbox for 1:16 within 1 percent with 17 to 90 teeth and the fewest total teeth. Is the ratio exact? Check it with the checker at module 2 mm.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
