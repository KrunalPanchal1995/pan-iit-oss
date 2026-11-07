# Activity sheet: opencrypto, Session 1: A secret message: the Caesar shift cipher

Name: ____________________   Date: ____________

**Objectives**

- Encrypt and decrypt a message by hand with a Caesar shift.
- Explain why a Caesar cipher has only 25 useful keys and why anyone can try them all.
- Use a readability score to pick the right shift automatically.
- Say why a cipher that is easy to break is still useful for learning but never for real secrets.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Encrypt SEE YOU AT NOON with key 5, then decrypt it again.

1. ______________________________  (hint: S = 18, 18 + 5 = 23 = X. E = 4, 4 + 5 = 9 = J. So SEE becomes XJJ....)
2. ______________________________  (hint: Y = 24, 24 + 5 = 29, which wraps to 29 - 26 = 3 = D. O = 14, 14 + 5 = ...)
3. ______________________________  (hint: A = 0 becomes F = 5, and T = 19 becomes Y = 24, so AT becomes FY....)
4. ______________________________  (hint: N = 13 becomes S = 18 and O = 14 becomes T = 19, so NOON becomes STTS....)
5. ______________________________  (hint: Ciphertext: XJJ DTZ FY STTS. To decrypt subtract 5: X = 23, 23 - 5 = 1...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can anyone break a Caesar cipher, even without knowing the key? Does it help to keep the method secret?

Answer: ______________________________________________


**B. Numerical.** Encrypt the word GO with key 20. Show the wrap-around, then check by decrypting.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the graph of readability against guess, why is one bar tall and the others low? Why can the gap be small for a very short message?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you must send a note that a classmate cannot read in the time they have, using only the ideas of this session. List two changes you could make and what each costs.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
