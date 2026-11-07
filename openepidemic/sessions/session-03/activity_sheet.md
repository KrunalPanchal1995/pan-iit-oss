# Activity sheet: openepidemic, Session 3: Simulate, fit and test: SIR with data, chance and vaccination

Name: ____________________   Date: ____________

**Objectives**

- Write and validate your own RK4 solver against conservation, the final-size equation and the early growth rate.
- Fit beta and gamma to synthetic noisy case counts by least squares and measure the uncertainty by repeating the experiment.
- Show that early data cannot separate beta from gamma, and explain the failure cases (fitting before the peak, reporting delays).
- Use a stochastic simulation to show that small outbreaks die out with probability about 1/R0, and use the model to choose a vaccination coverage under a capacity line.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A synthetic town of 50000 people has 10 infected people, beta = 0.4, gamma = 0.2 per day and a vaccine with efficacy 0.9. Its hospital line is 3000 people infected at once. Find the smallest whole-percent coverage that keeps the peak under the line.

1. ______________________________  (hint: R0 = 0.4 / 0.2 = 2. Without vaccination the RK4 simulation gives a pea...)
2. ______________________________  (hint: Protected share = coverage * 0.9. At 23 percent coverage the protected...)
3. ______________________________  (hint: At 24 percent coverage the protected share is 21.6 percent: R_eff = 1....)
4. ______________________________  (hint: Note that R_eff is far above 1 in both cases: the line is kept not by ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can the first two weeks of data fix the growth rate beta - gamma well but not beta and gamma separately?

Answer: ______________________________________________


**B. Numerical.** A fit to the first 14 days of the seed-1000 data gives beta = 0.477 and gamma = 0.288. Compute R0 and beta - gamma, and compare both with the truth (beta 0.4, gamma 0.2).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In Figure 2, compare the left panel (14 days) and the right panel (60 days). What does the diagonal shape mean, and what should a modeller conclude from it?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the hospital line is 1000 people for the synthetic town of the worked example (efficacy 0.9, beta 0.4, gamma 0.2). Find the smallest coverage, then say what margin you would add if beta is uncertain by 10 percent, and state one trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
