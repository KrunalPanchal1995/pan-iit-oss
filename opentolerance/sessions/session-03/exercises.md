# Coding tasks: Session 3

1. **Easy.** Use `simulate_gaps(t, 100000, 1, drift=1.0)` with equal tolerances of 0.10 mm and compute the fraction out with the limits from `spec_limits()`; compare with `fraction_out`.
2. **Stretch.** Change `K_COST` so that one part is 20 times as expensive to tighten as the others; run `allocate_rss` and describe how the tolerances change.
3. **Explain in your own words.** Explain why the cube root of k, not the square root, appears in the RSS allocation, and why the square root appears for worst case.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
