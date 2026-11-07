# Activity sheet: openclassifier, Session 4: Tune the forest by cross-validation

Name: ____________________   Date: ____________

**Objectives**

- Choose a hyperparameter (the tree depth) by k-fold cross-validation on the training data only, keeping the test set locked until the choice is made.
- Add random feature subsets to a bagged forest and tune it with a grid over depth.
- Compare two choice rules (best score, one standard error) and report the gain over the shipped forest with an error bar.
- Measure the optimism of peeking and of the best cross-validation score with a fresh test set.
- Recognise the failure cases: tiny data, an invalid k, and a test set that is an easy draw.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Four depths are cross-validated with 5 folds and give the fold scores: depth 1: 0.70, 0.74, 0.72, 0.70, 0.74; depth 2: 0.80, 0.78, 0.78, 0.78, 0.78; depth 3: 0.82, 0.76, 0.80, 0.78, 0.79; depth 4: 0.77, 0.75, 0.74, 0.76, 0.73. Find the mean of each depth, the standard error of the best, and the depth chosen by the best rule and by the one-SE rule.

1. ______________________________  (hint: The means are 0.720 (depth 1), 0.784 (depth 2), 0.790 (depth 3) and 0....)
2. ______________________________  (hint: The best mean is 0.790 at depth 3; the best rule chooses depth 3....)
3. ______________________________  (hint: The standard deviation of the depth-3 scores: the deviations from 0.79...)
4. ______________________________  (hint: SE = s / sqrt(5) = 0.0224 / 2.236 = 0.0100....)
5. ______________________________  (hint: The one-SE threshold is 0.790 - 0.010 = 0.780. Depth 1 (0.720) fails; ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why must the test set not be used to choose the tree depth, and what role does each of the three sets (the training folds, the held-out fold, the test set) play when the depth is chosen by cross-validation?

Answer: ______________________________________________


**B. Numerical.** An accuracy of 0.767 is measured on 500 test cases. Give its standard error and a 95 percent interval (about plus or minus two standard errors). How many test cases would give a standard error of 0.005?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the left panel of Figure 1 (training set 1) the cross-validation score is highest at depths 4 and 6, but test set A prefers depth 3 and the one-SE rule would take depth 2. Is cross-validation wrong here? What do the error bars say?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you have only 40 labelled cases and must choose the tree depth and make an honest statement about the accuracy. What do you do, and what do you tell the client?

Answer: ______________________________________________


## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
