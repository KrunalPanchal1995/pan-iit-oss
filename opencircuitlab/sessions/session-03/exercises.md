# Coding tasks: Session 3

1. **Easy.** Use `solve_network` to find V_A for the two-loop circuit with R3 changed to 600 ohm and compare with `two_loop` from Session 2.
2. **Stretch.** Build a 4-node ladder of your own (five resistors, one 9 V source) with `solve_network`, print the node voltages, and check the power balance with `power_balance`.
3. **Explain in your own words.** Explain why the Monte Carlo output of the bridge is centred on zero but never exactly balanced, and how the spread would change if you used 2 percent resistors (predict with `predicted_offset_std`, then check).

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
