# Activity sheet: openairfoil, Session 1: Lift, drag and the pressure around a wing

Name: ____________________   Date: ____________

**Objectives**

- Compute dynamic pressure, lift and drag from L = q S CL and D = q S CD.
- Find the lift coefficient a wing needs for level flight, and the stall speed.
- Explain why thrust = drag = weight / (L/D), and turn drag into fuel energy per kilometre.
- Use Bernoulli's equation and the pressure coefficient to explain where lift comes from.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 1000 kg aircraft with a 16 m2 wing cruises at 50 m/s at sea level. Find the dynamic pressure, the CL it needs and its stall speed for CL_max = 1.4. With CD = 0.03, find the drag, L/D and the fuel energy per kilometre for an engine-and-propeller efficiency of 0.25. Finally find CL for a toy wing with air 1.2 times faster than V_inf on top and 0.95 times underneath.

1. ______________________________  (hint: q = 0.5 x 1.225 x 50^2 = 1531.25 Pa.)
2. ______________________________  (hint: Weight = 1000 x 9.81 = 9810 N, so CL = 9810 / (1531.25 x 16) = 9810 / 24500...)
3. ______________________________  (hint: Stall speed = sqrt(2 x 9810 / (1.225 x 16 x 1.4)) = sqrt(19620 / 27.44) = s...)
4. ______________________________  (hint: Drag = 1531.25 x 16 x 0.03 = 735 N; L/D = 0.4004 / 0.03 = 13.35 (check: 981...)
5. ______________________________  (hint: Fuel energy per km = 735 N x 1000 m / 0.25 = 2.94 x 10^6 J = 2.94 MJ.)
6. ______________________________  (hint: Toy wing: Cp_upper = 1 - 1.2^2 = -0.44, Cp_lower = 1 - 0.95^2 = 0.0975, CL ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a slow aircraft have to fly with its nose higher (a larger angle of attack) than a fast one, and why can it not fly slower than the stall speed?

Answer: ______________________________________________


**B. Numerical.** A wing of 12 m2 flies at 60 m/s at sea level with CL = 0.5. Find q and the lift. Can it hold up a 1200 kg aircraft? Check the units.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the lift-against-speed figure, read the lift at CL = 0.6 at 40 m/s and at 80 m/s. By what factor does it grow, and why is the curve not a straight line?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose the wing area of a 1000 kg aircraft so that it stalls at no more than 25 m/s with flaps giving CL_max = 1.5. What CL will it then need in a 50 m/s cruise, and why would a designer not simply make the wing much bigger?

Answer: ______________________________________________


## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
