# Activity sheet: openheatpump, Session 3: Simulate a winter hour by hour

Name: ____________________   Date: ____________

**Objectives**

- Model a house as one thermal capacity (an RC model) and step it hourly with an exact exponential update.
- Build a COP that depends on outdoor and supply temperature, with a defrost derate, a falling capacity and a backup heater.
- Validate the program against energy conservation, an exact cooling curve and a steady-state hand calculation.
- Run sensitivity tests (UA, supply temperature, tariff) and a failure case: an undersized heat pump on the coldest night.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The house (UA = 0.20 kW/K) is held at 20 C while it is 0 C outdoors for a long time. The supply temperature is 35 C. Find the heat needed, the COP including the defrost derate, and the electric power, and compare with the simulation.

1. ______________________________  (hint: Heat needed: Q = 0.20 x (20 - 0) = 4.00 kW....)
2. ______________________________  (hint: Carnot COP = 308.15 / 35 = 8.80; with eta = 0.45 the COP is 3.962....)
3. ______________________________  (hint: It is below 2 C outdoors, so the defrost factor 0.9 applies: COP = 3.9...)
4. ______________________________  (hint: Electric power W = 4.00 / 3.566 = 1.122 kW....)
5. ______________________________  (hint: The simulation at constant 0 C (300 hours) gives 1.1218 kW in the last...)
6. ______________________________  (hint: Season (seeded winter, a heat pump rated 9.09 kW sized for -10 C): the...)

Final answer: ____________________

## Questions
**A. Conceptual.** On a single very cold night a house with a large heat capacity needs less backup heat than a lightweight house with the same UA. Explain why, and say why it does not help in a long cold spell.

Answer: ______________________________________________


**B. Numerical.** If the heating fails completely while it is 0 C outdoors, UA = 0.20 kW/K and C = 4.0 kWh/K, how long does the house take to cool from 20 C to 15 C?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the figure, the 5 kW heat pump with backup shows the backup heater switching on in the coldest hours. Estimate the capacity of the 5 kW pump at -11 C and the backup power needed, if the house loss at that temperature is 6.2 kW.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a poorly insulated house has UA = 0.30 kW/K, 20 C set point, 45 C supply, design temperature -10 C, and a 9 kW backup. Choose a rated capacity: compare the design-temperature size with 10 kW and 8 kW using the seeded winter.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
