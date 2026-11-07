# Activity sheet: openengine, Session 4: Temperature-dependent gas properties

Name: ____________________   Date: ____________

**Objectives**

- Compute cp, cv and gamma of air at any temperature from a published NASA polynomial.
- Follow the Otto cycle with variable cp using u(T) for the heats and an entropy function for the isentropes.
- Validate the model: it must give back the Session 2 formula when the properties are constant, and its P-V loop area must equal the net heat.
- Explain why more heat (a hotter cycle) lowers the ideal efficiency, and how much of the gap to real engines this explains.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
An ideal Otto cycle with r = 9, T1 = 300 K and q_in = 1100 kJ/kg (the Session 2 example), but with cp(T) of air from the NASA polynomial. Find T2, T3, T4, the efficiency and the effective gamma, and check the first law.

1. ______________________________  (hint: Compression: phi(300 K) = 5.0787 kJ/(kg K) and R ln 9 = 0.287 x 2.1972 = 0.6306,...)
2. ______________________________  (hint: Heat at constant volume: u(T2) = 215.4 kJ/kg, so u(T3) = 215.4 + 1100 = 1315.4 k...)
3. ______________________________  (hint: Expansion: phi(T4) = phi(T3) - 0.6306, so T4 = 964 K (constant gamma gave 937 K)...)
4. ______________________________  (hint: Rejected heat: q_out = u(964 K) - u(300 K) = 432.4 - (-84.2) = 516.6 kJ/kg (cons...)
5. ______________________________  (hint: Effective gamma = 1 + ln(1 / 0.470) / ln 9 = 1.344, between gamma(T3) = 1.298 an...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does adding more heat per cycle lower the ideal Otto efficiency once cp depends on temperature, while in Session 2 the efficiency did not depend on the heat at all?

Answer: ______________________________________________


**B. Numerical.** Using `cp_air`, find cp, cv and gamma of air at 1500 K. Then estimate the Otto efficiency at r = 9 if you used that single gamma for the whole cycle. Is it above or below the variable-cp answer of 0.530, and why?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the left panel of the efficiency figure, the variable-cp curve approaches a value near the constant-gamma line as the heat input goes to zero, but not exactly 0.585. Explain why it starts there and why it does not quite reach 0.585.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with Session 2's constant gamma, r = 9.88 gives an ideal efficiency of 0.60. With variable cp and q_in = 1100 kJ/kg, what compression ratio is needed for 0.60, and what is T2? If the fuel knocks above an end-of-compression temperature of about 750 K (an illustrative number), is this design possible? What would you trade?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
