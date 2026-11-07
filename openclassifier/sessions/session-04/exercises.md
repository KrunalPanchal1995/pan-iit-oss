# Coding tasks: Session 4

1. **Easy.** Use `cv_grid` on training set 105 (`make_data(150, 105, flip=0.15)`) and print the mean fold score for every depth. Which depth do the best rule and the one-SE rule choose?
2. **Stretch.** Change the number of folds from 5 to 10 in `cv_grid` for the first five training sets of `tuning_table`. Does the chosen depth change, and what does that say about the noise in the choice?
3. **Explain in your own words.** Explain why the accuracy of the peeking choice on test set A is higher than on the fresh set B, although both choices are made with the same data and the same forests.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
