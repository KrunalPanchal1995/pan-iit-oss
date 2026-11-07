# Activity sheet: openclassifier, Session 3: Judging a classifier honestly

Name: ____________________   Date: ____________

**Objectives**

- Build a ROC curve and AUC from scores, and verify that AUC is the probability that a random positive outranks a random negative.
- Show with measurements that a forest of bagged trees is more stable than one tree, and that deeper trees overfit.
- Write k-fold cross-validation and use it to estimate accuracy on unseen data.
- Compare error rates across two groups and demonstrate data leakage and the accuracy paradox as failure cases.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Four cases have scores 0.1, 0.4, 0.35, 0.8 and true labels 0, 0, 1, 1. Build the ROC curve and compute the AUC by area and as a probability.

1. ______________________________  (hint: Sort by score, highest first: 0.8 (positive), 0.4 (negative), 0.35 (po...)
2. ______________________________  (hint: Lower the threshold past each score and update (FPR, TPR): start (0, 0...)
3. ______________________________  (hint: Area under the curve by trapezoids: 0 + 0.5 x 0.5 + 0 + 0.5 x 1 = 0.25...)
4. ______________________________  (hint: Pairs (positive, negative): 0.35 > 0.1 yes, 0.35 > 0.4 no, 0.8 > 0.1 y...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can training accuracy reach 100 percent while test accuracy falls as a tree gets deeper? Why does a forest of trees help?

Answer: ______________________________________________


**B. Numerical.** Group B's scores are shifted up by 0.5 relative to group A, negatives are centred at 0 and the threshold is 1.0. Compute each group's false-positive rate with Phi(1) = 0.8413 and Phi(0.5) = 0.6915.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the overfitting figure, which depth would you choose and why? What does the gap between the two curves tell you?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a screening problem has 5 percent positives; a miss costs 20 and a false alarm costs 1. You may choose a depth-3 tree, a depth-8 tree or a 25-tree forest and a threshold. Which would you pick and how do you justify it?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
