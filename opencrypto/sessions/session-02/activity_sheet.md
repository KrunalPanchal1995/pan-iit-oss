# Activity sheet: opencrypto, Session 2: The key space, frequency analysis and Vigenere

Name: ____________________   Date: ____________

**Objectives**

- Count the keys of a cipher (25 for Caesar, 26! for a substitution cipher) and express them in bits.
- State Kerckhoffs's principle and explain why the attacker is assumed to know the method.
- Write a letter-frequency counter and use it to break a substitution cipher partly.
- Use the index of coincidence to guess the key length of a Vigenere cipher, and design a key length for a given message length.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
(a) How many keys does a substitution cipher have, and how many bits is that? (b) Compute the index of coincidence of the word LETTER by hand.

1. ______________________________  (hint: (a) 26! = 403291461126605635584000000, about 4.03 x 10^26....)
2. ______________________________  (hint: bits = log2(26!) = about 88.4, so a brute-force search must name one o...)
3. ______________________________  (hint: (b) Letter counts in LETTER: L 1, E 2, T 2, R 1. Compute n_i (n_i - 1)...)
4. ______________________________  (hint: n = 6, so n(n - 1) = 30 and IC = 4/30 = 2/15 = 0.1333....)
5. ______________________________  (hint: A six-letter word is far too short to estimate IC; the answer is exact...)

Final answer: ____________________

## Questions
**A. Conceptual.** A substitution cipher has about 4 x 10^26 keys. Why is it still easy to break? What does Kerckhoffs's principle say about the attacker?

Answer: ______________________________________________


**B. Numerical.** Encrypt HELLO with the Vigenere key AB. Then say how many keys of length 3 exist.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the figure of IC against guessed key length, why are there tall bars at 6, 12 and 18 but not at 4 or 5?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a message has 300 letters and you use a Vigenere cipher. Using the simulation facts of this session, choose a key length that stops the simple column attack, and give the trade-off. Why not just use a key as long as the message?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
