# Activity sheet: openclassifier, Session 1: A rule that splits two groups

Name: ____________________   Date: ____________

**Objectives**

- Explain a classifier as a rule that turns measurements into a yes/no decision.
- Draw and move a straight decision boundary between two clusters.
- Count the two kinds of mistake, false alarms and misses, for a rule.
- Read a graph that shows how sliding the boundary trades one mistake for the other.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Twelve fruit: unripe (2, 2), (3, 4), (4, 2), (3.5, 6), (5, 3), (6, 4.5) and ripe (4.5, 7), (6, 8), (7, 6), (8, 9), (7.5, 4), (5.5, 5.5). Use the line with a = 45 degrees and c = 7. Which fruit are misclassified, and what is the accuracy?

1. ______________________________  (hint: At 45 degrees cos = sin = 0.7071, so the rule is 0.7071 (x + y) > 7, t...)
2. ______________________________  (hint: Sums x + y for the unripe fruit: 4, 7, 6, 9.5, 8, 10.5. Only 10.5 (the...)
3. ______________________________  (hint: Sums for the ripe fruit: 11.5, 14, 13, 17, 11.5, 11. All are above 9.8...)
4. ______________________________  (hint: Correct = 12 - 1 - 0 = 11, so accuracy = 11 / 12 = 0.917....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do we count false alarms and misses separately instead of just counting 'mistakes'? Give an example where one is worse than the other.

Answer: ______________________________________________


**B. Numerical.** For the twelve fruit of the worked example, use the size-only rule 'ripe if size > 5' (that is a = 0 degrees, c = 5). Count the false alarms, the misses and the accuracy.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the trade-off graph for 200 random fruit with the 45 degree boundary, what happens to the two counts as the offset c increases from 2 to 11? Where do they cross?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the shop says a false alarm (unripe fruit on the shelf) is worse than a miss. Should you move the boundary left or right of c = 6.7? What do you give up? How would you decide how far?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
