# Coding tasks: Session 3

1. **Easy.** Run `trained(0.05, 8)` and print `eigenvalues(jacobian_at_origin(P))` next to `eigenvalues(A_TRUE)`. Which eigenvalue is closer to the truth, the real part or the imaginary part?
2. **Stretch.** Run `design_error(6, 0.05)` and `design_error(18, 0.05)`. Does more data still help at this lower noise? Explain.
3. **Explain in your own words.** Explain why the rollout-trained network is accurate inside the training box and fails outside it, and what you would add to the data to fix that.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
