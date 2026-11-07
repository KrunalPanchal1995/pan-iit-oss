# Activity sheet: openneuralnet, Session 3: Backpropagation: train a two-layer network

Name: ____________________   Date: ____________

**Objectives**

- Derive and code the forward pass and backpropagation (dL/dW2 and dL/dW1) of a two-layer network in numpy.
- Verify every gradient against finite differences with a relative error below 1e-6.
- Train on XOR and a seeded spiral data set to high test accuracy, and write minibatch SGD with momentum and Adam.
- Measure overfitting, the effect of initialisation, a learning rate that is too high and vanishing gradients.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 2-2-1 tanh network has W1 = [[0.5, -0.3], [0.2, 0.4]], b1 = (0, 0), W2 = (0.6, -0.4)^T, b2 = 0. For the one example x = (1, 0) with label y = 1 compute the forward pass, the loss and the gradients dL/dW2 and dL/dW1 by hand.

1. ______________________________  (hint: Layer 1: Z1 = x W1 = (0.5, -0.3). H = tanh Z1 = (0.4621, -0.2913)....)
2. ______________________________  (hint: Layer 2: Z2 = 0.6*0.4621 + (-0.4)*(-0.2913) = 0.3938, P = sigmoid(0.39...)
3. ______________________________  (hint: Output error (N = 1): dZ2 = P - y = -0.4028. So dL/dW2 = H^T dZ2 = (-0...)
4. ______________________________  (hint: Pass back: dH = dZ2 W2^T = (-0.2417, 0.1611). The tanh slopes are 1 - ...)
5. ______________________________  (hint: dL/dW1 = x^T dZ1: the first row is (-0.1901, 0.1474) and the second ro...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the gradient check use two-sided differences and a relative error, and what does it tell you if the error is 1e-2 instead of 1e-9?

Answer: ______________________________________________


**B. Numerical.** An output neuron gives P = 0.8 for a point with label 1 and the hidden activations are H = (0.5, -0.5), with N = 1. Find dZ2, dL/dW2 and the loss.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the gradient-norm figure, what is the ratio of the first-layer to the last-layer gradient norm for a 10-layer sigmoid network, and for tanh and ReLU? What does it say about training the first layers?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design (mini-project): on the two-moons data (400 points, noise 0.25, seed 11, 25 percent test) choose the smallest number of hidden neurons among 2, 4, 16 that reaches 0.92 test accuracy, and say what is lost by making the network larger than needed.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
