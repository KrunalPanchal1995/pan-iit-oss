# Coding tasks: Session 2

1. **Easy.** Use `surface_temperature` to print Ts for eps = 0, 0.25, 0.5, 0.75 and 1 and check them against the left panel of the temperature figure.
2. **Stretch.** Write `two_layer_temperatures(eps)` for two layers with the same absorptivity eps (write the balances for the top, both layers and the surface, and solve them with `np.linalg.solve` on the sigma T^4 values). Check that eps = 1 gives Te x 3^(1/4) = 335 K, the N = 2 value.
3. **Explain in your own words.** Explain why the layer temperature Ta = Ts / 2^(1/4) does not depend on eps, and why the real lower air is much warmer than 242 K.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
