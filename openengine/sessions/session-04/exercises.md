# Coding tasks: Session 4

1. **Easy.** Print `cp_air`, `cv_air` and `gamma_air` at 300, 600, 1000, 1500 and 2500 K, and check two of them against a cp table for air in a textbook.
2. **Stretch.** Write `otto_r_for_eta_variable(eta, q_in)` that finds the compression ratio for a target efficiency by bisection on `otto_cycle`, and check that r = 14.4 gives 0.60 at q_in = 1100 kJ/kg.
3. **Explain in your own words.** Explain why the Diesel cycle loses even more efficiency to variable cp than the Otto cycle at its usual r = 18 (compare `diesel_cycle` with `ConstantGas()` and without; hint: heat at constant pressure uses cp, and the expansion starts from a higher volume).

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
