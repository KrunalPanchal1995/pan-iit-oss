# Activity sheet: opensymbolic, Session 3: A real formula search: recover the law, measure the success rate

Name: ____________________   Date: ____________

**Objectives**

- Enumerate every formula up to a size and remove duplicates.
- Fit the constants of every formula exactly because they enter linearly, and choose with a complexity penalty.
- Measure how often the search recovers the true law at a stated noise level.
- Explain two failures (overfitting and a law outside the search space) and use units to filter impossible power laws.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Run the search on noise-free data from y = 3 x^2 (30 points, x from 0.5 to 5). Which formula is chosen and with which constants?

1. ______________________________  (hint: Enumeration up to 7 nodes on these x values keeps 11777 distinct formu...)
2. ______________________________  (hint: For every formula the exact fit gives a, b and the error....)
3. ______________________________  (hint: The Pareto front starts with x (a straight line fits poorly) and reach...)
4. ______________________________  (hint: For sq(x) the exact fit returns a = 3.000 and b = 0.000 with an error ...)
5. ______________________________  (hint: Every larger formula at the noise-free error is a duplicate or a worse...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does fitting y = a f(x) + b make the search much faster than trying many values of the constants one by one?

Answer: ______________________________________________


**B. Numerical.** Fit y = a f + b by hand to the data y = (1, 3, 5) at f = (0, 1, 2). Give a, b and the error.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the recovery-rate plot at 5 percent noise the rates for 40 trials are 97.5 percent for the quadratic, pendulum and Arrhenius laws and 87.5 percent for the saturating law; at 20 percent noise they are 87.5, 92.5, 97.5 and 0 percent. Interpret the difference.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a pendulum experiment used lengths L = g/2 by accident (so L and g are tied together), with the mass varied freely. Out of 729 exponent triples (p, q, r) from -2 to 2 in steps of 0.5, 9 fit equally well. How can units pick the right one, and how would you redesign the experiment so that fewer triples tie?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
