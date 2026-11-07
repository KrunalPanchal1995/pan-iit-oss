# Coding tasks: Session 4

1. **Easy.** Make a 3 percent candle photo with `noisy_candle(clean_candle(), 0.03, np.random.default_rng(7))` and print the lam chosen by `choose_lam` with each of the three rules. Then print `worst_row_error` for each choice and for `oracle_lam`. Which rule is closest to the oracle on your photo?
2. **Stretch.** Replace the noise estimate by the margin estimate: `choose_lam(img, "upre", sigma=noise_sigma_margin(img))`. Compare its mean worst-row error over 20 draws with the curvature estimate. Which is more reliable, and what must be true of the picture for the margin estimate to work?
3. **Explain in your own words.** Explain why the discrepancy principle picks a stronger smoothing than the best one, and why UPRE does not.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
