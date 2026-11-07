# Activity sheet: openalias, Session 4: Noise-proof recovery of the true speed

Name: ____________________   Date: ____________

**Objectives**

- Say where the noise of a measured apparent speed comes from, and how it falls as the clip gets longer.
- Explain why demanding an exact match between the two ladders fails once the measurements are noisy.
- Recover the most likely true speed from two noisy apparent speeds by choosing the best pair of rungs, and report an uncertainty.
- Check the recovery with 2000 simulated trials against the roadmap line, and against the theoretical limit no rule can beat.
- Explain how the choice of the two frame rates trades the unambiguous range against the noise the pair can survive.

## Before you start: predict
In your own words, what do you think happens to the share of correct answers when the noise on the apparent speeds doubles?

______________________________________________________________

## Worked example (fill in as you go)
Rates 30 and 24 fps, sigma = 0.3 rev/s, expected range 5 to 59 rev/s. The measured apparent speeds are a1 = -7.2 and a2 = -1.8 rev/s. Recover the speed with an uncertainty.

1. ______________________________  (hint: the rungs of clip 1 are -7.2 + 30 k: 22.8 and 52.8; of clip 2, -1.8 + 24 m: 22.2 and 46.2.)
2. ______________________________  (hint: the gaps are 0.6, 6.6, 23.4 and 30.6; the Session 3 rule needs 0.3 or less and gives no answer.)
3. ______________________________  (hint: middle = (22.8 + 22.2) / 2 = 22.5; sd = 0.3 / sqrt(2) = 0.21; margin = (6.6 - 0.6) / 0.424 = 14.1.)

Final answer: ____________________  (22.5 +- 0.21 rev/s)

## Questions
**A. Conceptual.** The measurements are good to 0.3 rev/s and the Session 3 rule asks for a match within 0.3 rev/s. Why does it still fail about half of the time?

Answer: ______________________________________________


**B. Numerical.** Rates 30 and 25 fps, sigma = 0.4 rev/s, expected range 5 to 59 rev/s. The measured apparent speeds are a1 = 4.3 and a2 = 8.8 rev/s. List the pairs of rungs with the smallest gaps, give the recovered speed with its uncertainty and the margin, and say what the Session 3 rule (tolerance 0.3) does.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the bottom left panel, at sigma = 0.7 the best pair is right in 68.5 percent of the trials, about the same as the dotted limit, while the Session 3 rule is right in 16 percent. What does this tell you about the remaining 31 percent of failures?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a marker is found with an error of 0.1 rad in each frame of a clip filmed at 30 fps. How many frames does a clip need so that the recovery is within 0.5 rev/s in at least 95 percent of the trials, and in at least 99 percent? (Take the same noise for the 24 fps clip; it is a little less, 0.8 times.)

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happens: ____________________
