# Coding tasks: Session 5

1. **Easy.** Call `gauss_legendre_nodes(4)` and check by hand that the nodes are symmetric, that the weights add up to 2, and that the 4-point rule gives the exact area of x^7 over [-1, 1] (zero) but not of x^8 (exact 2/9).
2. **Stretch.** For e^x on [0, 1] use `gauss_values_needed` to find the number of Gauss values for the targets 1e-6, 1e-8, 1e-10 and 1e-12, and compare with the Romberg counts from Session 4 (`evaluations_needed`). Which rule is cheaper at each target?
3. **Explain in your own words.** Explain why the 6-point Gauss rule cannot reuse the 5 values of the 5-point rule, why that matters when you do not know in advance how many points you need, and what a composite rule (`composite_gauss`) with an edge at a corner does about a function that is not smooth.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
