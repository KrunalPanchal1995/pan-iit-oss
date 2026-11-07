# Coding tasks: Session 3

1. **Easy.** Halve the time step in `simulate` from 1e-4 to 5e-5 and print the change of the final speed; explain why it is so small.
2. **Stretch.** Add a soft start to `simulate` by passing a list of voltages that ramps linearly from 0 to 12 V over 100 ms. Print the peak current and compare with the 5.70 A hard start.
3. **Explain in your own words.** Explain why the 3 A current limit makes the motor reach 90 percent of its speed later (403 ms) than the unlimited start (351 ms), and why many robots accept this.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
