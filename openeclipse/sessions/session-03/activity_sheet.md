# Activity sheet: openeclipse, Session 3: Predicting eclipses and the Saros

Name: ____________________   Date: ____________

**Objectives**

- Build a small eclipse predictor from mean motions of the Sun and Moon plus a few large corrections.
- Validate the predictor against published eclipse times and gamma values and report its errors.
- Show that 223 synodic months, 242 draconic months and 239 anomalistic months are nearly equal, and explain the 18-year Saros shift.
- Produce an honest, labelled eclipse list for a three-year window and name the model's failure cases.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Predict the new moon of the total eclipse of 8 April 2024 and compare it with the published greatest-eclipse time of 18:17 UT.

1. ______________________________  (hint: The nearest new moon number is k = 300. Mean time: 2451550.09766 + 300...)
2. ______________________________  (hint: The seven correction terms add -12.4 minutes, giving 18:22 UT. The pub...)
3. ______________________________  (hint: The argument of latitude at that moment gives a distance from the node...)
4. ______________________________  (hint: The latitude series gives beta = 0.36 degrees and the Moon distance 35...)
5. ______________________________  (hint: The umbra is longer than the Moon distance, so the predicted type is t...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does using only the mean motion give an error of up to 12.7 hours in the time of new moon?

Answer: ______________________________________________


**B. Numerical.** Compute 223 synodic months and 242 draconic months in days with the stated mean periods. How far apart are they?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the Saros-series figure, how many degrees does the Moon move past the node per member, and about how many members does a series have inside the 16.7 degree limit?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you want to find an eclipse whose track returns to nearly the same longitude as an earlier one. Which multiple of the Saros should you use, how many years is it, and how close is the longitude?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
