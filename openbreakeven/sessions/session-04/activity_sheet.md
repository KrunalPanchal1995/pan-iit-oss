# Activity sheet: openbreakeven, Session 4: When price and demand move together

Name: ____________________   Date: ____________

**Objectives**

- Draw two random inputs with a chosen correlation and check that the sample has it.
- Show that a correlation between price and demand changes the spread of profit and the loss probability while the mean barely moves.
- Validate the simulation against exact formulas for the mean and the standard deviation of profit.
- Estimate which correlation a demand line implies, and find the largest correlation that meets a lender's limit on the loss probability.

## Before you start: predict
In your own words, what do you think happens to the chance of a loss month if a high price tends to come with low demand (negative correlation)?

______________________________________________________________

## Worked example (fill in as you go)
The bakery sells loaves at 3.50 dollars (variable cost 1.40), with F = 1200 dollars a month, a price wobble of 0.20, a cost wobble of 0.15 and demand of 800 loaves with sd 150. Find the mean and the standard deviation of monthly profit for correlation -0.5 and estimate the loss probability.

1. ______________________________  (hint: planned profit 2.10 x 800 - 1200; Cov = rho x 0.20 x 150)
2. ______________________________  (hint: mean = planned profit + Cov)
3. ______________________________  (hint: sigma_X^2 = 0.20^2 + 0.15^2 = 0.0625, then the variance formula)
4. ______________________________  (hint: z = -mean / standard deviation, P(loss) = Phi(z))
5. ______________________________  (hint: compare with the simulated 5.6 percent and with 9.5 percent for independent inputs)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a negative correlation between price and demand make the bakery's profit less risky, although it hardly changes the average profit?

Answer: ______________________________________________


**B. Numerical.** Find the mean and the standard deviation of monthly profit for correlation +0.5 by hand, and use them to estimate the loss probability with the normal shortcut. How does it compare with the 12.4 percent of the simulation?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the loss-probability figure, the independent case (correlation 0) lies at 9.5 percent, above the lender's 8 percent, and the demand-line value (-0.33) lies below it. What can you conclude, and what can you not conclude?

Answer: ______________________________________________


**D. Design and optimisation challenge.** A lender asks for a loss probability of at most 5 percent. The owner can cut the fixed cost in steps of 50 dollars from 1200. What is the highest fixed cost that meets the limit (a) with independent inputs and (b) with the demand-line correlation of -0.33? How safe is the answer?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
