# Activity sheet: openexperiment, Session 2: Calibrating a sensor: a line, its uncertainty, and how many readings

Name: ____________________   Date: ____________

**Objectives**

- Fit a calibration line by least squares and report slope and intercept with standard errors.
- Invert the calibration line to turn a reading into a true value with an uncertainty.
- Compute the step size and quantisation noise of an N-bit ADC.
- Show by simulation that averaging reduces random error as 1 / sqrt(N) but leaves bias.
- Find how many repeat readings give a target uncertainty at 95 percent.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A calibration with 11 points (0 to 100 degrees C) gave slope 1.02, intercept -0.80 degrees C and s = 0.30 degrees C. The sensor now reads 30.4 degrees C. (a) What is the true temperature and its standard uncertainty? (b) How much better is the average of 4 readings? (c) How many readings are needed to know a mean to +-0.1 degrees C at 95 percent when the scatter is 0.30?

1. ______________________________  (hint: x0 = (30.4 - (-0.80)) / 1.02 = 31.2 / 1.02 = 30.59 degrees C....)
2. ______________________________  (hint: Sxx = 11000, xbar = 50, so (x0 - xbar)^2 / Sxx = (30.59 - 50)^2 / 1100...)
3. ______________________________  (hint: k = 1: u = (0.30 / 1.02) sqrt(1 + 1/11 + 0.0343) = 0.2941 * 1.061 = 0....)
4. ______________________________  (hint: k = 4: u = 0.2941 * sqrt(0.25 + 0.0909 + 0.0343) = 0.2941 * 0.6126 = 0...)
5. ______________________________  (hint: Readings needed: N >= (1.96 * 0.30 / 0.1)^2 = 5.88^2 = 34.57, rounded ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is the uncertainty of the inverted temperature smallest in the middle of the calibrated range and larger near the ends? Why can you not reduce it to zero by averaging the new readings?

Answer: ______________________________________________


**B. Numerical.** A sensor has scatter sd = 1.0 degrees C. How many readings must be averaged to know the mean to +-0.2 degrees C at 95 percent, and how many for +-0.1?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the average-versus-bias figure the scatter line falls with slope -1/2 on log axes while the bias line is flat. What does each tell you, and which could you reduce by taking more readings?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a 10-bit ADC over 0 to 100 degrees C is available. Its sensor noise sd is 0.30 degrees C. Is the quantisation noise a problem compared with the sensor noise? Would an 8-bit ADC be acceptable? Justify with numbers.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
