# Activity sheet: openepidemic, Session 2: The SIR equations, R0 and herd immunity

Name: ____________________   Date: ____________

**Objectives**

- Write the SIR equations and explain each term and unit.
- Show that the epidemic grows exactly when R0 * S / N is above 1.
- Compute the herd immunity threshold 1 - 1/R0 and the final size from z = 1 - exp(-R0 z).
- Solve a design problem: what vaccination coverage brings the effective reproduction number below 1, and why imperfect protection needs more.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
(a) For R0 = 3 find the herd immunity threshold. (b) For R0 = 2 check that z = 0.797 is the final size. (c) Find the coverage needed for R0 = 3 when the vaccine efficacy is 0.9.

1. ______________________________  (hint: (a) p_c = 1 - 1/3 = 0.667, that is 66.7 percent of the town....)
2. ______________________________  (hint: (b) Evaluate the right-hand side at z = 0.797: 1 - exp(-2 * 0.797) = 1...)
3. ______________________________  (hint: (c) v > 0.667 / 0.9 = 0.741, that is 74.1 percent....)
4. ______________________________  (hint: Check (c): protected share = 0.741 * 0.9 = 0.667; R_eff = 3 * (1 - 0.6...)

Final answer: ____________________

## Questions
**A. Conceptual.** Explain in words why the herd immunity threshold is 1 - 1/R0 and why a larger R0 needs a larger share protected.

Answer: ______________________________________________


**B. Numerical.** R0 = 4. Find the herd immunity threshold. With a vaccine of efficacy 0.8, what coverage is needed?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the vaccination figure, how do the peak height and peak day change as coverage goes from 0 to 30 to 50 percent? What does this tell you about R_eff?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for R0 = 3 the town can only buy a vaccine with efficacy 0.6. Is vaccination alone enough to stop the infection spreading? What combination of measures could work, and what assumption does your answer rely on?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
