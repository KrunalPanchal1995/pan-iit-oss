# Activity sheet: openodds, Session 3: Monte Carlo simulation, its error, and when it fails

Name: ____________________   Date: ____________

**Objectives**

- Estimate a probability by seeded simulation and compare with the exact value.
- Use the standard error sqrt(p(1-p)/N) to say how accurate an estimate is and how many trials are needed.
- Explain the law of large numbers and why the gambler's fallacy is wrong.
- Show, with the 6-of-49 lottery, why simulation fails for rare events and exact counting or importance sampling is needed.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
How many simulated trials are needed to estimate a probability near 0.5 to within plus or minus 0.01 (95 percent)? Then find the expected loss on a Rs 100 lottery ticket when the jackpot is Rs 10 crore (Rs 100,000,000), counting only the jackpot.

1. ______________________________  (hint: Worst case p = 0.5: p(1-p) = 0.25....)
2. ______________________________  (hint: N >= 1.96^2 x 0.25 / 0.01^2 = 3.8416 x 0.25 / 0.0001 = 9604 trials....)
3. ______________________________  (hint: Check: SE = sqrt(0.25 / 9604) = 0.0051, and 1.96 x 0.0051 = 0.0100....)
4. ______________________________  (hint: Lottery: P(jackpot) = 1 / 13,983,816. Expected jackpot winnings = 100,...)
5. ______________________________  (hint: Expected loss = 100 - 7.15 = Rs 92.85 per ticket, ignoring smaller pri...)

Final answer: ____________________

## Questions
**A. Conceptual.** A coin has landed heads 5 times in a row. A friend says tails is now due. Another says the coin must be biased. Who is right?

Answer: ______________________________________________


**B. Numerical.** You want to estimate P(two dice sum to at least 9) = 10/36 with a 95 percent half-width of 0.005. How many trials? How many if you want 0.0005?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the band figure, a run leaves the grey band at N = 200 but is inside it at N = 20000. Is the simulation broken?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design a fair game: pay Rs 10, roll two dice, win a gross payout if the sum is at least 9. What payout makes it fair? Choose N to check it by simulation to within a standard error of 0.05 Rs and say what you would see for a payout of Rs 30.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
