# Activity sheet: openfloat, Session 2: The 64-bit format, rounding and cancellation

Name: ____________________   Date: ____________

**Objectives**

- Read the 1 sign bit, 11 exponent bits and 52 fraction bits of a 64-bit float.
- State and compute machine epsilon 2^-52 with NumPy, and the relative rounding error bound 2^-53.
- Recognise catastrophic cancellation and repair a formula (quadratic root, 1 - cos).
- Explain overflow and underflow and the range of a 64-bit float.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
(a) Decode -6.5 into sign, exponent field and fraction field. (b) For x^2 - 1e6 x + 1 = 0, compute the small root with both formulas and measure the error. (c) Show why 1 - cos(1e-8) is exactly 0.

1. ______________________________  (hint: (a) -6.5 = -1.625 x 2^2. Sign bit s = 1. True exponent 2, so e = 2 + 1...)
2. ______________________________  (hint: (b) b = 1e6, c = 1. sqrt(b^2 - 4) = 999999.999998, very close to b = 1...)
3. ______________________________  (hint: Relative error of the textbook root = 7.6e-6, so only about 5 correct ...)
4. ______________________________  (hint: (c) For t = 1e-8, cos t = 1 - t^2/2 = 1 - 5e-17. The gap just below 1 ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does computing 1 - cos(1e-8) give exactly 0 although each single operation is accurate to 16 digits?

Answer: ______________________________________________


**B. Numerical.** Decode 0.15625 (that is 5/32): give s, e and the fraction field f. Sanity check by rebuilding the value.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the app graph view (c = 1), roughly how does the error of the textbook small root change when p increases by 1? About how many digits are correct at p = 6?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a program must evaluate 1 - cos(t) for every angle from 1e-9 to 1 radian with a relative error below 1e-12. Choose the formula(s). Where, if anywhere, is the textbook form acceptable?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
