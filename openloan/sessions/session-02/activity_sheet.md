# Activity sheet: openloan, Session 2: Compound growth and the EMI

Name: ____________________   Date: ____________

**Objectives**

- Use A = P (1 + r/n)^(n t) and see the continuous-compounding limit.
- Compute the EMI from the formula and verify it by simulating the balance month by month.
- Read an amortisation schedule: interest part falls, principal part rises.
- Compare loans by total cost, tenure and effective annual rate.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Borrow 100000 units at 12 percent a year for 24 months. Find the EMI, the interest and principal of month 1, and the total interest, then check the EMI by simulating the balance.

1. ______________________________  (hint: Monthly rate i = 12 / 12 percent = 0.01 and n = 24. (1.01)^24 = 1.2697...)
2. ______________________________  (hint: EMI = 100000 * 0.01 * 1.2697 / (1.2697 - 1) = 1269.7 / 0.2697 = 4707.3...)
3. ______________________________  (hint: Month 1: interest = 100000 * 0.01 = 1000.00; principal = 4707.35 - 100...)
4. ______________________________  (hint: Total interest = 24 * 4707.35 - 100000 = 12976.33 units....)
5. ______________________________  (hint: Check by simulation: start at 100000; each month multiply by 1.01 and ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is the interest part of the EMI large at the start and small at the end, although the EMI itself never changes?

Answer: ______________________________________________


**B. Numerical.** Find the EMI and the total interest for 100000 units at 12 percent a year over 12 months. State the units and do a sanity check.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the tenure graph for 100000 units at 12 percent, what happens to the EMI and to the total interest when the tenure grows from 12 to 60 months?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you can afford an EMI of at most 4000 on a 100000 loan at 12 percent and want the least total interest. Which tenure in the table (12, 24, 36, 48 or 60 months) do you pick? Separately, compare Offer A (9.0 percent a year with a 2 percent fee, 36 months) and Offer B (9.8 percent, no fee, 36 months) for 100000. Which is cheaper in total?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
