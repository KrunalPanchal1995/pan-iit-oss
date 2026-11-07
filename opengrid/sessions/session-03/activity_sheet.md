# Activity sheet: opengrid, Session 3: After a power station trips: frequency, inertia and droop

Name: ____________________   Date: ____________

**Objectives**

- State the swing equation in per unit with inertia constant H, damping D and governor droop R.
- Solve it with your own RK4 and validate the start slope and the final value with hand formulas.
- Compare the frequency with and without governor response and with different inertia.
- Solve a three-bus DC power flow and check power balance; find a battery size for a nadir target.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 5 percent loss hits a grid with H = 5 s, D = 1 and droop R = 0.05. Find the initial RoCoF and the settled frequency by hand, then compare with the RK4 simulation.

1. ______________________________  (hint: Initial RoCoF = -f0 dP / (2H) = -50 * 0.05 / (2 * 5) = -0.250 Hz/s....)
2. ______________________________  (hint: Stiffness 1/R + D = 20 + 1 = 21....)
3. ______________________________  (hint: Final deviation = -50 * 0.05 / 21 = -0.119 Hz, so the settled frequenc...)
4. ______________________________  (hint: Without a governor the final deviation is -50 * 0.05 / 1 = -2.5 Hz, so...)
5. ______________________________  (hint: The RK4 simulation gives a start slope of about -0.249 Hz/s, a settled...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a grid with a lot of solar and wind (little spinning mass) see a faster and deeper frequency fall after the same loss?

Answer: ______________________________________________


**B. Numerical.** An 8 percent loss hits a grid with H = 4 s. Find the initial RoCoF. Then for a 5 percent loss with droop R = 0.04 and D = 1, find the settled frequency.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the inertia figure (10 percent loss), compare the initial slopes for H = 2 s and H = 5 s, and say which curve crosses 49 Hz.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: after an 8 percent loss on a grid with H = 3 s the nadir must stay at or above 49.5 Hz. The nadir with no battery is 49.266 Hz. Find the smallest fast battery (in steps of 0.005 pu), and discuss what else could achieve it.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
