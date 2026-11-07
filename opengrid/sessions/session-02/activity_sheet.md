# Activity sheet: opengrid, Session 2: AC power, power factor and why we use high voltage

Name: ____________________   Date: ____________

**Objectives**

- Define real, reactive and apparent power and draw the power triangle.
- Compute the current a load draws at a given power factor.
- Size a capacitor bank (kvar and microfarad) to correct the power factor.
- Show that ten times the transmission voltage gives one hundredth of the line loss.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 100 kW single-phase load on 400 V has pf 0.70. Find its current, the capacitor needed to reach pf 0.95, the capacitance at 50 Hz, and the new current.

1. ______________________________  (hint: Current before: I = 100000 / (400 * 0.70) = 357.1 A....)
2. ______________________________  (hint: tan(phi1) = tan(acos 0.70) = 1.0202 and tan(phi2) = tan(acos 0.95) = 0...)
3. ______________________________  (hint: Qc = 100 kW * (1.0202 - 0.3287) = 69.15 kvar....)
4. ______________________________  (hint: C = 69150 / (2 pi * 50 * 400^2) = 0.001376 F = 1376 microfarad....)
5. ______________________________  (hint: Apparent power after: S = 100 / 0.95 = 105.3 kVA, so I = 105260 / 400 ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a low power factor waste capacity even though the reactive power does no useful work, and how does a capacitor help?

Answer: ______________________________________________


**B. Numerical.** A 30 kW single-phase load on 230 V has pf 0.8. Find its current, its reactive power, and the current if the pf were corrected to 1.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the current-against-pf graph (100 kW, 400 V), what are the currents at pf 1 and pf 0.5, and what does that tell you?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a 50 kW load has pf 0.75 and must reach 0.95 at 400 V, 50 Hz. Find the exact capacitor size and capacitance. A supplier only stocks a 30 kvar bank: what pf does it give? Discuss the trade-offs.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
