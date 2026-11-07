# Activity sheet: openalias, Session 5: A third clip: a wider range and less noise

Name: ____________________   Date: ____________

**Objectives**

- Find the speeds that sit on all three ladders, and show that 30, 24 and 25 fps leave only 22.5 rev/s below 400 rev/s, where two clips leave four candidates.
- Explain why the unambiguous range is the least common multiple of all the frame rates, and say exactly when a third rate adds nothing.
- Choose a third frame rate for a required range, and notice when a rate that helps is still not enough.
- Recover the speed from three noisy clips with an uncertainty, and show that the third clip also lowers the noise by sqrt(2/3).
- Check all of this with an exhaustive search and with simulated trials.

## Before you start: predict
In your own words, what do you think happens to the speeds that fit all the clips when you add a third clip at 25 fps to the clips at 30 and 24 fps?

______________________________________________________________

## Worked example (fill in as you go)
A fan is filmed at 30, 24 and 25 fps. The apparent speeds are -7.5, -1.5 and -2.5 rev/s. Which speeds below 400 rev/s fit, with two clips and with three?

1. ______________________________  (hint: clip 1 allows -7.5 + 30 k, clip 2 allows -1.5 + 24 m; on both: 22.5, 142.5, 262.5, 382.5.)
2. ______________________________  (hint: clip 3 allows -2.5 + 25 j; 142.5 + 2.5 = 145 is not a multiple of 25; neither are 265 and 385.)
3. ______________________________  (hint: the next shared speed is 22.5 + lcm(30, 24, 25) = 622.5.)

Final answer: ____________________  (two clips: 22.5, 142.5, 262.5, 382.5; three clips: only 22.5, unique up to 600 rev/s)

## Questions
**A. Conceptual.** With 30 and 24 fps, a speed 120 rev/s above the true one fools both clips. Why does it no longer fool a third clip at 25 fps?

Answer: ______________________________________________


**B. Numerical.** The first two rates are 30 and 24 fps. For third rates of 20, 25, 36 and 40 fps give the range of the three rates, and say which make a fan of up to 400 rev/s recoverable.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the top right panel the bars at 36, 45 and 48 fps are green (they help) but lie below the dashed 400 rev/s line. What does that mean for a fan of 380 rev/s filmed with 30, 24 and 45 fps?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you have clips at 30 and 24 fps and must measure fans up to 400 rev/s with noise 0.3 rev/s. Which third frame rates in 20 to 60 fps work, which one would you choose, and what share of trials will be within 0.5 rev/s?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happens: ____________________
