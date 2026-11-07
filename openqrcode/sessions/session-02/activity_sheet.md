# Activity sheet: openqrcode, Session 2: Parity bits and the Hamming(7,4) code

Name: ____________________   Date: ____________

**Objectives**

- Compute parity bits and a Hamming(7,4) codeword by hand and with the matrix G.
- Find and fix a single flipped bit with the syndrome H r.
- Explain code rate and redundancy as a trade-off.
- Use 2^r >= k + r + 1 to design how many parity bits a block needs.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Encode the data 1011, flip the third bit, and use the syndrome to find and fix it.

1. ______________________________  (hint: Parity bits (mod 2): p1 = d1+d2+d4 = 1+0+1 = 2 -> 0; p2 = d1+d3+d4 = 1...)
2. ______________________________  (hint: Codeword: 1011 followed by 010, that is 1011010....)
3. ______________________________  (hint: Flip bit 3: the receiver gets 1001010....)
4. ______________________________  (hint: Syndrome, row 1 of H is 1101100: 1+0+0+1+0+0+0 = 2 -> 0. Row 2 is 1011...)
5. ______________________________  (hint: The syndrome 011 equals column 3 of H, so bit 3 is wrong. Flip it back...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can a single parity bit detect one flipped bit but not repair it, while three overlapping parity checks can repair it?

Answer: ______________________________________________


**B. Numerical.** You receive 0100110 (Hamming(7,4) as in the lesson). Find the syndrome, the flipped bit and the data.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the rate graph, what are the rates for r = 3, 4 and 5, and why does the rate rise with r? What do we lose?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you must protect 100 data bits, one error per block. Compare (a) one big block with (b) 25 separate Hamming(7,4) blocks, in parity bits, code rate and robustness.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
