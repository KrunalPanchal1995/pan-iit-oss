# Coding tasks: Session 5

1. **Easy.** Use `dual_cycle(18, 1100, x)` for x = 0, 0.25, 0.5, 0.75 and 1 and print the efficiency and the peak pressure. Check the two ends against `diesel_eta` and `otto_eta`.
2. **Stretch.** Combine this session with Session 4: write `dual_cycle_variable(r, q_in, x)` that uses `u_air` for the constant-volume heat, `h_air` for the constant-pressure heat and `phi_air` for the isentropes, and compare the half split at r = 18 with the constant-gamma value of 0.676.
3. **Explain in your own words.** Explain why, under a fixed peak-pressure limit, raising the compression ratio forces you to move heat from constant volume to constant pressure, and why the efficiency can still go up.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
