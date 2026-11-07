# Coding tasks: Session 2

1. **Easy.** Run `simulate_altitude(4, 0, kd, mass=1.4)` for Kd = 2, 4 and 8 N s/m. Predict the overshoot of each with `overshoot_formula`, then measure it with `step_metrics`.
2. **Stretch.** Add measurement noise: inside `simulate_altitude`, give the PID a height with random noise of 2 cm (`np.random.normal(0, 0.02)`). Which gain makes the thrust most jumpy, and why?
3. **Explain in your own words.** Explain why we use the measured climb rate dz/dt in the D term instead of the rate of change of the error, and what would happen to the thrust if the target jumped from 0 to 2 m.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
