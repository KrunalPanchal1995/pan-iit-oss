# Activity sheet: openclassifier, Session 5: A threshold for each group

Name: ____________________   Date: ____________

**Objectives**

- Compute the error rates of a group from its share of positives, the quality of its instrument and its shift, and invert them to find the threshold for a wanted false-positive rate.
- Build a tool that picks one threshold per group so that the false-positive rates agree, and reports both groups' error rates.
- Explain with the odds form of Bayes' rule why equal FPR, equal TPR and equal PPV cannot all hold when the groups differ in prevalence.
- Price the repair in three situations (free, a PPV gap, a TPR floor) in errors and false alarms per 1000 people.
- Set thresholds from data on a calibration set and say how many cases it takes.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Groups A and B both have d = 1.5; B's scores are shifted up by 0.5. A single threshold t = 1 gives A a false-positive rate of 0.159. Find the threshold for B that gives it the same rate, and the true-positive rate of both groups there.

1. ______________________________  (hint: For A at t = 1: FPR = 1 - Phi(1) = 0.1587....)
2. ______________________________  (hint: For B we need 1 - Phi(t - 0.5) = 0.1587, so t - 0.5 = 1 and t = 1.5....)
3. ______________________________  (hint: TPR of A at t = 1: 1 - Phi(1 - 1.5) = 1 - Phi(-0.5) = 0.6915....)
4. ______________________________  (hint: TPR of B at t = 1.5: 1 - Phi(1.5 - 0.5 - 1.5) = 1 - Phi(-0.5) = 0.6915...)
5. ______________________________  (hint: Both are above the floor 0.6, and the gap in the false-positive rates ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Two groups have different shares of positive cases. Why can a classifier not give them equal false-positive rates, equal true-positive rates and equal PPV all at once, and which of the three should a clinic give up?

Answer: ______________________________________________


**B. Numerical.** Group C has prevalence 0.2, group D prevalence 0.4. Both have d = 1.5 and no shift, and both are judged at the threshold 1.0. Find the FPR, TPR and PPV of each. What TPR would D need, at the same FPR, to have the PPV of C?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the third panel of Figure 2 the two groups have the same false-positive rate and B's true-positive rate is 0.50 against 0.69 for A. In the fourth panel the common false-positive rate is raised to 0.228. Who gains, who pays, and why can no choice of thresholds remove the difference?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a clinic has only 300 labelled cases from group B (prevalence 0.3) and 20000 from group A. It wants B's false-positive rate to match A's within 0.01. What do you build, and what do you promise the clinic?

Answer: ______________________________________________


## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
