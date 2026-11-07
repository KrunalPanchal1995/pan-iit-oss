# Activity sheet: openclassifier, Session 2: Trees, neighbours and the confusion matrix

Name: ____________________   Date: ____________

**Objectives**

- Compute Gini impurity and find the best split of a node with a search written in NumPy.
- Build a small decision tree and a k-nearest-neighbour classifier and see how k and depth change the boundary.
- Fill a confusion matrix and compute accuracy, precision, recall and F1 from scratch.
- Use Bayes' rule to explain why a rare condition makes most positive results false, and choose a threshold for given costs.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A condition has prevalence 1 percent. The test has sensitivity 99 percent and specificity 95 percent. Of 10000 people tested, how many test positive, and what fraction of those truly have the condition?

1. ______________________________  (hint: Have the condition: 1 percent of 10000 = 100 people. The test finds 99...)
2. ______________________________  (hint: Do not have it: 9900 people. The test wrongly flags 5 percent of them:...)
3. ______________________________  (hint: Everyone who tests positive: 99 + 495 = 594 people....)
4. ______________________________  (hint: PPV = 99 / 594 = 0.1667, about 16.7 percent. By Bayes: 0.01 x 0.99 / (...)
5. ______________________________  (hint: The overall accuracy is (99 + 9405) / 10000 = 95.04 percent, yet five ...)

Final answer: ____________________

## Questions
**A. Conceptual.** A friend says: 'The test is 95 percent accurate, so a positive result means a 95 percent chance of having the condition.' What is wrong with this?

Answer: ______________________________________________


**B. Numerical.** A classifier produces TP = 40, FP = 10, FN = 20 and TN = 130 on 200 cases. Compute accuracy, precision, recall and F1.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the PPV graph at prevalence 1 percent, what PPV do specificities of 90, 95 and 99 percent give (sensitivity 99 percent)? At what prevalence does a 95 percent specificity reach a PPV above 80 percent?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a miss costs 10 units and a false alarm costs 1 unit. You have a classifier that gives scores between 0 and 1. Why should the threshold be below 0.5, how low would the theory put it if the scores were true probabilities, and how should you choose it in practice?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
