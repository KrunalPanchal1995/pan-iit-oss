# Coding tasks: Session 3

1. **Easy.** Run `calibrate(make_dataset(seed=5), [0, 0])` and compare the result and the uncertainty with seed 1. Does the truth stay inside two sigma?
2. **Stretch.** Change the noise to 0.10 in `make_dataset(sigma=0.10)`, fit again and compare the predicted uncertainty with the observed scatter over several seeds.
3. **Explain in your own words.** Explain why the implicit solver can use a step size that makes explicit RK4 return nan, and say what the price of an implicit step is.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
