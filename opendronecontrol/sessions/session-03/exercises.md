# Coding tasks: Session 3

1. **Easy.** Run `simulate(tau_m=tm)` for tm = 0.02, 0.10 and 0.13 s and print `metrics` for each. Describe how the settling time and the largest tilt change as the motors get slower.
2. **Stretch.** Add a sideways gust: in `simulate`, add a constant force of 1 N to `m y''` between t = 2 and 3 s. Does the drone return to y = 1 m? Add an integral term to the position loop and compare.
3. **Explain in your own words.** Explain why spinning the left rotors faster rolls the drone to the right, and why the outer loop limits the tilt it asks for.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
