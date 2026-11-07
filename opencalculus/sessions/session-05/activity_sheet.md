# Activity sheet: opencalculus, Session 5: Gaussian quadrature: choosing where to sample

Name: ____________________   Date: ____________

**Objectives**

- Compute the nodes and weights of the Gauss-Legendre rule (roots of a Legendre polynomial, found with Newton's method).
- Apply the rule on any interval and say what it costs (n points are n function values).
- Explain why n points are exact up to degree 2n - 1 and test it.
- Compare Gauss, Simpson and Romberg for the same number of function values.
- Recognise the failure cases: a function that is not smooth, a periodic function, a narrow peak, and the cost of rules that are not nested.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Find the area of e^x on [0, 1] with the 2-point and the 3-point Gauss-Legendre rules and compare with Simpson's rule for the same number of function values.

1. ______________________________  (hint: Exact: e - 1 = 1.718282. On [0, 1] the midpoint is m = 0.5 and the hal...)
2. ______________________________  (hint: Two points: t = plus or minus 0.577350, so x = 0.5 plus or minus 0.288...)
3. ______________________________  (hint: Two-point area: 0.5 x (1 x 1.235314 + 1 x 2.200479) = 1.717896, error...)
4. ______________________________  (hint: Three points: t = -0.774597, 0 and 0.774597, so x = 0.112702, 0.5 and...)
5. ______________________________  (hint: Three-point area: 0.5 x (5/9 x 1.119298 + 8/9 x 1.648721 + 5/9 x 2.428...)
6. ______________________________  (hint: Simpson's rule with the same 3 values (x = 0, 0.5, 1) gives 1.718861 w...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is the n-point Gauss-Legendre rule exact up to degree 2n - 1, when the n-point rule with equally spaced points is exact only up to about degree n - 1?

Answer: ______________________________________________


**B. Numerical.** Use the 2-point Gauss-Legendre rule to find the area of x^3 + 1 on [1, 3], and then the area of x^4 on [1, 3]. The exact answers are 22 and 48.4.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the error-against-values figure for the bell curve, at 9 values the errors are 1.6e-5 (Simpson), 5.0e-5 (Romberg) and 1.2e-11 (Gauss). What do you conclude about Gauss, and about the claim that Romberg is always better than Simpson?

Answer: ______________________________________________


**D. Design and optimisation challenge.** You can afford 10 function values (10 minutes) for the area of exp(-x^2) on [0, 2]. Which rule do you choose and what error do you expect? Then suppose you needed 1e-12 and did not know how many points to use: what would the Gauss approach cost, and how does it compare with Romberg?

Answer: ______________________________________________


## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
