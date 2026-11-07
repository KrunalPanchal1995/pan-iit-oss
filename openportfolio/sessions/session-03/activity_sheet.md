# Activity sheet: openportfolio, Session 3: Many assets, the efficient frontier and its limits

Name: ____________________   Date: ____________

**Objectives**

- Show that diversification removes only the idiosyncratic part of risk, not the market part.
- Build a covariance matrix, check it is positive definite, and compute minimum-variance and frontier portfolios.
- Compute the Sharpe ratio and the tangency portfolio, and check against random portfolios.
- Quantify estimation error with a seeded simulation, and explain two failure cases.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Four assets, each with risk 0.20 and common correlation 0.3, held with equal weights. Find the portfolio variance and risk, and the limit as the number of assets grows.

1. ______________________________  (hint: Variance = 0.04 * (1/4 + (3/4) * 0.3) = 0.04 * (0.25 + 0.225) = 0.04 *...)
2. ______________________________  (hint: Risk = sqrt(0.0190) = 0.1378, that is 13.78 percent, about 31 percent ...)
3. ______________________________  (hint: Limit: s * sqrt(rho) = 0.2 * sqrt(0.3) = 0.1095, that is 10.95 percent...)
4. ______________________________  (hint: Check by simulation: 200000 years of one-factor returns give 0.1380 fo...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can you never diversify away all the risk by adding more and more assets, if they share a common correlation?

Answer: ______________________________________________


**B. Numerical.** Find the variance and risk of an equal-weight portfolio of N = 10 assets with s = 0.20 and rho = 0.3. By what percent is it below the risk of one asset?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the estimation-error figure, what is the predicted risk and the true risk for a history of T = 12 periods, and for T = 240? What does the gap tell you?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with s = 0.20 and rho = 0.3 you want a risk of at most 12 percent using equal weights. How many assets do you need? What if the assets had rho = 0.5? What does that say about a crisis?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
