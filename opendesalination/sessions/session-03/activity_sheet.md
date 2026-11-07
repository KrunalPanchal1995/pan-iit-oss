# Activity sheet: opendesalination, Session 3: Simulate a membrane module and validate it

Name: ____________________   Date: ____________

**Objectives**

- Write the water and salt flux laws of a reverse osmosis membrane and explain concentration polarisation.
- March along a membrane with Runge-Kutta 4 and get recovery, brine salt and fresh-water salt.
- Validate the simulation against a closed-form answer, the salt balance and the Session 2 limits.
- Count the real energy (pump and ERD) and choose a feed pressure that meets recovery and water-quality limits.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
One vessel at P = 6000 kPa takes Qf = 12 m3/h of 35 g/L seawater (pi_f = 2969 kPa, A = 1e-5 m3/(m2 h kPa), B = 0, CP = 1). How much membrane gives 30 percent recovery? Check the simulation, find the brine salt and the energy with an 80 percent pump and a 95 percent ERD.

1. ______________________________  (hint: Flows: Qp = 0.3 x 12 = 3.6 m3/h, Qb = 12 - 3.6 = 8.4 m3/h. Constant k = pi_...)
2. ______________________________  (hint: Closed form: (Qf - Q) / P = 3.6 / 6000 = 0.000600; ln((6000 x 12 - 35 630) ...)
3. ______________________________  (hint: RK4 march over 149.2 m2 in 400 steps gives recovery 0.300000 (difference be...)
4. ______________________________  (hint: Energy: pump 6000 x 12 / 0.8 = 90 000 kJ/h; ERD returns 0.95 x 6000 x 8.4 =...)
5. ______________________________  (hint: Compare: least work at r = 0.3 is 0.98 kWh/m3; the vessel needs 3.3 times t...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the water flux fall along the membrane, even though the feed pressure is the same everywhere?

Answer: ______________________________________________


**B. Numerical.** At the inlet of a vessel at 6000 kPa with 35 g/L feed and CP = 1.1, find the water flux in L per m2 per hour. What is it at the outlet if the brine there is 56 g/L?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the energy ladder, which step costs the most energy, and which is a choice rather than a law of physics?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with the mini-project vessel, compare a pump of 80 percent and one of 85 percent at P = 6750 kPa. How much energy does the better pump save, and how much power is that for a 100 MLD (100 000 m3/day) plant?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
