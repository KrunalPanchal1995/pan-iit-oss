# Coding tasks: Session 2

1. **Easy.** Use `cutoff_hz` and `gain` to print the gain at 10, 100 and 1000 Hz for R = 4.7 kohm and C = 100 nF; check that the last two differ by about 20 dB.
2. **Stretch.** Write `design_for_attenuation(att_db, f_hum, C)` that returns the stock (E24) resistor giving at least att_db of hum removal, and use it for 30 dB of 50 Hz hum with C = 1 uF.
3. **Explain in your own words.** Explain, using a sketch of the Bode plot, why a cutoff 10 times above the hum frequency barely helps and a cutoff 10 times below it helps a lot.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
