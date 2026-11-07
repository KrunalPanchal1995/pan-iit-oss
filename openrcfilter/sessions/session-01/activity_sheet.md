# Activity sheet: openrcfilter, Session 1: A resistor and a capacitor smooth a noisy signal

Name: ____________________   Date: ____________

**Objectives**

- Describe a sensor signal as a slow part you want plus a fast part you do not.
- Explain how a resistor and a capacitor form a low-pass filter, and what the time constant tau = R C means.
- Measure how much of the slow signal and of the jitter survive a filter, and how late the output arrives.
- Read a graph of fraction kept against time constant and see the trade-off.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A filter has R = 10 kohm and C = 3.2 uF. Find tau and f_c, how much of the 2 Hz signal and of the 40 Hz jitter get through, and how late the slow wave is.

1. ______________________________  (hint: tau = R C = 10 000 ohm * 0.0000032 F = 0.032 s = 32 ms....)
2. ______________________________  (hint: f_c = 1 / (2 pi * 0.032) = 4.97 Hz....)
3. ______________________________  (hint: Slow wave (2 Hz): f / f_c = 0.402, gain = 1 / sqrt(1 + 0.162) = 0.928,...)
4. ______________________________  (hint: Jitter (40 Hz): f / f_c = 8.04, gain = 1 / sqrt(1 + 64.7) = 0.123, so ...)
5. ______________________________  (hint: Delay of the slow wave = atan(2 / 4.97) / (2 pi * 2) = 0.3826 rad / 12...)
6. ______________________________  (hint: The simulation in lesson.py measures 0.928, 0.123 and 30.3 ms: the num...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does an RC filter flatten fast jitter more than a slow wave? And why can it never remove the jitter without making the slow signal arrive late?

Answer: ______________________________________________


**B. Numerical.** R = 20 kohm and C = 1 uF. Find tau, f_c, the fraction of the 2 Hz signal and of the 40 Hz jitter that is kept, and the delay of the slow wave.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** Look at the figure of fraction kept against time constant. Could any single time constant keep at least 90 percent of the slow signal and at the same time let through less than 10 percent of the jitter?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with C = 1 uF, choose a stock resistor so that at least 90 percent of the slow signal is kept and less than 20 percent of the jitter gets through. How late is the output?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
