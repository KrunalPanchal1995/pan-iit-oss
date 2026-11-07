# Coding tasks: Session 3

1. **Easy.** Change the hidden activation in `train` to "relu" with the "he" initialisation and compare the loss after 40 epochs on the moons data with the tanh value printed by the lesson.
2. **Stretch.** Add a deliberate bug to `backward` (for example drop the division by N) and run `grad_check`. Describe how the error changes, then remove the bug.
3. **Explain in your own words.** Explain why, with all weights zero, the two hidden neurons of a network always receive exactly the same gradient, and how random initial weights break the tie.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
