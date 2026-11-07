# Activity sheet: openclimate, Session 3: Simulate the warming and validate it

Name: ____________________   Date: ____________

**Objectives**

- Step the energy balance forward in time with an ocean heat capacity (forward Euler).
- Validate the simulation against the Session 2 equilibrium, the exact step response and energy conservation.
- Use the CO2 forcing 5.35 ln(C / 280) and the feedback parameter lambda to get equilibrium and transient warming.
- Explain "warming in the pipeline" and find the CO2 level that keeps equilibrium warming below 2 K.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 70 m ocean layer, ECS = 3 K. CO2 doubles overnight and then stays. Find C, lambda, tau, the warming after 10 years and the final warming; check the simulation and the energy balance.

1. ______________________________  (hint: C = 1025 x 3990 x 70 / 3.156 x 10^7 = 9.07 W yr/(m2 K).)
2. ______________________________  (hint: F2x = 5.35 x ln 2 = 3.708 W/m2; lambda = 3.708 / 3 = 1.236 W/(m2 K).)
3. ______________________________  (hint: tau = C / lambda = 9.07 / 1.236 = 7.34 years.)
4. ______________________________  (hint: After 10 years: T = 3 x (1 - exp(-10 / 7.34)) = 3 x (1 - 0.256) = 2.23 K. T...)
5. ______________________________  (hint: Final warming F / lambda = 3.00 K. Energy check: heat stored C x T equals t...)

Final answer: ____________________

## Questions
**A. Conceptual.** When CO2 stops rising, why does the Earth keep warming for a while? Use the energy imbalance N in your answer.

Answer: ______________________________________________


**B. Numerical.** With a 100 m ocean layer and ECS = 3 K, find C and tau. What share of the final warming is reached after one tau?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the scenario figure, why does the ECS 4.5 K curve take longer to settle after year 70 than the Planck-only curve? Read the approximate times.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose a CO2 ceiling (ppm) so that the equilibrium warming stays at or below 2 K for ECS = 2.5, 3 and 4 K. Which ceiling is safe for all three? Compare with about 420 ppm today.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
