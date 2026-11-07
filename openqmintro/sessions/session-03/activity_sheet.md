# Activity sheet: openqmintro, Session 3: Tunnelling: getting through a wall, validated by a transfer matrix

Name: ____________________   Date: ____________

**Objectives**

- Compute the exact transmission probability of a rectangular barrier, below, at and above its height.
- Explain why the probability falls exponentially with the width, and use the thick-barrier formula.
- Validate the formula against a transfer-matrix solution, and use the same method for a smooth barrier.
- Estimate how sensitive a scanning tunnelling microscope is to its tip height.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
An electron with E = 1 eV meets a barrier of height V0 = 2 eV and width a = 0.5 nm. Find kappa, the exact transmission, the thick-barrier estimate, and the factor by which an STM current changes when the tip is pulled back by 0.1 nm (work function 4.5 eV).

1. ______________________________  (hint: kappa = sqrt((2 - 1) / 0.0381) = 5.123 per nm, so kappa a = 2.562.)
2. ______________________________  (hint: sinh(2.562) = 6.440, so sinh^2 = 41.47.)
3. ______________________________  (hint: T = 1 / (1 + 4 x 41.47 / (4 x 1 x 1)) = 1 / (1 + 41.47) = 0.0235: a...)
4. ______________________________  (hint: Thick-barrier formula: 16 x 1 x 1 / 4 x exp(-2 x 2.562) = 4 x 0.005...)
5. ______________________________  (hint: Check with the transfer matrix of one flat slice: it gives the same...)
6. ______________________________  (hint: STM: kappa = sqrt(4.5 / 0.0381) = 10.87 per nm, so pulling the tip...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the transmission probability fall exponentially with the width of the barrier, and why can an electron get through at all when its energy is below the barrier height?

Answer: ______________________________________________

**B. Numerical.** An electron with E = 0.5 eV meets a barrier of V0 = 1.5 eV and width 0.8 nm. Find kappa, the exact T and the thick-barrier T.

Answer: ______________________________________________

**C. Graph and simulation interpretation.** On the logarithmic graph of T against the width for E = 1 eV and V0 = 2 eV, by what factor does T fall for every extra 0.1 nm of width? Confirm with the formula.

Answer: ______________________________________________

**D. Design and optimisation challenge.** Design: an electron of energy E = 0.5 eV meets a thin insulating layer that acts as a rectangular barrier of height V0 = 3 eV. The transmission must be at most 1e-9. Find the least thickness, and say why a designer would not make the layer much thicker than needed.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
