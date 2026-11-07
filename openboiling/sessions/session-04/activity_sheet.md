# Activity sheet: openboiling, Session 4: The boiling curve from fluid properties, and what pressure does to it

Name: ____________________   Date: ____________

**Objectives**

- Compute the properties of saturated water at any pressure from 0.5 to 20 bar by interpolating a steam table, and check the interpolation against independent values.
- Build a boiling curve from correlations: Rohsenow for nucleate boiling, Zuber for the critical heat flux (CHF), Berenson for the minimum flux and film boiling.
- Explain why the CHF rises with pressure although the latent heat falls, using the three factors of Zuber's formula.
- Say how large the uncertainty of each correlation is, and which parts of the curve are only a shape.
- Use the curve to size the heat flux of a heater at several pressures and to test it for burnout.

## Before you start: predict
In your own words, what do you think happens to the critical heat flux when the pressure goes up from 1 atm to 5 bar?

______________________________________________________________

## Worked example (fill in as you go)
A heater surface carries 1300 kW/m2 in saturated water. (a) Find the CHF at 1 atm and at 5 bar by hand from the steam table. (b) Is the heater safe at each pressure? (c) At 5 bar, what are the wall superheat and the wall temperature?

1. ______________________________  (hint: Zuber, 1 atm: rho_v = 0.59762, h_fg = 2.2565e6, sigma = 0.058917, rho_l = 958.37)
2. ______________________________  (hint: q = 0.131 h_fg sqrt(rho_v) (sigma g (rho_l - rho_v))^(1/4))
3. ______________________________  (hint: the same at 5 bar: rho_v = 2.6681, h_fg = 2.1079e6, sigma = 0.048349, rho_l = 915.28)
4. ______________________________  (hint: compare 1300 kW/m2 with each CHF)
5. ______________________________  (hint: Rohsenow at 5 bar, C = 427.9 W/(m2 K3), dT = (q / C)^(1/3))

Final answer: ____________________

## Questions
**A. Conceptual.** The latent heat of water falls as the pressure rises, yet the critical heat flux rises. Explain, using the three factors of Zuber's formula.

Answer: ______________________________________________


**B. Numerical.** Compute the CHF at 2 bar by hand from the table row (rho_l = 942.94, rho_v = 1.129, h_fg = 2.2016e6, sigma = 0.054926) and its ratio to the value at 1 atm.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the second figure, the wall superheat needed for 500 kW/m2 at 1 atm is about 9.4 K for Csf = 0.008, 15.3 K for 0.013 and 23.5 K for 0.02. What does this say about predicting the wall temperature, compared with predicting the CHF?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a heater of 0.02 m2 must deliver 24 kW in water with a flux of at most 60 percent of the CHF. Among the pressures 0.5, 1 atm, 2, 5 and 10 bar, which is the lowest that works, and what is the wall temperature? What is the exact lowest pressure?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
