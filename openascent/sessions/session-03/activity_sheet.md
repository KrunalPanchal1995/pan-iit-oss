# Activity sheet: openascent, Session 3: Fly to orbit with a gravity turn and staging

Name: ____________________   Date: ____________

**Objectives**

- Write the 2D equations of motion of a rocket around a round Earth with thrust, gravity and drag.
- Fly a launch with a vertical rise, a pitch kick, a gravity turn, staging and an upper-stage burn to orbit.
- Find the orbit (perigee and apogee) from position and velocity using energy and angular momentum.
- Validate the simulation: the delta-v budget closes, the rocket equation is recovered, energy is conserved in a coast.
- Find the pitch-kick window and the largest payload the launcher can put in orbit.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Fly the reference launch: kick 3 degrees, payload 1 t, target 200 km. Hand-check the staging time and the orbital speed, then check the simulation's delta-v budget.

1. ______________________________  (hint: Stage 1 burn time: mdot = 1.6 x 10^6 / (290 x 9.80665) = 562.6 kg/s, so t_b...)
2. ______________________________  (hint: Circular speed at 200 km (Session 1): sqrt(3.986 x 10^14 / 6.571 x 10^6) = ...)
3. ______________________________  (hint: The orbit: perigee 199.8 km, apogee 200.2 km, eccentricity below 0.0001. A ...)
4. ______________________________  (hint: Budget: ideal 9801 - gravity 1442 - drag 95 - steering 476 = 7788 m/s, equa...)
5. ______________________________  (hint: Rocket equation for the propellant used (stage 1 all 90 t, stage 2 14.05 t,...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a gravity turn (thrust along the velocity) waste less propellant than pointing the rocket at a fixed angle from the start?

Answer: ______________________________________________


**B. Numerical.** A satellite is in a circular orbit at 400 km instead of 200 km. Find its speed. Then, ignoring losses, how much less sideways speed does it need than at 200 km, and why does it still need more energy to get there?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the pitch-kick window, both 1.5 degrees and 4.5 degrees fail. Using the trajectory and budget views of the app, explain the two different ways they fail.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the customer's satellite is 2000 kg. Using the model, choose the pitch kick, and say how much propellant margin is left. Then propose one change to stage 2 (more propellant, or higher Isp) that gives at least 500 kg of propellant margin, and check it in the app or with `launch`.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
