# Coding tasks: Session 1

1. **Easy.** In `lesson.py`, change the jitter frequency to 100 Hz (`JITTER_HZ`) and predict, then check, whether the same filter now removes more or less of it.
2. **Stretch.** Write `best_tau(target_jitter)` that returns the smallest tau (searching the values 0.002 s to 0.5 s) for which the jitter kept is below target_jitter, and print how much of the slow signal that costs.
3. **Explain in your own words.** Explain, in two sentences and without formulas, why a filter that removes more jitter always makes the output later.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
