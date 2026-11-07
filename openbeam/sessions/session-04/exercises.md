# Coding tasks: Session 4

1. **Easy.** Change the group to three axles of 20 kN with spacings of 4 m and 5 m on a 20 m span (`make_group([20e3, 20e3, 20e3], [4.0, 5.0])`). Run `envelope` and `worst_moment_by_hand`. Do they agree, and under which axle is the peak?
2. **Stretch.** Sweep the span instead of the spacing: keep two 10 kN axles 3 m apart and plot the envelope peak for spans from 4 m to 20 m. Where does the hand formula P (L - d/2)^2 / (2 L) stop being the answer because the spacing passes 0.586 L?
3. **Explain in your own words.** Explain why the worst bending moment is not under an axle at mid-span, and why the worst mid-span deflection is found with the pair centred.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
