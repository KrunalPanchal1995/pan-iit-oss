# Activity sheet: opensymbolic, Session 2: A formula is a tree: simple versus accurate

Name: ____________________   Date: ____________

**Objectives**

- Represent a formula as an expression tree and evaluate it with numpy.
- Count the complexity of a formula as its number of nodes.
- Compute the error of three candidates on Kepler's third law data and place them on a complexity-versus-error plot.
- Use a held-out set to detect a formula that fits the training data by overfitting.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Build the tree for T = c sqrt(a a a) with c = 1 and use it to predict the period of Mars (a = 1.524 AU). Count its complexity.

1. ______________________________  (hint: The tree is mul(c, sqrt(mul(a, mul(a, a)))). Its nodes are mul, c, sqr...)
2. ______________________________  (hint: Evaluate from the leaves: a * a * a = 1.524^3 = 3.540....)
3. ______________________________  (hint: Take the square root: sqrt(3.540) = 1.8814, and multiply by c = 1....)
4. ______________________________  (hint: The observed period of Mars is 1.881 years, so the prediction matches ...)
5. ______________________________  (hint: With the fitted constant (0.9999) the same tree predicts 11.867 years ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is it not enough to choose the formula with the smallest training error?

Answer: ______________________________________________


**B. Numerical.** Draw the tree for x^2 - 2 using sq, sub and a number node. Count the nodes and evaluate it at x = 3.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the complexity-versus-error plot, which candidate has the lowest training error and which the lowest held-out error? What does that tell you?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: use the rule 'accept a formula only if its held-out error is below 0.01 years squared, and then choose the one with the fewest nodes'. Which candidate is chosen? What changes if Jupiter is moved into the training set?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
