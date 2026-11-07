# Coding tasks: Session 5

1. **Easy.** For a fan at 31.5 rev/s filmed at 30, 24 and 25 fps, compute the three apparent speeds with `signed_alias`, then print `common_speeds` for the first two clips and for all three, in the range 0 to 400. How many candidates does each give?
2. **Stretch.** Use `rate_table(30, 24, range(20, 61))` to find the third rates whose range is above 400 rev/s, and then the one whose range is the smallest above 400. Then check with `run_trials` (sigma = 0.3) that its share within 0.5 rev/s is not worse than for 29 fps.
3. **Explain in your own words.** Explain why the unambiguous range of three clips is the lcm of all three rates and not the largest of the pairwise ranges, using the example 30, 24 and 36 fps.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
