# Activity sheet: openbinary, Session 2: Number systems, logic gates and Boolean algebra

Name: ____________________   Date: ____________

**Objectives**

- Convert whole numbers between binary, decimal and hexadecimal, by hand and by a function you test on thousands of numbers.
- Write the truth tables of AND, OR, NOT, XOR and NAND.
- Verify De Morgan's laws by trying every input.
- Show that NAND alone can build NOT, AND, OR and XOR.
- Design a gate from a truth table using sum of products, and verify it on every input.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Convert 183 to binary and to hexadecimal, and check by converting back.

1. ______________________________  (hint: Divide by 2 repeatedly and collect remainders from last to first. 183 ...)
2. ______________________________  (hint: So 183 is 10110111 in binary....)
3. ______________________________  (hint: Group in fours from the right: 1011 and 0111. 1011 is 11, which is B, ...)
4. ______________________________  (hint: So 183 is B7 in hexadecimal....)
5. ______________________________  (hint: Check: B7 = 11 x 16 + 7 = 176 + 7 = 183. The same number....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can NAND build every other gate? Show how to get NOT and OR from NAND.

Answer: ______________________________________________


**B. Numerical.** Convert the hexadecimal number A5 to decimal and to binary, and convert decimal 100 to binary and hexadecimal. Sanity check.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the comparator figure (A down the side, B along the top, dark where A > B), where are the dark squares and how many are there? Why is the diagonal white?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a lock opens when the 2-bit number A equals the 2-bit number B. Build the truth table, write the sum-of-products form and give a shorter form with XNOR. How many minterms are there?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
