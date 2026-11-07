# Activity sheet: openalias, Session 2: The alias formula and the Nyquist limit

Name: ____________________   Date: ____________

**Objectives**

- Sample a sine wave and show that two different frequencies give identical samples.
- Use f_alias = |f - k fs| with k = round(f / fs) and place the result in the range 0 to fs/2.
- State the Nyquist limit and the rule fs > 2 f_max.
- Solve a design problem: the minimum frame rate to measure a given wheel or fan speed.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 40 Hz sine is sampled at 50 Hz. Find the alias frequency, the signed alias, and check with one sample.

1. ______________________________  (hint: Nyquist frequency = 50 / 2 = 25 Hz. Since 40 Hz is above 25 Hz, aliasi...)
2. ______________________________  (hint: k = round(40 / 50) = round(0.8) = 1....)
3. ______________________________  (hint: Signed alias = 40 - 1 x 50 = -10 Hz, so the alias frequency is 10 Hz....)
4. ______________________________  (hint: Check with sample n = 1: x[1] = sin(2 pi x 40 / 50) = sin(2 pi x 0.8) ...)
5. ______________________________  (hint: A -10 Hz sine gives sin(2 pi x (-10) / 50) = sin(-72 degrees) = -0.951...)

Final answer: ____________________

## Questions
**A. Conceptual.** After a signal has been sampled, can any processing of the samples tell a 40 Hz sine from its 10 Hz alias at fs = 50 Hz? Why is the only real cure a change before sampling?

Answer: ______________________________________________


**B. Numerical.** A 130 Hz signal is sampled at 100 Hz. Find the alias frequency and give two other frequencies that give the same samples.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the folding graph for fs = 50 Hz, at which true frequencies from 0 to 150 Hz is the alias exactly 10 Hz?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a four-blade fan turns 12 rev/s. A phone can film at 30, 60, 100 or 120 frames per second. Which rates show the true speed and direction? What is the minimum, and what does a higher rate cost?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
