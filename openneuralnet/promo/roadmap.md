# Roadmap: the path to the openneuralnet Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Softmax and three classes

**You will learn:** How the output layer and the loss change when there are more than two classes (softmax and the multi-class cross-entropy).

**You will build:** A network with a softmax output trained on a three-arm spiral data set.

**Checkpoint (not met by the shipped code):** Test accuracy of at least 0.95 on a seeded three-arm spiral (the shipped network has a single sigmoid output and handles two classes only).

**Difficulty:** intermediate

## Session 5: Fight overfitting

**You will learn:** Weight decay and early stopping, and why they shrink the gap between training and test accuracy.

**You will build:** The same 100-hidden-neuron network on the 40 noisy points, with a regulariser.

**Checkpoint (not met by the shipped code):** A train-test accuracy gap of at most 0.08 on the 40-point task (the shipped code gives 1.00 train and 0.80 test, a gap of 0.20).

**Difficulty:** intermediate

## Session 6: Learn faster

**You will learn:** Learning-rate schedules and the role of the batch size.

**You will build:** A training loop with a decaying learning rate on the spiral data.

**Checkpoint (not met by the shipped code):** A training loss of 0.01 or below within 100 epochs on the two-spiral set (the shipped loop reaches 0.044 after 600 epochs).

**Difficulty:** advanced

## Session 7: Deep and stable

**You will learn:** Why normalisation keeps gradients alive in very deep networks.

**You will build:** A 20-hidden-layer sigmoid network with batch normalisation.

**Checkpoint (not met by the shipped code):** A first-layer to last-layer gradient-norm ratio of at least 1e-3 (the shipped 20-layer sigmoid network gives 2e-13).

**Difficulty:** advanced

## Session 8: Build the Target animation

**You will learn:** Taking snapshots during training and animating them.

**You will build:** A GIF with the decision boundary, the loss and accuracy curves and the hidden-layer view side by side.

**Checkpoint (not met by the shipped code):** A GIF of at most 3 MB with at least 40 frames whose last frame shows training accuracy of 0.97 or more.

**Difficulty:** advanced

## The final step

Combine the milestones: a network with a two-neuron bottleneck that learns two spirals, a decision boundary that morphs as it trains beside the loss curve and the hidden-layer view, and a gradient check that proves your backpropagation is right. If your result looks like the Target animation, open a pull request and tell us how you did it.
