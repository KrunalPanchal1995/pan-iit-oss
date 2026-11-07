# Activity sheet: openfloat, Session 3: Accumulated error: Patriot, Ariane 5 and safe summation

Name: ____________________   Date: ____________

**Objectives**

- Measure how rounding error grows when 0.1 is added ten million times, and compare it with the worst-case bound.
- Use Kahan (compensated) summation and math.fsum to remove most of that error.
- Reproduce the commonly cited Patriot clock drift (about 0.34 s after 100 hours) from a 0.1 chopped to 23 binary places.
- Show how a conversion to a 16-bit integer wraps, and add a range check.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
(a) Compute the Patriot clock error after 100 hours and the distance a 1676 m/s target covers in that time, from 0.1 chopped to 23 places. (b) What does 40000 become in a 16-bit signed integer? (c) State the measured error of summing 0.1 ten million times, naive versus Kahan.

1. ______________________________  (hint: (a) 0.1 = 0.0001100110011... in binary. Chopping at 23 places leaves a...)
2. ______________________________  (hint: 100 hours = 100 x 3600 s = 360000 s = 3,600,000 ticks. Clock error = 3...)
3. ______________________________  (hint: Distance = 1676 m/s x 0.3433 s = 575 m, about 0.58 km, in line with th...)
4. ______________________________  (hint: (b) 40000 is above 32767. Wrap: (40000 + 32768) mod 65536 - 32768. Fir...)
5. ______________________________  (hint: (c) Ten million terms: the exact reference is 1,000,000 (rounded to a ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the error of the naive sum keep growing while Kahan's stays flat? Why does it not matter that 0.1 itself is not exactly 0.1 in this comparison?

Answer: ______________________________________________


**B. Numerical.** Compute the Patriot clock error and the distance covered by a 1676 m/s target after 48 hours with 23 binary places. Sanity check against the 100 hour result.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the error-growth plot, how does the naive error change from n = 1e5 to n = 1e7? How far is it from the worst-case bound at n = 1e7?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a sensor reports values from -50000 to 50000 as floats, and a legacy interface accepts only 16-bit signed integers. Propose a conversion with scaling, a range check and a policy for bad values. What resolution do you get?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
