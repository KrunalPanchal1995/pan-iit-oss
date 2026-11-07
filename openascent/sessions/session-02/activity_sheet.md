# Activity sheet: openascent, Session 2: Straight up: gravity and drag losses

Name: ____________________   Date: ____________

**Objectives**

- Compute the thrust-to-weight ratio and the propellant mass flow, and say whether a rocket can lift off.
- Derive the burnout speed of a vertical burn, v = ve ln(m0 / mf) - g t_b, and name g t_b the gravity loss.
- Step a rocket flight forward in time with Euler and with Runge-Kutta 4, and check both against the exact answer.
- Add drag and inverse-square gravity, and explain why flying straight up never gives an orbit.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A single-stage rocket has m0 = 100 t, 75 t of propellant, Isp = 300 s and thrust F = 1.5 MN. It flies straight up with constant g0 and no air. Find the TWR, the burn time, the burnout speed and height, the gravity loss and the highest point.

1. ______________________________  (hint: TWR = 1.5 x 10^6 / (100 000 x 9.80665) = 1.53. Above 1, so it lifts off....)
2. ______________________________  (hint: ve = 300 x 9.80665 = 2942 m/s; mdot = 1.5 x 10^6 / 2942 = 509.9 kg/s; t_b =...)
3. ______________________________  (hint: Burnout speed: v = 2942 ln(100 / 25) - 9.80665 x 147.1 = 4078 - 1443 = 2636...)
4. ______________________________  (hint: Burnout height: h = 2942 x 147.1 - 2942 x (25 000 / 509.9) x 1.386 - 0.5 x ...)
5. ______________________________  (hint: Coast: extra height = 2636^2 / (2 x 9.80665) = 354.2 km, so the top is 126....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a rocket with a thrust-to-weight ratio of 1.1 waste so much propellant, even though it does lift off?

Answer: ______________________________________________


**B. Numerical.** The same 100 t rocket (75 t propellant, Isp 300 s) now has a 2.0 MN engine. Find the TWR, the burn time, the gravity loss and the burnout speed (constant g, no air).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the left panel, Euler with 10 s steps ends below the exact curve, and the gap grows with time. Why is Euler always low here, and what happens to its error if you halve dt?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose the smallest thrust for the 100 t stage (75 t propellant, Isp 300 s) that keeps the gravity loss below 1000 m/s. Lift-off TWR must also stay at or below 2.5 (load limit). Is there a design that meets both? Then switch on drag in the app: what new cost appears as TWR rises?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
