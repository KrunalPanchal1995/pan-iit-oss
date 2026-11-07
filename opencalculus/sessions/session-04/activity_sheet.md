# Activity sheet: opencalculus, Session 4: Romberg integration: far more accuracy from the same function values

Name: ____________________   Date: ____________

**Objectives**

- Build a Romberg table from trapezoid sums that reuse every function value.
- Explain why (4 T(h/2) - T(h)) / 3 removes the h^2 error, and why that is Simpson's rule.
- Measure the order of each column of the table (2, 4, 6, ...).
- Count how many function values a rule needs for a target error.
- Recognise the failure cases: a function that is not smooth at an endpoint, a periodic function, and a stopping rule that is fooled.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Build a three-row Romberg table for the area of e^x on [0, 1] and compare its corner with Simpson's rule for the same function values.

1. ______________________________  (hint: Exact: e - 1 = 1.718282. The trapezoid rule with 1, 2 and 4 slices giv...)
2. ______________________________  (hint: First column of corrections: R(1,1) = (4 x 1.753931 - 1.859141) / 3 =...)
3. ______________________________  (hint: R(2,1) is Simpson's rule with 4 slices: the same number you found in S...)
4. ______________________________  (hint: Second column: R(2,2) = (16 x 1.718319 - 1.718861) / 15 = 1.718283....)
5. ______________________________  (hint: The error of R(2,2) is +8.6e-7. With the same 5 values the trapezoid r...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does (4 T(h/2) - T(h)) / 3 remove the h^2 error of the trapezoid rule, and why do we divide by 3?

Answer: ______________________________________________


**B. Numerical.** The trapezoid rule for pi = the area of 4 / (1 + x^2) on [0, 1] gives T0 = 3.000000, T1 = 3.100000 and T2 = 3.131176. Complete the Romberg table (R(1,1), R(2,1), R(2,2)) and say which entry is closest to pi = 3.141593.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the error-against-values figure for e^x, at 17 values the errors are 5.6e-4 (trapezoid), 1.5e-7 (Simpson) and 3.3e-14 (Romberg). By what factor is Romberg better than each, and what happens to its line beyond 33 values?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Your budget is 40 function values (40 minutes) for the area of exp(-x^2) on [0, 2]. On the grids of 2^k + 1 values, which rule should you use and what error will it reach? What must you budget if you need 1e-12?

Answer: ______________________________________________


## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
