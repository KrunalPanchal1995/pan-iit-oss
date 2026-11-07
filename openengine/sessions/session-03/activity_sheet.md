# Activity sheet: openengine, Session 3: Simulate the cycle and validate it

Name: ____________________   Date: ____________

**Objectives**

- Step through an ideal cycle numerically and compute work as a sum of P dV.
- Validate the simulation against the formulas and the first law (net work = net heat).
- Add a Wiebe burn, heat loss and friction and measure how much each costs.
- Compare Otto and Diesel fairly (equal r, equal peak pressure) and explain the knock limit.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Simulate the ideal Otto cycle with r = 9 and q_in = 1100 kJ/kg (P1 = 100 kPa, T1 = 300 K). Compare its efficiency with the formula and check the first law.

1. ______________________________  (hint: Compression: integrate dP/dv = -gamma P / v from v1 = 0.861 to v2 = 0....)
2. ______________________________  (hint: Heat at constant volume: add 1100 kJ/kg in 400 equal steps, dP = 0.4 d...)
3. ______________________________  (hint: Sum P dv around the loop: net work = 643.3 kJ/kg; heat rejected = v1 (...)
4. ______________________________  (hint: Efficiency = 643.3 / 1100 = 0.58477; the formula gives 0.58476....)
5. ______________________________  (hint: First law: net work - (q_in - q_out) = 0.02 kJ/kg, about 0.002 percent...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a Diesel win at equal peak pressure although an Otto wins at equal compression ratio?

Answer: ______________________________________________


**B. Numerical.** Find the end-of-compression temperature for r = 10 and r = 9 (T1 = 300 K, gamma = 1.4). A fuel allows T2 up to 740 K with a 20 K margin: is r = 10 acceptable?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the knock-down figure, which single real effect costs the most efficiency, and by how much? Compare the burn time, the heat loss and the friction.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a generator engine uses fuel A (T2 limit 740 K) with a 20 K margin, or fuel B (800 K). Choose r for each in steps of 0.5, find the modelled brake efficiency (10 percent loss, friction 100 kPa) and say which fuel meets a 0.45 target. What r would be needed?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
