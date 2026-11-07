# Coding tasks: Session 5

1. **Easy.** Print the gate count and the slowest product-bit delay of `build_multiplier(n)` for n = 2, 3, 4. Predict each from 6n^2 - 8n and 6n - 8 first (n = 2 is a special case).
2. **Stretch.** Use `multiply` on all 256 pairs of 4-bit numbers and list every pair whose product is 36. Check your list against the divisors of 36 that are below 16.
3. **Explain in your own words.** Stretch: a multiplier that keeps only the low 4 bits gives the wrong answer for most pairs. Use `low_half` to count the pairs of 4-bit numbers where it is still right, and explain why the count is 76.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
