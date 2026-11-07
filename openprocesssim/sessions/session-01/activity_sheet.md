# Activity sheet: openprocesssim, Session 1: Boxes, pipes and a loop: solve the rules together

Name: ____________________   Date: ____________

**Objectives**

- Describe a plant as boxes joined by pipes, where each box has inlets, outlets and a rule.
- Write each box rule as one equation and solve all equations together with a matrix.
- Solve the same loop by guessing the recycle and going round (successive substitution).
- Explain why a bigger recycle fraction needs a much bigger separator.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A plant has a fresh feed F = 100 mol/s and a recycle fraction r = 0.6. Find S, R and P, and show the first three rounds of the guess-and-go-round method starting from R = 0.

1. ______________________________  (hint: Mixer: S = F + R. Separator: R = 0.6 S and P = 0.4 S....)
2. ______________________________  (hint: Substitute: S = 100 + 0.6 S, so 0.4 S = 100 and S = 250 mol/s....)
3. ______________________________  (hint: Then R = 0.6 * 250 = 150 mol/s and P = 0.4 * 250 = 100 mol/s. Check: t...)
4. ______________________________  (hint: Go round: guess R = 0, then S = 100 and the new R = 60. Next S = 160 a...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is the product flow equal to the fresh feed even though the separator handles much more?

Answer: ______________________________________________


**B. Numerical.** Find S, R and P for F = 100 mol/s and r = 0.75.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the left figure, what does the separator handle per unit feed at r = 0.8 and at r = 0.95, and what does that mean for equipment size?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the separator can pass at most 400 mol/s. What is the largest recycle fraction at a feed of 100 mol/s, and what happens if the feed is raised to 150 mol/s? What would you trade away?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
