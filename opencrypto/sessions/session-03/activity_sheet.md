# Activity sheet: opencrypto, Session 3: Perfect secrecy, hashes, HMAC and key size

Name: ____________________   Date: ____________

**Objectives**

- Explain the one-time pad, why it gives perfect secrecy, and why reusing the key breaks it.
- Show that a short key (16 bits) is found by trying everything, and compute the time to try 2^b keys at a stated rate.
- Verify the avalanche effect of SHA-256, and explain why salted PBKDF2 hashes defeat a precomputed table.
- Use HMAC with a constant-time comparison to detect a changed message.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
How long does it take to try all keys of 40 bits (a) at 10^6 guesses per second and (b) at 10^12 guesses per second? How many bits are needed so that trying all keys takes at least 100 years at 10^12 per second?

1. ______________________________  (hint: 2^40 = 1099511627776 keys....)
2. ______________________________  (hint: (a) 1099511627776 / 10^6 = 1099512 seconds. Divide by 86400 seconds pe...)
3. ______________________________  (hint: (b) 1099511627776 / 10^12 = about 1.1 seconds....)
4. ______________________________  (hint: 100 years = 100 x 365.25 x 86400 = 3.156 x 10^9 seconds. Keys needed a...)
5. ______________________________  (hint: log2(3.156 x 10^21) = 71.4, so round up to 72 bits. Check: 71 bits is ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does reusing a one-time pad key destroy its security, even though the pad is perfectly secret when used once?

Answer: ______________________________________________


**B. Numerical.** A 40-bit key is tried at 10^6 guesses per second. How long does a full search take, and how does that change if the key has 41 bits?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the time graph, which of the key sizes 40, 56, 80 and 128 bits are within one year at 10^12 guesses per second? What does the shape of the line tell you?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a site stores 5 users' passwords. Compare (i) plain SHA-256 hashes with (ii) salted PBKDF2 hashes against an attacker who has a table for a dictionary of 8 words. State what the attacker must do in each case and give the work.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
