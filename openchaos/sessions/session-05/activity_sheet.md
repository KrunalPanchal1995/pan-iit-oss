# Activity sheet: openchaos, Session 5: Ensemble forecasts

Name: ____________________   Date: ____________

**Objectives**

- Run an ensemble of 1000 forecasts from a Gaussian cloud of start errors and measure how fast the cloud spreads.
- Turn the cloud into a probability that the outer rod has flipped, and state its sampling error.
- Check that the answer is converged: different seeds, then a halved time step.
- Say how much a better instrument buys, and why a probability is not a promise about one pendulum.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A forecast of the 95 degree release from 1000 members says that 77 percent have flipped by 20 s. What is the sampling standard error and a 95 percent interval? How many members give a standard error of 0.01?

1. ______________________________  (hint: SE = sqrt(P (1 - P) / N) = sqrt(0.77 x 0.23 / 1000) = sqrt(1.771e-4) = 0.01...)
2. ______________________________  (hint: A 95 percent interval is about plus or minus 1.96 SE = 0.026, so 0.74 to 0....)
3. ______________________________  (hint: For SE = 0.01: N = P (1 - P) / SE^2 = 0.1771 / 0.0001 = 1771, so about 1800...)
4. ______________________________  (hint: Four times as many members (4000) halve the error: sqrt(0.1771 / 4000) = 0....)
5. ______________________________  (hint: Check with the simulation: four different seeds give 0.773, 0.766, 0.780 an...)

Final answer: ____________________

## Questions
**A. Conceptual.** After the spread time, why does a forecaster report a probability instead of a path, and what can still go wrong with that probability?

Answer: ______________________________________________


**B. Numerical.** For the 95 degree release the probability of a flip by 20 s is about 0.77 with 1000 members. A report must give it with a standard error of 0.005. How many members are needed, and how long will the run take if 1000 members take 2.3 s? Give a sanity check.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In Figure 3 the probability of a flip by 20 s is 0.708 for h = 0.01 s, 0.773 for 0.005 s and 0.785 for 0.0025 s, with a sampling standard error of 0.013. Can sampling explain the change from 0.01 s to 0.005 s? Which step would you report?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you must publish the probability that the outer rod of the 95 degree release has flipped by 20 s, accurate to plus or minus 0.02 with 95 percent confidence. Choose the number of members and the step, say how you will check convergence, and name one thing the number does not cover.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
