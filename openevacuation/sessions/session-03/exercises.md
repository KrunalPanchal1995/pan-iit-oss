# Coding tasks: Session 3

1. **Easy.** In `lesson.py` change the final exit width from 1.5 m to 1.0 m. Predict whether the stair or the exit becomes the bottleneck, then run it and look at the queue figure.
2. **Stretch.** Give each floor its own pre-movement time (for example floor 3 reacts 60 s later because the alarm is quieter there) by adding a `t_pre_by_floor` list to `building`, and measure how much the evacuation time changes.
3. **Explain in your own words.** Explain why a building with two stairs must be checked with one stair blocked, and why that case, not the normal case, usually sets the stair width.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
