# Activity sheet: openfridge, Session 2: COP, the Carnot limit and sizing a fridge for a heat leak

Name: ____________________   Date: ____________

**Objectives**

- Convert temperatures to kelvin and compute the Carnot COP T_c / (T_h - T_c).
- Compute the compressor power and the heat given to the kitchen for a given heat leak.
- Explain why a hotter kitchen or a colder inside lowers the COP.
- Solve the inverse problem: which kitchen temperature or efficiency fraction meets a power limit?

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A fridge holds 4 C in a 25 C kitchen. The heat leak is 60 W and eta2 = 0.25. Find the Carnot COP, the real COP, the compressor power and the heat given to the kitchen.

1. ______________________________  (hint: Convert: T_c = 4 + 273.15 = 277.15 K and T_h = 25 + 273.15 = 298.15 K,...)
2. ______________________________  (hint: COP_Carnot = 277.15 / 21 = 13.20....)
3. ______________________________  (hint: COP = 0.25 x 13.20 = 3.30....)
4. ______________________________  (hint: W = Q_cold / COP = 60 / 3.30 = 18.2 W....)
5. ______________________________  (hint: Q_hot = 60 + 18.2 = 78.2 W. Check: Q_hot / W is 4.3 = COP + 1....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can no fridge have a COP above the Carnot value? And why does a freezer at -18 C have a lower Carnot COP than a fridge at 4 C in the same kitchen?

Answer: ______________________________________________


**B. Numerical.** A fridge holds 5 C in a 30 C kitchen with a 40 W heat leak and eta2 = 0.30. Find the Carnot COP, the real COP, the compressor power and Q_hot.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the COP graph for a 4 C inside, estimate by what fraction the Carnot COP falls when the kitchen goes from 25 C to 35 C. Confirm with the formula.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the heat leak is 60 W, the inside is 4 C and the compressor power must not exceed 15 W. Find the warmest kitchen allowed if eta2 = 0.30. Then, for a 32 C kitchen, find the least eta2 that meets the limit. State the trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
