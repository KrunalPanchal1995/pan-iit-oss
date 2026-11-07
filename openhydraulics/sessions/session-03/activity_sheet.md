# Activity sheet: openhydraulics, Session 3: Simulate a hydraulic lift

Name: ____________________   Date: ____________

**Objectives**

- Build a time-stepping model of a pump, cylinder, relief valve, leakage, friction and compressible oil.
- Validate it against the exact lift speed v = Q / A, an energy balance and a plateau-pressure formula.
- Measure how leakage and oil temperature change the lift.
- Explain what happens when the load is too heavy for the relief valve setting.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 1200 kg car sits on a 50 mm ram. The pump delivers 6 L/min (1e-4 m^3/s), new seals leak with c = 3e-13 m^3/(s Pa) at 40 C, seal friction is c_f = 10 000 N s/m and the relief valve is set to 80 bar. Find the pressure the load needs, the ideal lift speed, the speed with leakage and friction, and what the 6 s simulation gives for the lift and the energy.

1. ______________________________  (hint: Ram area A = pi * 0.050^2 / 4 = 1.9635e-3 m^2. Load pressure = m g / A...)
2. ______________________________  (hint: Ideal speed v = Q / A = 1e-4 / 1.9635e-3 = 0.05093 m/s = 50.93 mm/s, s...)
3. ______________________________  (hint: Leakage flow at the load pressure: c p = 3e-13 * 5.996e6 = 1.8e-6 m^3/...)
4. ______________________________  (hint: Speed with leakage and friction: v = (1e-4 - 3e-13 * 11 772 / 1.9635e-...)
5. ______________________________  (hint: The simulation lifts the car 29.7 cm in 6 s (the oil first has to be s...)
6. ______________________________  (hint: Energy: the pump puts in 3733 J; lifted energy m g x = 3493 J (93.6 pe...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a lift with worn seals rise more slowly when the oil is hot than when it is cold, even though the pump has not changed?

Answer: ______________________________________________


**B. Numerical.** A 1800 kg load stands on the 50 mm ram. What pressure does it need? Can a relief valve set to 70 bar let the lift work? What is the plateau pressure of that valve with the 6 L/min pump (k_r = Q / (0.1 p_set), c = 3e-13)?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the left graph, the worn-seal curve at 80 C is a straight line at a lower slope. What is that slope in cm/s, and what would the slope of the ideal line be?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with worn seals (wear 10) and hot oil (80 C), choose a pump flow in whole L/min so that the 1200 kg car still rises at least 25 cm in 6 s, with the relief valve at 80 bar. Which flow works and what does it cost in hydraulic power p Q?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
