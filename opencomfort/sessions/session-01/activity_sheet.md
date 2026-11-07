# Activity sheet: opencomfort, Session 1: Where the heat in a hot room comes from

Name: ____________________   Date: ____________

**Objectives**

- List the four ways heat enters or leaves a room: through walls and roof, sunshine through glass, people and lamps, and air flow.
- Compute each one in watts: Q = U A dT, Q = (1 - s) SHGC A I, and Q = rho cp V_dot dT.
- Find the steady indoor temperature where heat in equals heat out.
- Explain why shading and ventilation are the two cheapest levers for keeping a room cool.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The example room (UA = 70 W/K, 48 m3, 250 W of internal gains) has 500 W/m2 of sun on its 2 m2 window (SHGC 0.8) at 34 C outside. A shade blocks 80 percent of the sun and the windows give 10 air changes per hour. Find the steady indoor temperature and check the energy balance.

1. ______________________________  (hint: Sun gain: Q_sun = (1 - 0.8) x 0.8 x 2 x 500 = 160 W....)
2. ______________________________  (hint: Air flow: V_dot = 10 x 48 / 3600 = 0.1333 m3/s, so H_v = 1200 x 0.1333 = 16...)
3. ______________________________  (hint: Steady temperature: T_in = 34 + (160 + 250) / (70 + 160) = 34 + 410 / 230 =...)
4. ______________________________  (hint: Check: walls and roof carry 70 x 1.78 = 125 W out, air carries 160 x 1.78 =...)
5. ______________________________  (hint: Without shade or air flow (0.5 ACH from leaks, H_v = 8 W/K): T_in = 34 + 10...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a shade work much better outside the window than a curtain inside it?

Answer: ______________________________________________


**B. Numerical.** A 1.5 m2 clear window (SHGC 0.8) receives 600 W/m2. How much heat enters with no shade and with a shade blocking 70 percent? Check the units.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the second figure, why do both curves flatten as the air change rate grows, and what temperature do they approach?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the example room must stay within 2 K of outdoor at 34 C with 500 W/m2 on the window. Find the minimum air changes per hour with no shade and with an 80 percent shade. Which is more realistic to achieve?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
