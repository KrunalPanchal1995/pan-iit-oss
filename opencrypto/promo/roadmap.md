# Roadmap: the path to the opencrypto Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Break a substitution cipher completely

**You will learn:** Letter pairs (bigrams) and common words as extra clues, and hill climbing: improving a guess by small swaps.

**You will build:** A solver that starts from frequency ranks and improves the key with a score for letter pairs.

**Checkpoint (not met by the shipped code):** At least 90 percent of the letters right on a substitution ciphertext of at least 700 letters (the shipped rank matching gives 44 percent on the Session 2 sample).

**Difficulty:** intermediate

## Session 5: Vigenere with any key length

**You will learn:** Repeated-sequence spacing (Kasiski) as a second way to find the key length, and how both methods behave for long keys.

**You will build:** A Vigenere breaker that searches key lengths up to 20.

**Checkpoint (not met by the shipped code):** Exact key recovered in at least 9 of 10 random trials for a 14-letter key and 1200-letter English-like texts (the shipped code, which searches up to 12, recovers 0 of 10).

**Difficulty:** intermediate

## Session 6: Why modes of operation matter

**You will learn:** Block ciphers, and why encrypting each block separately (ECB) leaks repeated patterns while chaining (CBC) does not.

**You will build:** A toy 8-byte block cipher used in two modes, with a pattern counter.

**Checkpoint (not met by the shipped code):** For 64 identical plaintext blocks: 1 distinct ciphertext block in the separate mode and 64 distinct blocks in the chained mode (the shipped code has no block mode).

**Difficulty:** advanced

## Session 7: How strong is a password?

**You will learn:** Entropy of a randomly chosen password, and how slow hashing multiplies an attacker's cost.

**You will build:** A calculator for bits of entropy and the time to try every password at an assumed rate and hash cost.

**Checkpoint (not met by the shipped code):** A random 12-letter lowercase password is reported as 56.4 bits and the time at an assumed rate is printed for plain and for 1000-times-slower hashing (the shipped code only tabulates key sizes).

**Difficulty:** intermediate

## Session 8: Public keys with a toy RSA

**You will learn:** Modular powers and why publishing an encryption key can be safe: factoring a large number is hard.

**You will build:** A toy RSA with the textbook numbers n = 3233, e = 17 and d = 2753, plus a trial-division factoring demo for small n.

**Checkpoint (not met by the shipped code):** The message 65 encrypts to 2790 and decrypts back to 65, and a 32-bit n is factored by trial division in under a second while the text explains why 2048-bit numbers are out of reach.

**Difficulty:** advanced

## The final step

Combine the milestones: a solver that breaks a substitution cipher from letter statistics, with a chart that compares your attack's effort with the size of the key space, as in the Target animation. If your result looks like the Target, open a pull request and tell us how you did it. Remember the rule of this repo: toy ciphers for learning only; real systems use vetted libraries.
