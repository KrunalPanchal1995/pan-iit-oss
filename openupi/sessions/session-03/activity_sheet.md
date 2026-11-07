# Activity sheet: openupi, Session 3: A toy payment switch: failures, invariants and fraud rules

Name: ____________________   Date: ____________

**Objectives**

- Store a PIN safely as a salted hash and compare it in constant time, and explain why.
- Inject lost requests, lost replies and retries into a switch and check three invariants: money conserved, no negative balance, no double charge.
- Validate a formula for the expected number of charges against a simulation, and show the failure case without idempotency keys.
- Measure false positive and false negative rates of three fraud rules on seeded synthetic data and read the trade-off.
- Design a limit that caps the damage when fraud rules miss.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A test set has 1000 ordinary payments and 50 fraud payments. The rules flag 30 ordinary payments and 40 fraud payments. Find the false positive rate and the false negative rate and say what each means.

1. ______________________________  (hint: Ordinary payments: flagged = 30 (false positives, FP = 30), not flagge...)
2. ______________________________  (hint: FPR = FP / (FP + TN) = 30 / 1000 = 0.03, that is 3 percent of ordinary...)
3. ______________________________  (hint: Fraud payments: flagged = 40 (true positives, TP = 40), not flagged = ...)
4. ______________________________  (hint: FNR = FN / (FN + TP) = 10 / 50 = 0.20, that is 20 percent of fraud pay...)
5. ______________________________  (hint: Sanity check: 30 + 970 = 1000 and 40 + 10 = 50, so every payment is co...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do we store a salted hash of a PIN instead of the PIN, and why compare with compare_digest instead of ==? Why is hashing still not enough for a 4-digit PIN?

Answer: ______________________________________________


**B. Numerical.** With p_req = 0.1, p_rep = 0.2 and k = 3, compute a, s, the expected charges per payment without a key and with a key, and the expected extra charges per 100 payments.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the right-hand panel of the first figure, what happens to FPR and FNR when the velocity limit V changes from 5 to 3, and which kind of mistake does each setting prefer?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you may annoy at most 4 percent of ordinary payments. Choose the velocity limit V from the sweep (V = 2 to 11 gives FPR 7.54, 5.33, 3.69, 2.82, 2.79, 2.79, ...) and then say what else you would add to catch slow, small attacks and what you would use to cap the damage if a burst gets through.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
