# Activity sheet: openalias, Session 3: Simulate, find the folded peak, recover the true speed

Name: ____________________   Date: ____________

**Objectives**

- Generate sampled signals and rendered marker clips in code, with optional jitter and exposure blur.
- Find the folded peak with the FFT and validate it against the exact folding formula.
- Recover the true frequency from two frame rates and state when the answer is unique.
- Measure how timing jitter and shutter exposure change what is seen, and compare with the formulas.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The 30 fps clip shows the marker at -7.5 rev/s and the 24 fps clip shows it at -1.5 rev/s. The fan turns at less than 60 rev/s. Find its true speed and say how sure you are.

1. ______________________________  (hint: Clip 1 allows f = -7.5 + 30 k: ..., -7.5, 22.5, 52.5, 82.5, ......)
2. ______________________________  (hint: Clip 2 allows f = -1.5 + 24 m: ..., -1.5, 22.5, 46.5, 70.5, ......)
3. ______________________________  (hint: Values in both lists below 60: only 22.5 (k = 1 and m = 1). Check: -7....)
4. ______________________________  (hint: Next common value: 22.5 + lcm(30, 24) = 22.5 + 120 = 142.5, far above ...)
5. ______________________________  (hint: In rpm: 22.5 x 60 = 1350 rpm. Also check the simulation: sampled at 30...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a long exposure act as an anti-alias filter, and why can this not be repaired after the video is recorded?

Answer: ______________________________________________


**B. Numerical.** A frame clock has 1 millisecond of random timing jitter. By what factor does the peak of a 40 Hz signal shrink? Do the same for a 400 Hz signal. Which signal suffers more and why?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the spectrum figure the FFT of the 22.5 Hz signal sampled at 30 Hz peaks at 7.5 Hz. Name four other true frequencies that would give a peak at the same place.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the first camera runs at 30 fps and fan speeds up to 100 rev/s must be recovered uniquely from signed measurements. Which second frame rate would you choose from 15, 20, 24, 25 and 60? Justify the choice.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
