# Activity sheet: openbuoyancy, Session 3: Does it stay upright? Metacentric height and the righting arm

Name: ____________________   Date: ____________

**Objectives**

- Locate the centre of buoyancy B, the centre of gravity G and the metacentre M of a floating box and compute GM = KB + BM - KG.
- Compute the righting arm GZ against heel angle from exact submerged-area geometry.
- Validate the numerical result against the small-angle limit GM sin(phi) and the wall-sided formula.
- Explain and show how loading height and a cargo shift change stability, and what a negative GM does.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The barge (20 x 6 x 2.5 m, empty 60 t with its centre of gravity 1.0 m above the keel) carries 120 t of cargo whose centre of gravity is 2.5 m above the keel, in fresh water. Find GM, and the righting arm at 10 degrees exactly and by the small-angle formula.

1. ______________________________  (hint: Total mass 180 000 kg, so draft d = 180 000 / (1000 * 20 * 6) = 1.500 ...)
2. ______________________________  (hint: KB = d / 2 = 0.750 m. BM = B^2 / (12 d) = 36 / 18 = 2.000 m. KM = 2.75...)
3. ______________________________  (hint: KG = (60 * 1.0 + 120 * 2.5) / 180 = 360 / 180 = 2.000 m....)
4. ______________________________  (hint: GM = 2.750 - 2.000 = 0.750 m, positive, so the barge rights itself....)
5. ______________________________  (hint: Small angle at 10 degrees: GM sin(10 deg) = 0.750 * 0.1736 = 0.1302 m....)
6. ______________________________  (hint: Wall-sided formula: sin(10 deg) (0.750 + 0.5 * 2.000 * tan^2(10 deg)) ...)

Final answer: ____________________

## Questions
**A. Conceptual.** A barge has 1.2 m of freeboard but capsizes when loaded with tall stacked cargo. Explain why freeboard does not guarantee stability, and what quantity does.

Answer: ______________________________________________


**B. Numerical.** The same barge carries 120 t with its centre of gravity at 3.0 m. Find KG and GM, and say whether it is stable.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the GZ figure, at 20 degrees the exact curve is above the small-angle line. Read approximately both values for the loaded barge, state which is larger and give a likely reason for the difference.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with 160 t of cargo (instead of 120 t), find the highest cargo centre of gravity, in steps of 0.1 m, that keeps GM at or above 0.15 m. Compare it with the 3.40 m for 120 t and explain.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
