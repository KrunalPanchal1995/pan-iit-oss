# Activity sheet: openbinary, Session 3: Build an adder from gates and see how computers count

Name: ____________________   Date: ____________

**Objectives**

- Build a half adder, a full adder and an n-bit ripple-carry adder in a small gate-level simulator.
- Represent negative numbers in two's complement and subtract with the same adder.
- Detect overflow, and explain why 7 + 1 gives -8 on four bits.
- Measure the gate delay of the carry chain and explain why it grows with the number of bits.
- Select add, subtract, AND or OR in a 4-bit ALU slice and validate it against Python for every input.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Compute 6 - 3 on four bits with the adder-subtractor, showing the bits.

1. ______________________________  (hint: Subtraction means sub = 1: flip every bit of b and add 1 through the c...)
2. ______________________________  (hint: 6 is 0110 and 3 is 0011; flipping the bits of 3 gives 1100....)
3. ______________________________  (hint: Add 0110 + 1100 + 1 (the carry in) = 10011....)
4. ______________________________  (hint: Keep only four bits: 0011, the carry out of the top bit is thrown away...)
5. ______________________________  (hint: 0011 is 3, and 6 - 3 = 3. The carry into the top bit and the carry out...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does 7 + 1 give -8 on four bits, and how does the circuit know that the answer is wrong?

Answer: ______________________________________________


**B. Numerical.** Compute 5 - 7 on four bits: show the three numbers you add, the four-bit result, and whether overflow occurs. Sanity check with ordinary arithmetic.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the delay graph, how many gate delays does the carry take for 8 bits, and for 12 bits? What does the slope of the line tell you?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: each gate takes 0.5 ns and the carry out of a ripple adder must be ready within 20 ns. What is the widest adder allowed? What would you change to go wider?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
