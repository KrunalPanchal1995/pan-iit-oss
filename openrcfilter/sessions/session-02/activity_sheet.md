# Activity sheet: openrcfilter, Session 2: The RC low-pass in numbers: tau, cutoff, decibels and the Bode plot

Name: ____________________   Date: ____________

**Objectives**

- Use the step response 1 - exp(-t / tau) and read tau from a graph.
- Compute the cutoff frequency, the gain and the phase of an RC low-pass at any frequency.
- Convert gain to decibels and read a Bode plot: -3 dB at f_c and -20 dB per decade above it.
- Solve a design problem (choose R and C, then compute how many dB of 50 Hz hum are removed) and predict the loading effect.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Design a low-pass with f_c = 100 Hz using C = 100 nF. Choose R (nearest E24 stock value), then compute tau, the actual cutoff, the gain at 50 Hz and how many dB of 50 Hz hum are removed. Then find the cutoff needed to remove 20 dB.

1. ______________________________  (hint: R = 1 / (2 pi f_c C) = 1 / (2 pi * 100 * 100e-9) = 15 915 ohm. The nea...)
2. ______________________________  (hint: tau = 16 000 * 100e-9 = 1.60 ms, and f_c = 1 / (2 pi * 0.0016) = 99.47...)
3. ______________________________  (hint: Gain at 50 Hz: f / f_c = 0.503, gain = 1 / sqrt(1 + 0.2528) = 0.8935....)
4. ______________________________  (hint: In dB: 20 log10(0.8935) = -0.98 dB. So only 0.98 dB of the hum is remo...)
5. ______________________________  (hint: For 20 dB we need gain 0.1: (f / f_c)^2 = 1 / 0.1^2 - 1 = 99, so f_c =...)
6. ______________________________  (hint: With C = 1 uF that is R = 31.7 kohm (stock value 33 kohm, f_c = 4.82 H...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is f_c defined at -3 dB, and what does that mean for the size of the wave and for its power?

Answer: ______________________________________________


**B. Numerical.** A filter has R = 33 kohm and C = 1 uF. Find f_c, the dB removed from 50 Hz hum, the dB change of a 1 Hz signal and the phase at 1 Hz.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the Bode plot of the 100 Hz filter, read the gain at 1 kHz and at 10 kHz. What does the difference tell you about the slope?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a sensor signal lives between 0 and 2 Hz and must not lose more than 1 dB anywhere in that band. Choose a cutoff and a stock R (with C = 1 uF) that removes as much 50 Hz hum as possible. How many dB can you remove at most, and why can you not ask for 40 dB?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
