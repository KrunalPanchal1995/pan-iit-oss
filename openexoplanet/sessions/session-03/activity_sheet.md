# Activity sheet: openexoplanet, Session 3: Find the planet in a noisy light curve

Name: ____________________   Date: ____________

**Objectives**

- Remove slow stellar variability with a moving median and show that a window that is too short erases the transits.
- Implement Box Least Squares (BLS) and recover an injected period, identifying the aliases at P/2 and 2P.
- Use the odd-even check to separate a planet from an eclipsing binary.
- Measure the false-alarm rate of the search on pure noise, and recognise two failure cases.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Use the mini-project light curve (star of assumed radius 0.9 solar radii, 50 days). Find the first planet and report its period, depth, radius ratio and radius in Earth radii, with the odd-even check.

1. ______________________________  (hint: Detrend with a 1.0 day moving median, then run BLS and refine: the str...)
2. ______________________________  (hint: The box depth is 2311 ppm (0.002311)....)
3. ______________________________  (hint: Radius ratio: k = sqrt(0.002311) = 0.0481....)
4. ______________________________  (hint: Radius: 0.0481 x 0.9 x 695700 / 6371 = 4.73, so about 4.7 Earth radii ...)
5. ______________________________  (hint: Odd-even: the depths of odd and even transits differ by only 0.5 sigma...)
6. ______________________________  (hint: Mask the transits and search again: the second planet appears at P = 2...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can BLS not tell the difference between period P and period 2P if every second transit falls in a data gap? What would you need to resolve it?

Answer: ______________________________________________


**B. Numerical.** A candidate has depth 0.0025 around a star of radius 0.9 solar radii. Find the planet radius in Earth radii.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the periodogram of the 4.2 day planet, which peaks are at about 2.1 and 8.4 days, and how do their heights compare with the main peak? Why are they lower?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the transit lasts 0.12 days and the star's brightness varies with a period of 7.3 days. Choose a moving-median window and say what limits it on each side. Then say which SNR threshold you would adopt for a search like the one in the lesson and why.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
