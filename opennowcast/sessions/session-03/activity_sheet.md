# Activity sheet: opennowcast, Session 3: When one shift is not enough: local motion, growth, uncertainty

Name: ____________________   Date: ____________

**Objectives**

- Estimate local motion by block matching and show that a global vector fails when two regions move differently.
- Measure how forecast skill falls with lead time, and why growth and decay break pure advection.
- Compare 12 small interpolated shifts with one 60-minute shift and explain the numerical diffusion.
- Turn motion uncertainty into a probability with a seeded ensemble and check its reliability.
- Recognise where advection fails: new storms and rotating patterns.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A cell of width sigma = 2.5 pixels moves 8.4 pixels east in 60 minutes (0.7 pixels per 5 minutes). Compare the blur from 12 separate 0.7 pixel shifts with one 8.4 pixel shift.

1. ______________________________  (hint: One 0.7 pixel shift has fractional part f = 0.7 and adds f(1 - f) = 0....)
2. ______________________________  (hint: Twelve of them add 12 x 0.21 = 2.52 pixels squared....)
3. ______________________________  (hint: One shift of 8.4 pixels has fractional part 0.4 and adds 0.4 x 0.6 = 0...)
4. ______________________________  (hint: The cell starts with variance 6.25 pixels squared, so the 12-step cell...)
5. ______________________________  (hint: Both conserve the total rain exactly; only the shape differs. The chec...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can advection never forecast a storm that starts after the forecast time? And why does a rotating pattern break a single-vector forecast?

Answer: ______________________________________________


**B. Numerical.** A cell is moved in 12 steps of 0.5 pixels. How much blur (in pixels squared) is added in total? How much would one shift of 6 pixels add?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the growth and decay panel of the skill curves, at what lead time does each method fall below CSI 0.5 (10 mm/h)? What does that mean for a user?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you must publish a 60-minute forecast for a field with two regions that move differently and cells that grow and fade. Choose the motion method and the longest lead time you would show as a single picture, and say what you would show beyond that.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
