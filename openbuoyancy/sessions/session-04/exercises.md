# Coding tasks: Session 4

1. **Easy.** Use `make_tank`, `free_surface_correction` and `gm_effective` to find the effective GM of the 120 t barge cargo in tanks 10 m long and 3.0, 4.0 and 5.0 m wide (use `height=8.0` for the 3.0 m tank so that the liquid fits). Write down the three numbers. By what factor does FSC change from 3.0 to 5.0 m, and does it match (5.0 / 3.0) cubed?
2. **Stretch.** For the 10 x 5.8 m tank find, with `max_tank_width` and `gm_effective`, the smallest number of longitudinal compartments that gives GM_eff of at least 0.75 times the solid-cargo GM, and check your answer with `effective_gm_exact`. Does the exact value agree with the formula to 0.002 m?
3. **Explain in your own words.** A shipmate says: "the tank is only half full, so the free surface is small and we can ignore it". Explain with the picture of the liquid wedge, and with the 20 and 80 percent fill points in the third figure, why that is wrong.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
