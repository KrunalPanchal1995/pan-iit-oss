# Activity sheet: opendcmotor, Session 2: The DC motor model, power, and choosing a gearbox

Name: ____________________   Date: ____________

**Objectives**

- Write the two DC motor equations and derive the torque-speed line from them.
- Verify the line numerically and show why k_t equals k_e in SI units.
- Find the speed of peak power and the efficiency there, with and without friction.
- Choose a gear ratio so that a motor lifts a load at a required speed within a current limit.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For the motor V = 12 V, R = 2.0 ohm, k = 0.05 N m/A: find the stall torque, stall current, no-load speed, peak power and efficiency there. Then choose the best gear ratio for the winch (load torque 0.981 N m, drum speed at least 5 rad/s, current at most 1.5 A, gearbox efficiency 0.9, friction b = 5e-5).

1. ______________________________  (hint: Stall torque = k V / R = 0.05 x 12 / 2 = 0.300 N m; stall current = V ...)
2. ______________________________  (hint: No-load speed = V / k = 12 / 0.05 = 240 rad/s = 2292 rpm....)
3. ______________________________  (hint: Ideal peak power = T_stall x w_noload / 4 = 0.3 x 240 / 4 = 18.00 W at...)
4. ______________________________  (hint: With friction: a = k^2/R + b = 0.00125 + 0.00005 = 0.0013; the shaft l...)
5. ______________________________  (hint: Load: the drum torque is 5 x 9.81 x 0.02 = 0.981 N m. For ratio N the ...)
6. ______________________________  (hint: Scanning ratios 5 to 60: N = 17 to 42 meet drum speed >= 5 rad/s and c...)
7. ______________________________  (hint: Best efficiency in the window: N = 22. Motor torque 0.0496 N m, motor ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is the efficiency at maximum power below 50 percent in a real motor, and why is the best-efficiency speed higher than the best-power speed?

Answer: ______________________________________________


**B. Numerical.** A motor has V = 6 V, R = 1.5 ohm, k = 0.03 N m/A (no friction). Find the stall torque, stall current, no-load speed (rad/s and rpm) and peak mechanical power.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the gear-ratio window graph, what happens to the output speed and to the current as the ratio grows from 17 to 42? Which limit decides the lower end of the window and which the upper end?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: lift a 3 kg load on the same 2 cm drum at a drum speed of at least 8 rad/s with at most 1.5 A. Which ratios work and which would you choose? State the trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
