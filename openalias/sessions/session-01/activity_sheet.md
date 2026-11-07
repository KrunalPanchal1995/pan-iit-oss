# Activity sheet: openalias, Session 1: A wheel on camera: slow, frozen or backwards

Name: ____________________   Date: ____________

**Objectives**

- Explain why a camera that takes pictures at fixed instants can show a wheel turning slowly, backwards or not at all.
- Compute the turn between two frames and the apparent speed of a marker, by hand and in Python.
- Read a graph of apparent speed against true speed (a sawtooth).
- Predict which frame rates make a given wheel look frozen.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A wheel turns 28 rev/s and is filmed at 30 frames per second. How far does the marker turn between frames, what does the viewer see, and how fast does the wheel seem to go?

1. ______________________________  (hint: Turn between frames: step = 360 x 28 / 30 = 336 degrees....)
2. ______________________________  (hint: The viewer sees the shortest way: 336 degrees is the same place as 336...)
3. ______________________________  (hint: Apparent speed = -24 / 360 x 30 = -2 rev/s....)
4. ______________________________  (hint: Check with f - k fs: k = round(28 / 30) = 1, so 28 - 30 = -2 rev/s. Th...)

Final answer: ____________________

## Questions
**A. Conceptual.** A wheel turns slightly slower than fs rev/s (for example 29 rev/s at 30 fps). Why does it seem to turn slowly backwards, and not forward?

Answer: ______________________________________________


**B. Numerical.** A wheel turns 33 rev/s and is filmed at 24 frames per second. Find the turn per frame, the apparent turn and the apparent speed. Do a sanity check.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** Using the sawtooth graph for 30 frames per second, for which true speeds between 0 and 60 rev/s does the wheel seem to go backwards, and where does it seem frozen?

Answer: ______________________________________________


**D. Design and optimisation challenge.** A wheel turns 29 rev/s. You may film with 24, 25, 28, 29, 30 or 60 frames per second. Which choice shows it turning slowly forward at no more than 1 rev/s? Which choice shows its true speed? What does the true-speed choice cost?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
