# Activity sheet: opensurvey, Session 3: Close, adjust and test a traverse

Name: ____________________   Date: ____________

**Objectives**

- Compute the misclosure of a closed traverse and judge it by the relative accuracy and the angle check.
- Apply and verify the Bowditch rule, and find the area by the coordinate (shoelace) method.
- Propagate typical angle and distance errors by seeded Monte Carlo and check the result against a first-order prediction and the exact polygon.
- Recognise a blunder that adjustment hides, and locate it.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A traverse of perimeter 673.238 m has a misclosure vector (eE, eN) = (+0.100, -0.060) m. Find the misclosure, the relative accuracy, and the Bowditch correction for the 200 m leg. Is 1 in 5000 met?

1. ______________________________  (hint: Misclosure = sqrt(0.100^2 + 0.060^2) = 0.1166 m....)
2. ______________________________  (hint: Relative accuracy = 673.238 / 0.1166 = 5773, so 1 in 5773....)
3. ______________________________  (hint: The 200 m leg gets cE = -0.100 x 200 / 673.238 = -0.0297 m and cN = +0...)
4. ______________________________  (hint: 1 in 5773 is better than 1 in 5000, so the traverse is acceptable and ...)
5. ______________________________  (hint: The five corrections for all legs sum to (-0.100, +0.060), the opposit...)
6. ______________________________  (hint: Area check on the exact plot (rectangle 200 m x 120 m plus a gable of ...)

Final answer: ____________________

## Questions
**A. Conceptual.** The Bowditch rule always makes a traverse close exactly. Does a perfect closure after adjustment prove that the survey is correct? Give an example from this session.

Answer: ______________________________________________


**B. Numerical.** A traverse of 673.238 m perimeter closes with a misclosure of 0.050 m. What is the relative accuracy? How much is a leg of 116.619 m corrected?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** Read the sensitivity graph: roughly how large can the angle error become before the typical misclosure exceeds the 1 in 5000 limit? What does the straight rise tell you about the effect of a better instrument?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose the poorest angle standard deviation (in arc-seconds) so that about 95 percent of surveys of this plot meet 1 in 5000. Hint: require the RMS misclosure to be at most half the limit. Why half, and what is the trade-off?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
