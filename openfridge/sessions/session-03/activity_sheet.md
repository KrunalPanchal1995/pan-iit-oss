# Activity sheet: openfridge, Session 3: A vapour-compression cycle, validated, and the energy bill

Name: ____________________   Date: ____________

**Objectives**

- Compute the four states of a simplified vapour-compression cycle and read them on a P-h diagram.
- Include a compressor efficiency and find the COP from enthalpies.
- Validate the model: energy balance, an isentropic check and the Carnot bound.
- Measure the sensitivity of the COP to the condenser temperature and estimate a yearly energy bill including door openings.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Evaporator at -8 C, condenser at 35 C, compressor efficiency 0.7. Find the pressures, the work, the heat taken per kilogram and the COP, and check the energy balance.

1. ______________________________  (hint: Pressures: P_evap = 2.08 bar and P_cond = 10.10 bar, so the pressure r...)
2. ______________________________  (hint: h_1 = 0.8 x (-8) + 300 = 293.6 kJ/kg and h_3 = 0.8 x 35 = 28.0 kJ/kg, ...)
3. ______________________________  (hint: q_evap = h_1 - h_4 = 293.6 - 28.0 = 265.6 kJ/kg....)
4. ______________________________  (hint: T_2s = 265.15 x 4.85^0.125 = 265.15 x 1.218 = 323.0 K, which is 49.8 C...)
5. ______________________________  (hint: Real work = 46.3 / 0.7 = 66.1 kJ/kg, so COP = 265.6 / 66.1 = 4.02....)
6. ______________________________  (hint: q_cond = h_2 - h_3 = 359.7 - 28.0 = 331.7 kJ/kg, and q_evap + work = 2...)
7. ______________________________  (hint: Carnot between -8 C and 35 C: 265.15 / 43 = 6.17, and 4.02 is below it...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the COP of the cycle fall when the condenser temperature rises, even though nothing else changes? Why is the cycle COP always below the Carnot COP?

Answer: ______________________________________________


**B. Numerical.** For the cycle in the worked example, find the COP if the compressor efficiency is 0.5 instead of 0.7. Show how the result follows from the isentropic work.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the COP graph (evaporator -8 C, eta_c = 0.7) read the COP at condenser temperatures of 25 C and 45 C. How large is the fall, and how far below the Carnot line is the cycle?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with capacity 150 W, UA = 3.0 W/K, 4 C inside, 30 door openings a day and compressor efficiency 0.7, find the warmest whole-degree kitchen for which the compressor runs at most 60 percent of the time. Then say what happens at 34 C and what you could change.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
