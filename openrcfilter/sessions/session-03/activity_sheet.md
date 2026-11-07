# Activity sheet: openrcfilter, Session 3: Digital filters: the exponential moving average, Butterworth and the limits

Name: ____________________   Date: ____________

**Objectives**

- Implement the digital first-order filter y[n] = y[n-1] + alpha (x[n] - y[n-1]) and choose alpha from tau and the sample time.
- Measure its frequency response with sine sweeps and with an FFT, and compare it with the analog Bode curve.
- Verify the noise-reduction formula alpha / (2 - alpha) numerically and quantify the lag it costs.
- Build a second-order Butterworth biquad, check its -3 dB point, and explain two failure cases: aliasing and a cutoff above Nyquist.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The temperature sensor is sampled at 500 Hz with an EMA of cutoff 2 Hz. Find alpha, the noise left (from 0.05 C rms), the lag, and the hum left (from 0.5 C of 50 Hz). Does it meet the limit of 0.02 C of hum? If not, try 1.5 Hz.

1. ______________________________  (hint: alpha = 1 - exp(-2 pi * 2 / 500) = 1 - exp(-0.02513) = 0.02482....)
2. ______________________________  (hint: Noise power factor = alpha / (2 - alpha) = 0.02482 / 1.97518 = 0.01257...)
3. ______________________________  (hint: Lag = (1 - alpha) / alpha = 39.3 samples = 39.3 / 500 = 78.6 ms....)
4. ______________________________  (hint: Hum: the digital gain at 50 Hz is 0.0406, so 0.5 C of hum becomes 0.02...)
5. ______________________________  (hint: Try 1.5 Hz: alpha = 0.0187, hum left 0.0152 C (passes), rms noise 0.00...)

Final answer: ____________________

## Questions
**A. Conceptual.** The exact discretisation makes the digital step response equal the analog one at every sample. Why does the digital Bode curve still differ from the analog curve near Nyquist?

Answer: ______________________________________________


**B. Numerical.** An EMA with fc = 5 Hz is run at fs = 200 Hz. Find alpha, the noise power factor (also in dB), the lag in samples and in milliseconds, and the number of samples to reach 90 percent of a step.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the noise-versus-lag graph, how many samples of lag are needed to cut the white-noise power by 10 dB? What does the trade-off say about halving the noise power again?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: your microcontroller can only sample at 60 Hz, the signal band is below 1 Hz and 50 Hz hum is present. Why can a digital EMA with fc = 2 Hz not fix the hum, and what do you add? Give the hum removed and the loss of the 1 Hz signal for your solution.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
