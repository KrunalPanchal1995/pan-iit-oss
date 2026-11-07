# Coding tasks: Session 4

1. **Easy.** Make one noisy measurement of a 31.5 rev/s fan with `noisy_apparent(31.5, 30, 0.3, rng)` and `noisy_apparent(31.5, 24, 0.3, rng)` (use `np.random.default_rng(3)`). Print the answer of `recover_noisy` with its `sd` and `margin`, and the error. Is the true speed inside the band of 2 standard deviations?
2. **Stretch.** Run `run_trials("pairs", 0.3, 2000, fs2=p)` for the second rates p = 20, 25 and 29 and print the share right and `wrong_pair_probability`. Find the noise at which the pair 30 and 29 fps drops below 95 percent, and say why 29 fps is a bad partner although its range is 870 rev/s.
3. **Explain in your own words.** Explain why the error of the recovered speed cannot be smaller than sigma / sqrt(2) however clever the rule, and what you would change in the experiment to make it smaller.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
