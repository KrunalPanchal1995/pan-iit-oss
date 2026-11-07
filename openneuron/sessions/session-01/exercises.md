# Coding tasks: Session 1

1. **Easy.** In `lesson.py` change the leak to 0.2 and predict the smallest drive that can fire before you run it (use the formula d = k (V_th - V_rest)).
2. **Stretch.** Write `first_spike_step(drive)` that finds the first spike by looping over `toy_neuron`, and compare it with `steps_to_first_spike` for drives 2.0, 3.0 and 4.0.
3. **Explain in your own words.** Explain why doubling the drive does not exactly double the number of spikes in 100 ms. (Hint: look at the time it takes the voltage to climb and at the refractory time.)

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
