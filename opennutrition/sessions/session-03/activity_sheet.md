# Activity sheet: opennutrition, Session 3: A dynamic model: mass approaches a steady state

Name: ____________________   Date: ____________

**Objectives**

- Model body mass when expenditure rises with mass and show it approaches a steady state.
- Validate a numerical (Euler) solution against the closed-form exponential.
- Compare the dynamic model with the naive 7700 rule over 12 weeks and over 2 years.
- Propagate 10 percent input errors with Monte Carlo and explain a failure case.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Asha (made up) is 60 kg, 165 cm, 20 years, female, PAL 1.55, and eats 2400 kcal a day. Find the steady state and the mass after 12 weeks (84 days) from the dynamic model and the naive rule.

1. ______________________________  (hint: A = 10 x 1.55 = 15.5 kcal/day per kg. B = 1.55 x (6.25 x 165 - 5 x 20 ...)
2. ______________________________  (hint: Starting use E0 = 15.5 x 60 + 1193.89 = 2123.9 kcal/day, so the surplu...)
3. ______________________________  (hint: Steady state M_ss = (2400 - 1193.89) / 15.5 = 77.81 kg. Time constant ...)
4. ______________________________  (hint: Dynamic after 84 days: 62.77 kg. Naive: 60 + 276.1 x 84 / 7700 = 63.01...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the dynamic curve flatten while the naive line does not?

Answer: ______________________________________________


**B. Numerical.** For Asha, what steady-state mass does an intake of 2200 kcal a day give, and what fraction of the way to the steady state has the mass travelled after one time constant?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** Reading the first figure: by how much do the naive and dynamic answers differ at 12 weeks and at 2 years (intake 2400)? What does this tell you about using the 7700 rule?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a planner for the made-up person Asha (sedentary base, 60 kg) wants a starting daily balance between -225 and -175 kcal using meal plans of 1400, 1500, 1600 or 1700 kcal and walking in 15 minute steps up to 1.5 hours. Which plans pass, which is the least walking, and can a 12-week weigh-in confirm it? State a trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
