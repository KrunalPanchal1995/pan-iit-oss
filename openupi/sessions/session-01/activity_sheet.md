# Activity sheet: openupi, Session 1: The cast of a payment and its message flow

Name: ____________________   Date: ____________

**Objectives**

- Name the five actors in a digital payment and say what each one does and does not hold.
- Read a sequence diagram: time runs downwards and each arrow is one message.
- Explain that money moves as changes of numbers in ledgers, not as coins.
- Check that the total across all ledgers and the in-flight box never changes during a payment.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The payer has Rs 1000 and the payee has Rs 400. The payer pays Rs 250. Find the three numbers after each step and check the total.

1. ______________________________  (hint: Before step 3 nothing has moved: payer 1000, in flight 0, payee 400, t...)
2. ______________________________  (hint: Step 3 (payer bank debits): payer = 1000 - 250 = 750 and in flight = 2...)
3. ______________________________  (hint: Step 4 (switch asks payee bank): nothing changes yet....)
4. ______________________________  (hint: Step 5 (payee bank credits): in flight = 0 and payee = 400 + 250 = 650...)
5. ______________________________  (hint: Sanity check: the payer lost 250 and the payee gained 250, so the tota...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do the payer app and the payee app hold no money, and why do we need the in-flight box at the switch?

Answer: ______________________________________________


**B. Numerical.** The payer has Rs 2000 and the payee has Rs 150. The payer pays Rs 600. Give the three numbers after step 3 and after step 6, and the total each time.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the stacked-bar figure, at which steps is there an orange in-flight block, and what happens to the total height?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the switch crashes after step 3 and never sends step 4. The payer has lost Rs 250 and the payee has gained nothing. Describe two sensible ways the system could recover, and what each would have to remember.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
