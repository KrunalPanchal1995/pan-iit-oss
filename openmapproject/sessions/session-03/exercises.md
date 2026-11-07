# Coding tasks: Session 3

1. **Easy.** Print `distortion` for the four projections at latitude 45 degrees and read off which is conformal and which is equal-area.
2. **Stretch.** Change `h` in `jacobian_fd` to 1e-2, 1e-5 and 1e-9 and print the error in the Mercator area scale at 60 degrees. Which step is best and why?
3. **Explain in your own words.** Explain why the sinusoidal map has area scale 1 everywhere, using the derivatives x_lambda / cos phi = 1, x_phi = -lambda sin phi, y_lambda = 0 and y_phi = 1.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
