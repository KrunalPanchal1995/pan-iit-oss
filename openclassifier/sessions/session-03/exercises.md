# Coding tasks: Session 3

1. **Easy.** Use `roc_curve` and `auc_pairs` on your own list of 6 scores and labels. Work out the AUC by hand first.
2. **Stretch.** Change the group shift in `group_rates_analytic` to 1.0 and find a threshold that equalises the true-positive rates but not the false-positive rates. What does that tell you about using one threshold?
3. **Explain in your own words.** Explain why scaling the features with statistics from the whole data set before cross-validation is a form of leakage, and write the version that scales inside each fold.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
