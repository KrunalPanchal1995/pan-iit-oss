# Coding tasks: Session 5

1. **Easy.** Use `series_diode` to find the diode voltage and current for a 3.3 V supply and a 220 ohm resistor, and check them with `series_diode_exact`.
2. **Stretch.** Build the network 9 V, 1 kohm, two diodes in series, 470 ohm with `newton_solve` (diodes `[(2, 3), (3, 4)]`) and check the power balance. How many passes does it need?
3. **Explain in your own words.** Explain why the plain loop from 0.5 V needs 18 passes while the one from 0.6 V needs 5, using the shape of the diode curve.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
