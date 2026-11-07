# Coding tasks: Session 1

1. **Easy.** In `lesson.py` change the stage-2 Isp in `LAUNCHER` from 340 s to 450 s (a hydrogen engine). Predict whether the total delta-v rises by more or less than 1 km/s, then run it.
2. **Stretch.** Write `best_split(total_prop, dry_share, isp1, isp2, payload)` that tries every stage-1 propellant mass in 1 t steps and returns the split with the largest `stack_delta_v`. Check that it finds about 100 t for Question D.
3. **Explain in your own words.** Explain why a single-stage rocket to orbit would need about 96 percent of its lift-off mass to be propellant (Isp 300 s, 9.4 km/s), and why that is so hard to build.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
