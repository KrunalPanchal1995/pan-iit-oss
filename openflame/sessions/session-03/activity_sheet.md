# Activity sheet: openflame, Session 3: Test the whole measurement on a video you know

Name: ____________________   Date: ____________

**Objectives**

- Generate a noisy synthetic flame video with a known mean height and flicker.
- Extract the flame height automatically to a fraction of a pixel and recover the flicker with an error bar that you check against repeated experiments.
- Predict and observe aliasing when the frame rate is too low, and the threshold shift of the height.
- State when the method fails (low signal-to-noise) and which assumptions the error bar rests on.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A synthetic flame models a 0.30 m pool fire releasing 40 kW, seen by a camera with 13 mm per pixel at 30 frames per second for 8 s, with 2 px flicker amplitude at 2.74 Hz and camera noise 0.15. What mean height (in px) does Heskestad predict? What do the measurements give, and what error bar on the frequency does the formula promise for a residual height noise of 0.44 px?

1. ______________________________  (hint: Heskestad: 40^(2/5) = 4.3795, so H = 0.235 x 4.3795 - 1.02 x 0.30 = 1....)
2. ______________________________  (hint: In pixels: 722 mm / 13 mm per px = 55.5 px. This is the synthetic mean...)
3. ______________________________  (hint: The video has N = 30 x 8 = 240 frames. The pipeline gives a trace erro...)
4. ______________________________  (hint: Error bar by hand: eta = A^2 / (2 s^2) = 4 / (2 x 0.44^2) = 10.33; N(N...)
5. ______________________________  (hint: Result: f = 2.7399 +- 0.0013 Hz against the truth 2.74 Hz, within one ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does changing the threshold shift the measured height but hardly change the measured frequency?

Answer: ______________________________________________


**B. Numerical.** Use the threshold formula for threshold 0.3 and s_tip = 2 px. How far does the tip move, in px and in mm at 13 mm per px? Is that a large part of the 722 mm flame?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the aliasing spectra figure, the 15 fps spectrum of a 9 Hz flame peaks at 6 Hz. Explain the position of the peak, and say what you would change in the experiment to see 9 Hz.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you need the flicker frequency to better than 0.01 Hz. At 30 frames per second the flicker amplitude is 1 px and the extraction noise 0.5 px. How long must the recording be? What else would you check?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
