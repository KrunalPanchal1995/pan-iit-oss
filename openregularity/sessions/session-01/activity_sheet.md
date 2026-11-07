# Activity sheet: openregularity, Session 1: Smooth or blow-up? The question and a toy

Name: ____________________   Date: ____________

**Objectives**

- Explain in plain words what the Navier-Stokes smoothness problem asks, and say clearly that it is open.
- Show, with a formula and a computer, that dy/dt = y^2 becomes infinite at t = 1/y0, while dy/dt = y never does.
- Say why a smooth wave that steepens moves its energy to small scales.
- Read a graph of a quantity approaching infinity at a finite time.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For dy/dt = y^2 with y0 = 2, find the blow-up time and the value of y at t = 0.4. Check the blow-up time with a computer.

1. ______________________________  (hint: Separate variables: dy / y^2 = dt, so -1/y = t - 1/y0 + ..., which giv...)
2. ______________________________  (hint: y is infinite when the denominator is zero: t* = 1/y0 = 1/2 = 0.5....)
3. ______________________________  (hint: At t = 0.4: y = 2 / (1 - 2 * 0.4) = 2 / 0.2 = 10....)
4. ______________________________  (hint: The computer (RK4 with steps that shrink as y grows) reaches y = 1,000...)

Final answer: ____________________

## Questions
**A. Conceptual.** In one or two sentences, what does the Navier-Stokes smoothness problem ask, and what is its status?

Answer: ______________________________________________


**B. Numerical.** For dy/dt = y^2, find the blow-up time for y0 = 4 and for y0 = 0.5. What happens to the time when y0 doubles?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the growth view, which curve reaches the top of the plot first for y0 = 1: p = 2 or p = 1.5? What does p = 1 do?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you are told y follows dy/dt = y^2 and the model is only trusted until t = 1.5. Find the largest starting value y0 for which no blow-up occurs before t = 1.5, and one reason the answer is only a model result.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
