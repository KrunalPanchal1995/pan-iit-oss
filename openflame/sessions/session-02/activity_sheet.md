# Activity sheet: openflame, Session 2: How fast does it flicker? Sampling and the FFT

Name: ____________________   Date: ____________

**Objectives**

- Find a flicker frequency by counting cycles and by the FFT of a height signal.
- State the resolution (1/T) and the Nyquist limit (fs/2) of a recording and compute an aliased frequency.
- Use the Heskestad flame-height and puffing-frequency correlations with correct units and state where they are valid.
- Choose a frame rate and recording length for a measurement.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 0.30 m diameter pool fire releases 50 kW. Estimate the mean flame height and the puffing frequency. You film 10 s at 30 frames per second: how many frames, what resolution and what Nyquist limit? Is the flicker seen correctly?

1. ______________________________  (hint: Heskestad: 50^(2/5) = 4.7818, so 0.235 x 4.7818 = 1.1237 m....)
2. ______________________________  (hint: Subtract 1.02 x 0.30 = 0.3060 m, so H = 0.8177 m = 0.818 m....)
3. ______________________________  (hint: Puffing frequency: f = 1.5 / sqrt(0.30) = 1.5 / 0.5477 = 2.74 Hz....)
4. ______________________________  (hint: Recording: N = 30 x 10 = 300 frames, resolution = 1/10 = 0.1 Hz, Nyqui...)
5. ______________________________  (hint: 2.74 Hz is far below 15 Hz, so it is seen correctly and the FFT peak s...)

Final answer: ____________________

## Questions
**A. Conceptual.** A friend films a flame at 24 frames per second and sees a flicker at 9 Hz. Can she conclude the true flicker is 9 Hz?

Answer: ______________________________________________


**B. Numerical.** A 0.05 m diameter burner puffs at about 1.5/sqrt(D). Calculate that frequency. At what frequency would a camera at 10 frames per second report it, and how does that compare with the Nyquist limit?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the aliasing map, what does a 24 frames per second camera report for a true 20 Hz flicker? Why does the curve return to 0 at 24 Hz?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you want to measure the puffing frequency of pool fires with diameters from 0.1 m to 1 m to a resolution of 0.05 Hz. Choose a frame rate and a recording length and justify them.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
