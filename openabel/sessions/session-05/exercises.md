# Coding tasks: Session 5

1. **Easy.** Make a 3 percent photo with `noisy(clean_candle_full(0.7), 0.03, np.random.default_rng(7))` and print the axis from `axis_centroid` and from `axis_mirror`. How far is each from 0.7? Then print `worst_row_error` once with the axis 0 and one half, and once with the mirror axis and both halves.
2. **Stretch.** Use only the 5 rows of the photo around 8 mm (`img[5:10]`) in `axis_mirror`, and compare the scatter of the axis over 20 draws with the scatter when you use all 20 rows. Then repeat with `blur=0.01` (almost no smoothing) and say what you see.
3. **Explain in your own words.** Explain why a one-pixel mistake in the axis costs about as much as 3 percent noise, and why finding the axis lets you use both halves of the photo.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
