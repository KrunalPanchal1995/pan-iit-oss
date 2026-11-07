# Coding tasks: Session 3

1. **Easy.** Run `rk4_fixed(1000.0, make_params(), dt, 3e-3)` for dt = 1.3, 1.45, 1.6 and 2.0 microseconds and print the final state. Which are correct?
2. **Stretch.** Add the pressure exponent m = 1.5 in `delay_at_pressure` and check by hand how much shorter the delay at 4 atm becomes.
3. **Explain in your own words.** Explain, with the Jacobian, why backward Euler is stable at any step but still smears the ignition time when the step is longer than the delay.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
