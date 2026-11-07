# Coding tasks: Session 3

1. **Easy.** Run `clock_drift(h, 23)` for h = 10, 24, 100 and 200 and check that the error is proportional to h; predict the 200 hour value before you run it.
2. **Stretch.** Write `sum_in_chunks(x, size)` that sums blocks with the naive loop and then adds the block sums, and compare its error with naive and Kahan for 0.1 repeated 1e6 times.
3. **Explain in your own words.** Explain why wrapping 40000 to -25536 is more dangerous than raising an exception, and describe where in a program you would place the range check.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
