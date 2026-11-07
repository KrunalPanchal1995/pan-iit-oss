# Coding tasks: Session 3

1. **Easy.** Run `rrt(CLUTTER, seed=s)` for seeds 0 to 9 and print the raw path length of each. How much do they vary? Then smooth each with `shortcut`.
2. **Stretch.** Write `clearance(path, obstacles)` that returns the smallest distance from sampled path points to any circle, and print it for the exact wall path (it is 0).
3. **Explain in your own words.** Explain why the exact shortest path around a wall must touch the wall's corners, and why the collision test must therefore allow touching.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
