# Activity sheet: openpipeflow, Session 2: Friction loss, Reynolds number and pump power

Name: ____________________   Date: ____________

**Objectives**

- Compute the Reynolds number and say whether the flow is laminar or turbulent.
- Find the friction factor (64/Re when laminar, Swamee-Jain when turbulent) and the Darcy-Weisbach head loss.
- Add minor losses and the static lift to get the pump head, and convert it to electric power.
- Solve the design problem: the smallest standard diameter within a power budget and a speed limit.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Water at 20 L/s goes through 500 m of 125 mm pipe (roughness 0.15 mm, K = 5) to a tank 10 m higher. The pump and motor are 65 percent efficient. Find the electric power.

1. ______________________________  (hint: Q = 0.020 m^3/s, D = 0.125 m. v = 4(0.020) / (pi (0.125)^2) = 1.630 m/...)
2. ______________________________  (hint: Re = v D / nu = 1.630 x 0.125 / 1.0e-6 = 203 700, which is turbulent. ...)
3. ______________________________  (hint: Swamee-Jain: log10(0.0012 / 3.7 + 5.74 / 203 700^0.9) = log10(0.000324...)
4. ______________________________  (hint: Friction loss h_f = 0.0219 x (500 / 0.125) x 0.1354 = 11.87 m. Minor l...)
5. ______________________________  (hint: Pump head H = 10 + 11.87 + 0.68 = 22.55 m. Water power = 998 x 9.81 x ...)
6. ______________________________  (hint: Electric power = 4415 / 0.65 = 6793 W, about 6.79 kW: just inside the ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does doubling the pipe diameter reduce the friction loss by much more than a factor of two for the same flow rate?

Answer: ______________________________________________


**B. Numerical.** 12 L/s of water flows through 200 m of 100 mm pipe of roughness 0.15 mm. Find the speed, Reynolds number, friction factor, head loss and the power lost to friction (no minor losses).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** Read the power-against-diameter curve for 20 L/s, 500 m, 10 m lift. About what power is needed at 100 mm, 125 mm and 200 mm, and what limits the curve for large diameters?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the same job (20 L/s, 500 m, 10 m lift, K = 5, roughness 0.15 mm, 65 percent efficient) but a smaller budget of 5 kW. Choose a standard size from 100, 125, 150, 200 mm. What if the budget were 4 kW? Justify with speed and trade-offs.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
