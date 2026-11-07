# Activity sheet: openqrcode, Session 1: Squares of data and the check digit

Name: ____________________   Date: ____________

**Objectives**

- Explain how text becomes a grid of black and white squares.
- Compute the EAN-13 check digit of a 12-digit number by hand and in Python.
- Verify real-format numbers with the check.
- State what a check digit catches (and what it misses) and why it cannot repair anything.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Find the check digit of the 12 digits 400638133393 and say whether 4006381333931 is valid.

1. ______________________________  (hint: Write the digits with weights 1, 3, 1, 3, ...: 4x1, 0x3, 0x1, 6x3, 3x1...)
2. ______________________________  (hint: Products: 4, 0, 0, 18, 3, 24, 1, 9, 3, 9, 9, 9....)
3. ______________________________  (hint: Sum of the 12 products: S = 4 + 0 + 0 + 18 + 3 + 24 + 1 + 9 + 3 + 9 + ...)
4. ______________________________  (hint: The next multiple of 10 above 89 is 90, so the check digit is 90 - 89 ...)
5. ______________________________  (hint: The full number is 4006381333931. Its 13 weighted terms add to 89 + 1x...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can the check digit tell you that a number is wrong, but not which digit is wrong? What extra would you need to repair it?

Answer: ______________________________________________


**B. Numerical.** Find the check digit for the 12 digits 590123412345 and show the weighted sum.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the graph of the weighted sum mod 10 against the digit written in place 6 (weight 3), how much does the remainder move when the digit goes up by 1? Why does exactly one digit give 0?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a library wants a check digit for 6-digit member numbers that catches EVERY swap of two neighbouring digits, which the EAN-13 rule does not (it misses digits that differ by 5). Propose a rule and state its cost.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
