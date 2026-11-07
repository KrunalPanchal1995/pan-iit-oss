# Activity sheet: openloan, Session 3: Simulating real loans: prepayment, rate changes and flat rates

Name: ____________________   Date: ____________

**Objectives**

- Build a month-by-month loan simulator and validate it against the EMI formula.
- Quantify interest saved by a lump-sum prepayment or a slightly higher EMI.
- Find the true rate of a flat-rate loan by root-finding (bisection and Newton).
- Recognise failure cases: unaffordable loans and negative amortisation.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A loan of 200000 units at 12 percent a year over 60 months has an EMI of 4448.89. You pay a lump sum of 50000 after month 12 and keep paying the same EMI. When does the loan end and how much interest is saved? Then find the true rate of a flat 8 percent, 36-month loan of 100000.

1. ______________________________  (hint: Without prepayment the simulation ends in 60 months with total interes...)
2. ______________________________  (hint: With the lump sum the balance drops by 50000 at month 12; the simulati...)
3. ______________________________  (hint: Interest saved = 66933.37 - 42482.30 = 24451.07 units; the loan ends 1...)
4. ______________________________  (hint: Flat 8 percent: interest = 100000 * 0.08 * 3 = 24000, instalment = 124...)
5. ______________________________  (hint: Solve EMI(100000, x, 36) = 3444.44 for x by bisection: x = 14.548 perc...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a lump sum paid early save more interest than the same lump sum paid late?

Answer: ______________________________________________


**B. Numerical.** A flat 8 percent loan of 100000 units for 3 years: find the total interest and the instalment, and compare the interest with a reducing 8 percent loan. Is the flat loan really cheaper than its name suggests?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the balance graph, what happens at the month of the lump sum, and how does the later part of the curve differ from the plain loan?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: monthly income is 30000 units and you decide an EMI may use at most 40 percent. At 12 percent over 60 months, what is the largest loan you can take? Then explain what goes wrong if someone pays only 800 per month on a 100000 loan at 12 percent.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
