# Coding tasks: Session 5

1. **Easy.** With `make_group` build a group C with prevalence 0.2 and a group D with prevalence 0.4 (d = 1.5, no shift). Use `rates` at the threshold 1.0 and print the PPV of each. Which group gets the more reliable flag?
2. **Stretch.** Replace the quantile in `fit_thresholds` by a normal-curve fit: the mean and the standard deviation of a group's negative scores give the threshold `mean + sd x inv_phi(1 - f)`. Repeat `gap_study` for 500 cases per group. Is the gap smaller than with the quantile, and which assumption did you add?
3. **Explain in your own words.** Explain why raising the common false-positive rate (policy 2 in the app) helps group B but also changes group A's results, although A's instrument did not change.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
