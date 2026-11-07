# Activity sheet: openneuron, Session 1: A neuron adds up signals and fires a spike

Name: ____________________   Date: ____________

**Objectives**

- Describe how a neuron collects signals, sums them and fires an all-or-nothing spike at a threshold.
- Use the rise-and-leak update to predict whether a constant input can ever fire the neuron.
- Read a voltage-versus-time trace and tell a spike from a sub-threshold wobble.
- Compute the delay of a spike along an axon from its length and speed.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A constant drive of 2.0 mV per ms is applied from rest. Will the neuron fire, and after how many milliseconds?

1. ______________________________  (hint: Settling level: V_inf = -70 + 2.0 / 0.1 = -50 mV. That is above the th...)
2. ______________________________  (hint: With the drive constant the climb is V(n) = -70 + 20 (1 - 0.9^n). We n...)
3. ______________________________  (hint: n = ln 0.25 / ln 0.9 = 13.16 steps, so 13 steps are not enough and 14 ...)
4. ______________________________  (hint: Check: V(13) = -55.08 mV (just below the threshold) and V(14) = -54.58...)
5. ______________________________  (hint: The simulation agrees: the first spike is at 14 ms and there are 6 spi...)

Final answer: ____________________

## Questions
**A. Conceptual.** A stronger stimulus does not make a bigger spike. So how does a nerve tell the brain that a touch is stronger?

Answer: ______________________________________________


**B. Numerical.** For a constant drive of 3.0 mV per ms find the level the voltage would settle at, and the step at which the first spike happens (hand calculation, then check with the code).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the trace for drive 1.0 mV per ms the voltage rises and then flattens out below the threshold line. What level does it flatten at, and why is there no spike?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a model neuron must fire at least 10 times in 100 ms, and a spike must cross a 0.5 m axon in under 5 ms. Choose a drive (in steps of 0.5 mV per ms) and an axon speed, and say what trade-off you see.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
