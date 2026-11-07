# Activity sheet: openupi, Session 2: A ledger, atomic payments and safe retries

Name: ____________________   Date: ____________

**Objectives**

- Write a payment as a double entry: two signed entries that add up to zero.
- Compute any balance as the sum of that account's entries and check that the whole ledger sums to zero.
- Explain atomic (all-or-nothing) transactions and show what a crash does without them.
- Use a unique transaction id to make a retry idempotent and count charges with and without it.
- Order the checks before a debit and justify the order.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Start with payer 1000 and payee 400. Process (T1: pay 250), then (T1 again), then (T2: pay 900). Give the final balances and say what each reply is.

1. ______________________________  (hint: T1 is new, authenticated, 250 is within the limit and 1000 >= 250, so ...)
2. ______________________________  (hint: T1 again is a duplicate id, so the saved reply (ok) is returned and no...)
3. ______________________________  (hint: T2 asks for 900 but the payer has only 750, so it is declined: insuffi...)
4. ______________________________  (hint: Check: the entries are two deposits and one payment; every transaction...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is it a problem if a program writes the debit, then crashes before writing the credit? What does writing both entries in one step change?

Answer: ______________________________________________


**B. Numerical.** The payer has Rs 1000. A request for Rs 300 arrives 5 times. How much is the payer charged in total, and what are both balances, (a) without an id check and (b) with one? The payee starts with Rs 400.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the retries figure (Rs 250 from Rs 1000), what are the payer balances without the id check for 1, 2, 3, 4 and 8 arrivals, and why does the red curve go flat?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: list the checks a bank should run before debiting in a good order, and for each say what goes wrong if it is moved. Assume a per-payment limit of Rs 2000.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
