# Activity sheet: openphtitration, Session 3: Weak acids: buffers, the numerical curve and the noisy endpoint

Name: ____________________   Date: ____________

**Objectives**

- Use the acid dissociation constant Ka and the charge balance to compute a weak-acid titration curve.
- Write a bisection root finder and validate the curve against the strong-acid limit and the half-equivalence rule.
- Compare the Henderson-Hasselbalch relation with the exact solution and say where it fails.
- Find the equivalence point of a noisy curve from the maximum of the first derivative and find an unknown vinegar concentration.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
25 mL of 0.1 mol/L acetic acid (Ka = 1.8e-5) is titrated with 0.1 mol/L NaOH. Find the pH after 10 mL by Henderson-Hasselbalch, compare with the exact numerical value, and find the equivalence pH.

1. ______________________________  (hint: pKa = -log10(1.8e-5) = 4.745....)
2. ______________________________  (hint: Moles: acid 0.1 x 25 = 2.5 mmol; base 0.1 x 10 = 1.0 mmol. After react...)
3. ______________________________  (hint: Henderson-Hasselbalch: pH = 4.745 + log10(1.0/1.5) = 4.745 - 0.176 = 4...)
4. ______________________________  (hint: The bisection solver of the charge balance gives 4.569 as well (differ...)
5. ______________________________  (hint: Equivalence is at 25 mL: Ct = 2.5/50 = 0.05 mol/L of A-, Kb = 1e-14/1....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a weak acid titration have a flat region around pH = pKa, and why is the equivalence point above 7 although acid and base have cancelled exactly?

Answer: ______________________________________________


**B. Numerical.** For the 0.1 mol/L acetic acid titration above, find the pH after 20 mL of base with Henderson-Hasselbalch. Then state the pH at 12.5 mL without calculating.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the Henderson-Hasselbalch comparison table, where does the formula fail and why? Which direction does it err?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a student must locate the equivalence point of a vinegar titration with a volume reading noise of 0.03 mL and pH noise of 0.02. Compare a 1.0 mL step with a 0.2 mL step and recommend a plan. What does a 0.5 percent target on the concentration require?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
