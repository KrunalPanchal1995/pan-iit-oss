# Activity sheet: opensolarbattery, Session 3: A whole year: reliability and the cost-optimal size

Name: ____________________   Date: ____________

**Objectives**

- Simulate 8760 hours with seasonal sunshine, seeded random cloudiness and a year of demand.
- Measure reliability and loss-of-load hours, and test the simulator against exact energy rules.
- Run sensitivity tests on cloudiness, demand and the random seed.
- Search designs for the cheapest one that meets a reliability target and read the Pareto front.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Part 1 (analytic reference). Check the hourly clear-sky model against the exact formula A x 2D / pi summed over the year. Part 2. Find the cost-optimal design for R at least 0.9 with cloudiness 0.5, seed 1, demand 10 kWh per day on average (3642 kWh in the simulated year), and check how robust it is.

1. ______________________________  (hint: Sum over the 365 days of A(d) x 2D(d) / pi: 2399 kWh per kW. The hourl...)
2. ______________________________  (hint: With clouds (cloudiness 0.5, seed 1) the year gives 1936 kWh per kW: m...)
3. ______________________________  (hint: Check the energy conservation: solar + import - (demand + export + cha...)
4. ______________________________  (hint: Search 20 array sizes (0.5 to 10 kW) x 25 battery sizes (0 to 24 kWh) ...)
5. ______________________________  (hint: Robustness: run the same design on 100 other random years. It reaches ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does increasing the battery capacity not necessarily solve every problem caused by an undersized solar array?

Answer: ______________________________________________


**B. Numerical.** A 4 kW array and an 8 kWh battery give reliability 0.977 for a home with 3642 kWh of demand in the simulated year. How much energy did the home import? If the demand is 30 percent higher, reliability falls to 0.901: how many more kWh were imported?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the sensitivity results for the 4 kW / 8 kWh design, reliability is 0.982 at cloudiness 0, 0.977 at 0.5, 0.956 at 0.75 and 0.897 at 1.0. What do the loss-of-load hours (188, 218, 477, 1028) add?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose the array and battery for 95 percent reliability and justify your choice against the Pareto front. Would you pick the single-year optimum or something larger?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
