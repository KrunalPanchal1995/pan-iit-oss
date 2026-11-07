# Coding tasks: Session 3

1. **Easy.** Change `abc_network(0.5, 0.2, 0.1)` to kr = 0 and k2 = 0 and show that RK4 gives A0 exp(-k t) for A; then print the largest error.
2. **Stretch.** Write `ab_c_d_network` with a stoichiometry matrix for A -> B, B -> C and C -> D, solve it with `rk4`, and show that the sum of the four concentrations stays 1.
3. **Explain in your own words.** Explain in your own words why the explicit solver with h = 1e-3 fails although the answer after a millisecond is smooth, and why backward Euler with h = 0.05 does not.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
