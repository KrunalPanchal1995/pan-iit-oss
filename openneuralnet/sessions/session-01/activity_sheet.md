# Activity sheet: openneuralnet, Session 1: A neuron, a line and a nudge

Name: ____________________   Date: ____________

**Objectives**

- Explain machine learning as finding the settings of a rule from examples instead of typing the rule.
- Compute what one neuron does: a weighted sum of the inputs plus a bias, then fire if it is above zero.
- Show that a neuron draws a straight line between two groups of points.
- Apply the perceptron rule by hand and see the line move until it splits the groups.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Start with w = (1, -2), b = 0 and apply the perceptron rule, visiting the points in the order of the table, until every point is right.

1. ______________________________  (hint: Point 1 is (2, 2.5) with label 1. Its sum is z = 1*2 + (-2)*2.5 + 0 = ...)
2. ______________________________  (hint: Nudge 1: output 0, label 1, so w = (1, -2) + (1 - 0)*(2, 2.5) = (3, 0....)
3. ______________________________  (hint: Points 2 to 7 are right. Point 8 is (0.5, -0.5) with label 0 but z = 3...)
4. ______________________________  (hint: Nudge 2: output 1, label 0, so w = (3, 0.5) - (0.5, -0.5) = (2.5, 1) a...)
5. ______________________________  (hint: In the next pass point 8 gives nudge 3: w = (2.5, 1) - (0.5, -0.5) = (...)

Final answer: ____________________

## Questions
**A. Conceptual.** What is the difference between a traditional program and a machine learning model, and why does the neuron need a bias b in addition to the weights?

Answer: ______________________________________________


**B. Numerical.** The learned neuron has w = (2, 1.5) and b = -1. What are z and the output for the new point (-0.5, -1.5)? Is that correct if this point is from group B?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the 'points right versus bias' graph with w = (1, 1), over which range of b are all 10 points right, and why does the curve have flat steps?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: keep w = (1, 1) and pick a bias that classifies all ten points correctly while staying as far as possible from both groups. Which b, and why?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
