# Activity sheet: openfloat, Session 1: Numbers with gaps

Name: ____________________   Date: ____________

**Objectives**

- Explain why 0.1 + 0.2 is not exactly 0.3 on a computer.
- Describe stored numbers as points on a number line with gaps between them.
- Predict how the gap grows with the size of the number.
- Compare computed numbers with a tolerance instead of ==.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Find the gap above 1000 in the 64-bit format by hand, then check it by computer. Also explain why 2^53 + 1 equals 2^53.

1. ______________________________  (hint: 1000 lies between 512 = 2^9 and 1024 = 2^10, so k = 9....)
2. ______________________________  (hint: gap = 2^(k - 52) = 2^(9 - 52) = 2^-43....)
3. ______________________________  (hint: 2^-43 = 1.137e-13. The relative gap is 1.137e-13 / 1000 = 1.137e-16, b...)
4. ______________________________  (hint: For 2^53: k = 53, so gap = 2^(53 - 52) = 2. The next number after 2^53...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can 0.5 be stored exactly but 0.1 cannot?

Answer: ______________________________________________


**B. Numerical.** What is the gap just above 1000.0 in a 64-bit float? What is the relative gap? Does your answer pass a sanity check?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the graph view with 3 fraction bits, what is the gap for numbers in [8, 16) and how many numbers are stored there? What changes if you use 5 fraction bits?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a toy sensor must store lengths from 1 to 16 units with a gap of at most 0.1 units everywhere. How many fraction bits m are needed? What is the cost of using more?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
