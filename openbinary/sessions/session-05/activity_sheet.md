# Activity sheet: openbinary, Session 5: A multiplier from gates

Name: ____________________   Date: ____________

**Objectives**

- Multiply two binary numbers on paper as shifted partial products added column by column.
- Make the partial products with AND gates and add them with half and full adders in the simulator.
- Check a 4 x 4 multiplier against Python's own product for all 256 input pairs.
- Say why the product of two n-bit numbers needs 2n bits.
- Read the gate count and delay of the multiplier from the simulator and explain how both grow with the width.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Multiply 7 x 3 with the AND-gate partial products and the column method, and check the answer.

1. ______________________________  (hint: Write the inputs: a = 0111 and b = 0011, so b0 = 1 and b1 = 1 and the...)
2. ______________________________  (hint: The partial products are row 0 = a = 0111 and row 1 = a shifted one pl...)
3. ______________________________  (hint: Column 0: only a0 AND b0 = 1, so the product bit is 1. Column 1: a1b0...)
4. ______________________________  (hint: Column 2: a2b0 = 1 and a1b1 = 1 plus the carry 1, total 3, so bit 1 an...)
5. ______________________________  (hint: Column 4: no ones plus the carry 1, total 1, so bit 1; the higher colu...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the product of two 4-bit numbers need 8 bits, and why does multiplying by 8 need no adder at all?

Answer: ______________________________________________


**B. Numerical.** Multiply 13 x 11 by partial products: write each row, add them, and give the product in binary. Sanity check with decimal arithmetic.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the size and delay graph, how many gates and how many gate delays does the multiplier have at n = 4 and at n = 8? What happens to each when the width doubles?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: each gate takes 0.5 ns and the product of an array multiplier must be ready within 10 ns. What is the widest multiplier allowed? What would you change to go wider?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
