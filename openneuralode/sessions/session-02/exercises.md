# Coding tasks: Session 2

1. **Easy.** Run `error_at_T(euler_step, h)` and `error_at_T(rk4_step, h)` for h = 0.4 and print them. Which method is more accurate at h = 0.4? Predict the ratio of errors for h = 0.1 before you run it.
2. **Stretch.** Change the noise to `sigma = 0.05` in `make_data` and train the network again. Report the field error and the loss, and explain why the loss ends higher.
3. **Explain in your own words.** Explain why the one-step loss can be very small while predictions 3 seconds ahead are poor. (Hint: what does the loss not see?)

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
