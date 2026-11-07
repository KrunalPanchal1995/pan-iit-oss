# Activity sheet: openfatigue, Session 3: Variable loads, cracks and scatter: a life estimate

Name: ____________________   Date: ____________

**Objectives**

- Count the cycles in a messy load history with a rainflow counter and check it on a hand-traced sequence.
- Add up fatigue damage with Miner's rule and say where the rule is weak.
- Integrate Paris' law numerically for crack growth and validate it against the closed form.
- Show the scatter of fatigue life by seeded Monte Carlo and the sensitivity of life to stress, and use all of it for a bracket life and an inspection interval.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A part has seen 10,000 cycles at an amplitude of 400 MPa and 50,000 cycles at 350 MPa (fully reversed, S_u = 600 MPa, S_e = 300 MPa). By Miner's rule, how much of its life is used, and how many more cycles at 400 MPa can it take?

1. ______________________________  (hint: Lives from the S-N line: N(400) = 34,017 cycles and N(350) = 163,392 c...)
2. ______________________________  (hint: Damage at 400 MPa: 10,000 / 34,017 = 0.294. Damage at 350 MPa: 50,000 ...)
3. ______________________________  (hint: Total D = 0.294 + 0.306 = 0.600, so 60 percent of the life is used and...)
4. ______________________________  (hint: More cycles at 400 MPa: 0.400 x 34,017 = 13,607 cycles (about 13,600)....)
5. ______________________________  (hint: Sanity check: if the order were reversed the sum would be the same, wh...)

Final answer: ____________________

## Questions
**A. Conceptual.** Give two reasons why Miner's rule can be wrong, and say whether ignoring cycles below the endurance limit is safe when large overloads are also present.

Answer: ______________________________________________


**B. Numerical.** An edge crack (Y = 1.12) in a part sees a stress range of 80 MPa (zero to maximum). Using C = 6.9e-12, m = 3 and K_Ic = 50 MPa sqrt(m), find delta K for a0 = 2 mm, the critical length and the life in cycles.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the scatter histogram the 5th percentile life is 31,000 cycles and the 95th is 311,000 for a median of 100,000. What does the spread say about testing one part, and what ratio of 95th to 5th percentile do you read off?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the bracket's life is 4,998 shifts with 6 hard knocks per shift. A customer needs at least 4,000 shifts. How many knocks per shift may the machine produce at most? And the inspection method can find a crack of 1 mm instead of 0.5 mm: what happens to the interval, and what if it can only find 2 mm?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
