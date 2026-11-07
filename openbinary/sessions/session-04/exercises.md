# Coding tasks: Session 4

1. **Easy.** Print the gate count and the carry delay of `build_flat(n)` and `build_prefix(n)` for n = 2, 4, 8. Predict the prefix delays first from 2k + 3 where n = 2^k.
2. **Stretch.** Find a pair (a, b) of 16-bit numbers with carry in 0 whose longest carry run is exactly 16, and one whose longest run is exactly 8. Print `carry_sources` for each and say which stages generate and which pass the carry on.
3. **Explain in your own words.** Stretch: in `build_flat` every term builds its own AND tree. Share the products of p between terms so each product is built once, then print the new gate count and carry delay at 16 bits and check the adder with `mismatches`.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
