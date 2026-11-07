# Coding tasks: Session 2

1. **Easy.** In `lesson.py` change the overhang depth `P` to 0.3 m and 1.0 m. Predict the sunlit share at noon on 21 June and 21 December in Delhi, then run it.
2. **Stretch.** Write `fin_sunlit_fraction(alt, az, facing, fin_depth, width)` for a vertical fin on one side of the window, using the horizontal shadow angle (the wall-solar azimuth gamma): the fin shades a width of fin_depth x tan(|gamma|). Check that a fin does nothing when the sun is straight in front.
3. **Explain in your own words.** Explain why the vertical shadow angle is larger than the sun altitude whenever the sun is not straight in front of the wall, and what this means for an overhang.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
