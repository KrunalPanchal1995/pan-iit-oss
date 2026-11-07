# Activity sheet: openepidemic, Session 1: Three boxes with arrows: how an outbreak rises and falls

Name: ____________________   Date: ____________

**Objectives**

- Describe the S, I and R boxes and the two arrows between them.
- Explain why an infection spreads when each case infects more than one other person.
- Read a graph of infected people against time: it rises, peaks and falls.
- Compute and use the number R0 = beta / gamma.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A town has N = 1000 people, 999 susceptible and 1 infected. With beta = 0.5 and gamma = 0.25 per day, move the people for one day (dt = 1) and find R0.

1. ______________________________  (hint: New infections = 0.5 * 999 * 1 / 1000 * 1 = 0.4995 people....)
2. ______________________________  (hint: New recoveries = 0.25 * 1 * 1 = 0.25 people....)
3. ______________________________  (hint: S = 999 - 0.4995 = 998.5005; I = 1 + 0.4995 - 0.25 = 1.2495; R = 0 + 0...)
4. ______________________________  (hint: Check: 998.5005 + 1.2495 + 0.25 = 1000, so nobody was lost....)
5. ______________________________  (hint: R0 = beta / gamma = 0.5 / 0.25 = 2, so one case infects about 2 others...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the number of infected people fall after the peak even if nobody changes their behaviour?

Answer: ______________________________________________


**B. Numerical.** A town has beta = 0.3 and gamma = 0.1 per day. Find R0 and the number of cases in generation 3, starting from one case.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the S, I, R figure, on which day is the peak, roughly how many people are infected then, and what happens to R at that moment?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with gamma = 0.25 per day, the town's contact rate is beta = 0.5. A school-closure plan could reduce beta. What beta makes R0 equal to exactly 1, and what happens if the plan reaches beta = 0.2? State one reason your answer might be too optimistic.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
