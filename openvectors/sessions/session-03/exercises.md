# Coding tasks: Session 3

1. **Easy.** Print the landing point and time of `simulate(4, 3, 0.5, K=k)` for k = 0, 2 and 4, and describe in two sentences how the answer changes.
2. **Stretch.** Halve the time step in `simulate` from 0.05 to 0.025 and show that the landing point of the feedback boat changes by less than 0.1 m, then repeat with `method="euler"` for the fixed heading at dt = 0.5 and dt = 0.25 and compare the errors against 30.0 m.
3. **Explain in your own words.** Explain the failure case: why does a 4 m/s boat in a uniform 5 m/s current drift at least 45 m, whatever the heading? Which heading gives that minimum?

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
