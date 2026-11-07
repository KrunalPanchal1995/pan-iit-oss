# Activity sheet: openpinn, Session 2: Train a tiny network on a differential equation

Name: ____________________   Date: ____________

**Objectives**

- Write a one-hidden-layer tanh network and its slope, and derive its gradients by hand (backpropagation).
- Verify the hand gradients against finite differences and train with Adam written in numpy.
- Build a physics-informed loss for u' = -u, u(0) = 1 from a residual term and a boundary term.
- Study how many collocation points are needed, and read the residual between the points.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A trial solution u = exp(-0.8 x) is tested at the three collocation points x = 0, 1, 2. Compute the loss of Section B and compare with the exact solution; then read the error table for N collocation points.

1. ______________________________  (hint: u = exp(-0.8 x) has slope -0.8 exp(-0.8 x), so the residual is u' + u ...)
2. ______________________________  (hint: At x = 0, 1, 2 the residuals are 0.2, 0.2 exp(-0.8) = 0.0899 and 0.2 e...)
3. ______________________________  (hint: Mean of the squares = (0.04 + 0.00808 + 0.00163) / 3 = 0.01657. The bo...)
4. ______________________________  (hint: For the exact solution exp(-x) every residual is 0 and the loss is 0....)
5. ______________________________  (hint: Training the network (10 units) for several N gives the largest error ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the loss need the boundary term (u(0) - 1)^2? What would the network do without it?

Answer: ______________________________________________


**B. Numerical.** For a single unit u = tanh(x) (c = 1, a = 1, d = 0, e = 0), compute the residual u' + u at x = 0.5.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the error-against-N plot, what is the smallest N tested that brings the largest error below 0.01, and what happens at N = 2?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you can afford at most 8 collocation points (each costs a training evaluation) but need the largest error below 0.01 on 0 to 2. Is that possible, and what would you change if a colleague wanted 0.001?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
