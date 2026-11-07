# Activity sheet: openmole, Session 3: An automatic balancer and a reactor sweep

Name: ____________________   Date: ____________

**Objectives**

- Write a reaction as an element-by-species matrix A and explain why the coefficients solve A c = 0.
- Find integer coefficients as the null space of A with numpy and fractions.Fraction, and validate them on known reactions.
- Check conservation of atoms, mass and charge, including for an ionic equation.
- Sweep a reagent feed ratio, measure the sensitivity of the answer to the molar-mass table, and recognise equations with no solution or many solutions.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Balance Fe2O3 + Al -> Al2O3 + Fe with the null-space method and verify the result.

1. ______________________________  (hint: Species columns in order: Fe2O3, Al, Al2O3, Fe. Rows in alphabetical o...)
2. ______________________________  (hint: Row Al: b - 2c = 0. Row Fe: 2a - d = 0. Row O: 3a - 3c = 0. So c = a, ...)
3. ______________________________  (hint: Take a = 1: the null vector is (1, 2, 1, 2). The numpy SVD returns a u...)
4. ______________________________  (hint: Check by integers: A c = (0 + 2 - 2, 2 + 0 - 0 - 2, 3 + 0 - 3 - 0) = (...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a unique balanced equation correspond to a null space of dimension exactly 1? What would nullity 0 and nullity 2 mean?

Answer: ______________________________________________


**B. Numerical.** How many kilograms of hydrogen are needed for 250 kg of ammonia, assuming complete reaction? Check with a mass balance.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the feed-ratio graph (left), why does the NH3 line become flat at ratio 3 while the red waste curve has a V shape with its minimum at 3?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a plant feeds 100 kmol/h of N2, but the hydrogen meter is only good to plus or minus 5 percent. Choose the hydrogen set-point ratio so that yield never falls below 99.5 percent of the possible ammonia, and report the worst-case hydrogen waste.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
