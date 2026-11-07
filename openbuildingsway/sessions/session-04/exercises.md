# Coding tasks: Session 4

1. **Easy.** For the frame of the lesson, use `modal_base_shears` and `srss` to compute the SRSS base shear with 1, 2 and 3 modes, and `time_history_base_shear` for the reference. Write down the three errors. Does adding the third mode change the estimate by more than 1 percent? Why or why not (look at the effective masses)?
2. **Stretch.** Repeat the comparison with 2 percent damping instead of 5 (`zeta=0.02` in `shortcut_base_shear` and in `time_history_base_shear`). Do both numbers go up or down, and does the error stay within 5 percent? Then find with `error_vs_stiffness`-style loops the first stiffness (100 to 1500 MN/m in steps of 100) at which the 2-mode SRSS and the 3-mode SRSS differ by more than 0.5 percent, or say that none does and explain why.
3. **Explain in your own words.** A colleague says: "the shortcut is exact because it uses the spectrum of the very same record". Explain with the soft 100 MN/m frame, where mode 1 peaks at 2.92 MN and the full run peaks at 2.62 MN, what the shortcut still assumes about the modes.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
