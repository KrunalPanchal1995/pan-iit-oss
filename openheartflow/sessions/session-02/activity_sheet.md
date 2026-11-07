# Activity sheet: openheartflow, Session 2: Resistance, cardiac output and mean pressure

Name: ____________________   Date: ____________

**Objectives**

- Use Poiseuille's law to compute the resistance of a vessel and show that half the radius means 16 times the resistance.
- Compute cardiac output from heart rate and stroke volume and convert units (mmHg, mL, L/min).
- Use MAP = CO x TPR to predict how the mean pressure responds to heart rate, stroke volume and vessel radius.
- Solve a design problem with constraints and state its assumptions.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A vessel 0.10 m long has radius 1.0 mm; blood has mu = 3.5e-3 Pa s. Find its resistance in mmHg per (mL/s), the flow for a push of 10 mmHg, and the same for radius 0.5 mm. Then: at a constant 5 L/min with TPR = 18.6, what happens to MAP if the resistance rises by 20 percent, and what radius change causes such a rise?

1. ______________________________  (hint: R = 8 mu L / (pi r^4) = 8 x 3.5e-3 x 0.10 / (pi x (1.0e-3)^4) = 2.8e-3...)
2. ______________________________  (hint: Convert: x 1e-6 (m^3 to mL) / 133.322 (Pa per mmHg) = 6.685 mmHg per (...)
3. ______________________________  (hint: Flow for 10 mmHg: 10 / 6.685 = 1.496 mL/s....)
4. ______________________________  (hint: Radius 0.5 mm: R is 16 times larger = 106.96 mmHg per (mL/s); the flow...)
5. ______________________________  (hint: TPR rises by 20 percent: 18.6 x 1.2 = 22.32. At constant 5 L/min, MAP ...)
6. ______________________________  (hint: The radius ratio k that gives resistance x1.2 satisfies k^-4 = 1.2, so...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the resistance depend on the radius to the fourth power and not just on the cross-section area (radius squared)?

Answer: ______________________________________________


**B. Numerical.** A heart beats 80 times per minute with a stroke volume of 60 mL. Find the cardiac output, and the MAP for a TPR of 18.6 mmHg per (L/min). Check the units.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the graph of MAP against radius at 5 L/min, read the MAP at radius 0.9 and 1.1 of normal. Why are the two changes from 93 not equal?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the vessels are 5 percent narrower (radius 0.95 of normal) and the mean arterial pressure must stay at or below 100 mmHg. Find the largest cardiac output and choose a heart rate and stroke volume. State the trade-offs.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
