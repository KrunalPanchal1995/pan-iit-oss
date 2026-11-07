# Activity sheet: openlinkage, Session 3: A walking leg: simulate, validate and tune

Name: ____________________   Date: ____________

**Objectives**

- Simulate a full crank turn of a leg linkage and validate it with the loop-closure error and constant bar lengths.
- Compute the foot velocity by finite differences and by the analytic Jacobian, and compare; relate the speed ratio to mechanical advantage with a power balance.
- Measure stance straightness, stride, lift and dig, and see that a flat stance and a clear swing fight each other.
- Recognise a failure case (the crank locks at a dead centre) and tune a leg against a requirement list.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For the leg (a, b, c, d) = (4.4, 1, 3.5, 2.25) with k = 1.6, find B and the foot at crank angle 0, then the rocker speed ratio by the instant centre and the mechanical advantage.

1. ______________________________  (hint: Crank angle 0: A = (1, 0), O4 = (4.4, 0), so D = 3.4. x = (c^2 - d^2 +...)
2. ______________________________  (hint: The foot hangs below the frame (the -1 assembly): B = (1 + 2.757, -2.1...)
3. ______________________________  (hint: The coupler line passes through A, which lies on the ground line y = 0...)
4. ______________________________  (hint: w4/w2 = x_I/(x_I - a) = 1/(1 - 4.4) = -5/17 = -0.294. The rocker turns...)
5. ______________________________  (hint: Power balance: MA = w2/w4 in magnitude = 17/5 = 3.4. Statics: the coup...)

Final answer: ____________________

## Questions
**A. Conceptual.** A Hoeken-type linkage (ground 2, crank 1, coupler 2.5, rocker 2.5, foot at k = 2) has a much flatter stance than our leg. Why is it not a good leg as it stands?

Answer: ______________________________________________


**B. Numerical.** Our leg has a stance deviation of 0.1658 and a stride of 2.143 crank lengths. Express the deviation as a percentage of the stride. If the crank is 0.05 m long and turns once per second, what are the stride in metres and the mean foot speed during the stance (stance is half of the turn)?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the mechanical-advantage figure the curve is 3.4 at crank angle 0 and rises steeply at some angles. What does 3.4 mean, and what is happening to the rocker where the curve shoots up?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the leg must dig at most 0.5 percent of its stride, lift at least 15 percent and keep the smallest transmission angle at or above 40 degrees, with the stance as straight as possible. Which (a, k) in the mini-project grid wins, and how risky is it?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
