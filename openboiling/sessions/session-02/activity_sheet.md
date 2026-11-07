# Activity sheet: openboiling, Session 2: Energy to boil, heat flux and the limits of a heater

Name: ____________________   Date: ____________

**Objectives**

- Compute the power and heating time for a given mass and temperature rise with Q = m cp dT + m L.
- Use q = eta P / A and the empirical scaling q proportional to dT cubed to find the wall superheat of a heater.
- Estimate the critical heat flux and the bubble departure size, and say how reliable these estimates are.
- Solve an inverse design problem: the smallest heater area that keeps a safety factor on the critical heat flux.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Design a kettle element: 1.7 kg of water from 20 C to 100 C in 240 s, element area 100 cm2 (0.01 m2), efficiency 0.85. Find the power, the heat flux, the wall superheat and the safety factor on the CHF (1.1 MW/m2).

1. ______________________________  (hint: Energy: Q = 1.7 * 4186 * 80 = 569 296 J (569.3 kJ)....)
2. ______________________________  (hint: Power: P = Q / (eta t) = 569 296 / (0.85 * 240) = 2791 W....)
3. ______________________________  (hint: Heat flux: q = 0.85 * 2791 / 0.01 = 237 207 W/m2 = 237 kW/m2....)
4. ______________________________  (hint: Superheat: dT = (q / C)^(1/3) = (237 207 / 40.74)^(1/3) = 5822^(1/3) =...)
5. ______________________________  (hint: Safety factor: 1.1e6 / 237 207 = 4.6. For a factor of 3 the area could...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the heat transfer coefficient h = q / dT increase with the heat flux in nucleate boiling, whereas in natural convection it is roughly constant?

Answer: ______________________________________________


**B. Numerical.** With the illustrative C = 40.74 W/(m2 K3), the flux at 10 K is 40.7 kW/m2. What is it at 15 K? By what factor does the flux grow when the superheat grows by half?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** Using the q versus superheat graph, at about what superheat does the flux reach half of the critical heat flux (550 kW/m2)? What does that mean for the wall temperature?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a 3000 W element must give a safety factor of at least 3 on the CHF and keep the wall below 125 C. What is the smallest area? How long does it take to boil 1.7 kg from 20 C?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
