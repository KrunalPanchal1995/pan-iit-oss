# Coding tasks: Session 4

1. **Easy.** Use `romberg_table` on f(x) = x^2 over [0, 3] with 2 levels and predict the first column and R(1,1) by hand before running (the exact area is 9). Which column is already exact, and why?
2. **Stretch.** Use `romberg_tol` on exp(-x^2) over [0, 2] with the tolerances 1e-4, 1e-6, 1e-8 and 1e-10 and tabulate the number of values it uses. Compare with the Simpson counts of the README table, and say why the Romberg count rises in steps of a doubling.
3. **Explain in your own words.** Explain why the trapezoid rule is almost perfect for exp(sin(2 pi x)) over [0, 1] while Romberg makes it worse, and how the stopping rule of `romberg_tol` can claim success with only 3 values.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
