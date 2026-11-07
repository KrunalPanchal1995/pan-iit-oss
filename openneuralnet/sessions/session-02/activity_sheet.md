# Activity sheet: openneuralnet, Session 2: Gradient descent, the sigmoid and the XOR wall

Name: ____________________   Date: ____________

**Objectives**

- Explain why the perceptron rule stops after a finite number of updates on separable data, and verify it on seeded data.
- Use the sigmoid and its derivative s' = s (1 - s), and check the derivative numerically.
- Train logistic regression by gradient descent with the cross-entropy loss and check the gradient (p - y) x against finite differences.
- Show the effect of the learning rate (too small is slow, too large diverges) and prove by exhaustive search that no single line solves XOR.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
One example: input x = (2, -1) with label 0. Start with w = (0, 0), b = 0. Do one gradient descent step with learning rate 0.4 and check the loss falls.

1. ______________________________  (hint: Score z = 0, so p = s(0) = 0.5 and the loss is -ln(1 - 0.5) = 0.6931....)
2. ______________________________  (hint: Gradient: (p - y) x = 0.5 * (2, -1) = (1, -0.5) and (p - y) = 0.5 for ...)
3. ______________________________  (hint: Step: w = (0, 0) - 0.4 * (1, -0.5) = (-0.4, 0.2) and b = 0 - 0.4 * 0.5...)
4. ______________________________  (hint: New score z = (-0.4)*2 + 0.2*(-1) + (-0.2) = -1.2, so p = s(-1.2) = 0....)
5. ______________________________  (hint: New loss = -ln(1 - 0.2315) = 0.2633. The loss fell from 0.6931 to 0.26...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do we use the smooth sigmoid with cross-entropy loss for gradient descent, instead of the step 'fire if z > 0' of Session 1 with the count of wrong answers as the loss?

Answer: ______________________________________________


**B. Numerical.** For the single example x = (2, -1), label 0, starting from w = (0, 0), b = 0 with lr = 0.4: what are the gradient and the weights after one step? Check that the loss fell.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the learning-rate figure, lr = 100 reaches loss 0.2 around epoch 22 and yet ends at 0.699. What does that tell you about judging a learning rate?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: on the 100-point blob data (sep 3, seed 0) choose a learning rate and the smallest number of epochs that gets the loss to 0.2 or below and keeps it there up to epoch 100. Give a choice and a reason, and say what goes wrong with lr = 0.01 and lr = 100.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
