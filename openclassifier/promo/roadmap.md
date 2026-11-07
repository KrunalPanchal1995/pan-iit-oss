# Roadmap: the path to the openclassifier Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 6: Beat the screening cost

**You will learn:** Cost-sensitive learning: class weights, resampling and calibrated probabilities.

**You will build:** A screening classifier chosen and tuned only with validation data.

**Checkpoint (not met by the shipped code):** A test cost below 1200 on the Session 3 screening split (the shipped forest costs 1230).

**Difficulty:** advanced

## Session 7: How sure is the AUC?

**You will learn:** Bootstrap resampling of the test set to put an error bar on a metric.

**You will build:** A 95 percent bootstrap interval for the AUC and a coverage experiment.

**Checkpoint (not met by the shipped code):** Over 100 simulated test sets, the interval contains the true AUC in at least 90 of them (the shipped code gives a single number and no interval).

**Difficulty:** advanced

## Session 8: Three classes and a 3 by 3 confusion matrix

**You will learn:** Multi-class confusion matrices, per-class precision and recall, and macro-averaging.

**You will build:** A classifier for three fruit types with a 3 by 3 matrix and macro-F1.

**Checkpoint (not met by the shipped code):** At least 90 percent of 300 test points on the right diagonal for three Gaussian clusters with centres (2, 2), (6, 2), (4, 6) and spread 1 (the shipped code handles two classes only).

**Difficulty:** advanced

## The final step

Combine the milestones: a dashboard that trains a tuned forest, shows its boundary, ROC curve and confusion matrix live as a threshold slides, and reports per-group error rates and a bootstrap interval for the AUC. If your result looks like the Target animation, open a pull request and tell us how you did it.
