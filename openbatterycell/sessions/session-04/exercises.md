# Coding tasks: Session 4

1. **Easy.** Use `pack_report` to print the start voltage, the runtime and the limit ("start", "cutoff" or "exhausted") of the 12 x 2 pack at -10, -5 and 0 C and explain what changes between them.
2. **Stretch.** Use `design_search(temps_c=(-10.0, 0.0, 25.0, 45.0))` and compare the smallest working pack with the 24 cells of Section E. Which temperature sets the size now, and how many cells does a lower-resistance cell (`r0=0.56`) save?
3. **Explain in your own words.** Explain, in your own words and with R_eq = R npar / ns, why the pack behaves like one cell, and why adding series cells beyond the minimum can shorten the run.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
