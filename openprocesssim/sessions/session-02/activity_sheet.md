# Activity sheet: openprocesssim, Session 2: Streams, blocks and the flash: the numbers inside the boxes

Name: ____________________   Date: ____________

**Objectives**

- Define a stream object (component flows, T, P, phase) and write mixer, splitter, heater, pump and valve as functions.
- Compute vapour pressures with the Antoine equation and K-values with Raoult's law.
- Find bubble and dew points by root-finding and check them against the boiling points of pure liquids.
- Solve the Rachford-Rice equation for the vapour fraction, check mass balance closure and the limits V = 0 and V = 1, and solve a design problem for the flash temperature.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
An equimolar benzene-toluene feed (z = 0.5 each) at 1 atm (101.325 kPa) is flashed at 368 K. Find K-values, V, and the liquid and vapour compositions.

1. ______________________________  (hint: Antoine at 368 K: P_sat is 156.2 kPa for benzene and 63.3 kPa for tolu...)
2. ______________________________  (hint: K = P_sat / P: K_benzene = 156.2 / 101.325 = 1.542 and K_toluene = 63....)
3. ______________________________  (hint: Rachford-Rice: f(V) = 0.5 * 0.542 / (1 + 0.542 V) + 0.5 * (-0.3755) / ...)
4. ______________________________  (hint: Liquid: x_benzene = 0.5 / (1 + 0.409 * 0.542) = 0.409. Vapour: y_benze...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can a mixture not boil at a single temperature, as a pure liquid does?

Answer: ______________________________________________


**B. Numerical.** (a) How much heat does heating 100 mol/s of the equimolar liquid from 300 K to 350 K take? (b) What shaft power does a pump with 70 percent efficiency need to raise it by 400 kPa (molar volume 1e-4 m3/mol)? (c) What is the temperature after mixing 60 mol/s benzene at 300 K with 40 mol/s toluene at 340 K?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the flash curve and T-x-y diagram: what is the highest benzene fraction any single flash of the equimolar feed can give in the vapour, and what temperature gives 50 percent vapour?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a flash of the equimolar feed at 1 atm must vaporise at least 30 percent of the feed and give a vapour with at least 0.65 benzene. Find the temperature window and say what a control engineer would worry about.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
