# Coding tasks: Session 5

1. **Easy.** For a 50 x 30 mm pocket with a 10 mm boss at (25, 15), use `clearance` and `max_clearance` to find the largest clearance, and check it against the closed form from question B. At which clearance does `level_components` first report two pieces?
2. **Stretch.** In the 60 x 40 mm pocket with a 14 mm boss, the coverage repair adds a whole ring (250 mm per layer). Add a cheaper repair: after `plan_pocket(..., refine=False)`, cut one short straight line across the uncut block at its mid height, and check with `uncovered_cells` and `simulate_moves` that the volume is within 0.5 percent of the target. How much shorter is the layer?
3. **Explain in your own words.** Explain why `level_offsets` does not simply use spacing r instead of the stepover, and what the coverage check adds that the spacing rule alone cannot.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
