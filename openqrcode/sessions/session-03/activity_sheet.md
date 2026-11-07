# Activity sheet: openqrcode, Session 3: A toy matrix code, damaged and repaired

Name: ____________________   Date: ____________

**Objectives**

- Build a toy 2D code: message, check byte, Hamming blocks, interleaving, finder patterns.
- Damage it with random noise and with a burst, and decode it.
- Compare the measured success rate with the formula P_block^10 and with a repetition code.
- Explain why interleaving defeats bursts, and show a failure case with too much damage.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
At q = 5 percent random damage, what is the probability that the toy code is read correctly? Compare with a simulation.

1. ______________________________  (hint: No flips in a block: (0.95)^7 = 0.6983....)
2. ______________________________  (hint: Exactly one flip in a block: 7 x 0.05 x (0.95)^6 = 0.35 x 0.7351 = 0.2...)
3. ______________________________  (hint: P_block = 0.6983 + 0.2573 = 0.9556....)
4. ______________________________  (hint: All 10 blocks must survive: P_msg = 0.9556^10 = 0.635....)
5. ______________________________  (hint: A simulation of the whole pipeline (build, damage, decode) with thousa...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does writing the codewords as rows and sending the columns (interleaving) help against a scratch, even though it adds no new bits?

Answer: ______________________________________________


**B. Numerical.** For q = 2 percent, find P_block and P_msg for the toy code, and say how many of 100 parcels you expect to read.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the success-versus-damage graph, at about which damage do the Hamming and the no-protection curves differ most, and what does the dashed line at 15.7 percent mean?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a label gets bursts of up to 7 squares. You may choose the interleave group 1, 2, 5 or 10. Which do you pick, and what is the price of choosing the largest group when random noise is also present?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
