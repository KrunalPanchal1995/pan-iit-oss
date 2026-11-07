# Coding tasks: Session 4

1. **Easy.** Write a netlist of the Session 3 divider (12 V, 1 kohm, 2 kohm, 1 kohm load on the middle node) as a string, solve it with `solve_netlist` and check the load voltage against 4.8 V.
2. **Stretch.** Add a rule to `check_netlist`: a warning for any voltage source above 50 V. Test it on a file of your own and on `TECH_NETLIST` (which must not change).
3. **Explain in your own words.** Explain why the solver accepts `R2 out 0 1M` without complaint although it is almost surely a mistake, and what a person or program has to add to catch it.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
