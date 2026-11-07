# Activity sheet: opendronecontrol, Session 3: Tilt to move: attitude control and cascaded PID

Name: ____________________   Date: ____________

**Objectives**

- Write the equations of a planar quadrotor and use a mixer to turn a thrust and a torque into rotor forces.
- Design the inner attitude loop with the second-order formulas and explain why it must be faster than the outer position loop.
- Find the motor-lag stability limit tau_m < Kd_att / Kp_att and confirm it in simulation.
- Fly a cascaded controller, validate it against hand calculations and limits, and tune it for a camera drone.

## Before you start: predict
In your own words, what do you think will happen when you slide the motor time constant from 0 to 0.2 s in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The drone (m = 1.2 kg, I = 0.012 kg m^2, L = 0.2 m) uses Kp_att = 1.2 N m/rad and Kd_att = 0.17 N m s/rad. Find the attitude wn, zeta and overshoot, and the motor-lag limit. At the start of a 1 m move with Kp_y = 2.25 1/s^2, find the tilt the outer loop asks for, the first roll torque and the two rotor forces.

1. ______________________________  (hint: Attitude loop: wn = sqrt(1.2 / 0.012) = 10 rad/s; zeta = 0.708....)
2. ______________________________  (hint: Overshoot = exp(-0.708 pi / 0.706) = 0.043....)
3. ______________________________  (hint: Motor-lag limit: tau_m < 0.17 / 1.2 = 0.142 s....)
4. ______________________________  (hint: Wanted tilt: phi_des = 2.25 x 1 / 9.81 = 0.229 rad = 13.1 degrees....)
5. ______________________________  (hint: tau = 0.275 N m; F_l = 6.574 N, F_r = 5.198 N....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why must the inner attitude loop be much faster than the outer position loop? What happens if it is too slow, and what happens if you make it very fast?

Answer: ______________________________________________


**B. Numerical.** For candidate B (Kp_att = 0.432 N m/rad, Kd_att = 0.1008 N m s/rad, I = 0.012 kg m^2) find wn, zeta, the overshoot and the motor-lag limit. Is it safe with 0.06 s motors and a safety factor of 2? With 0.10 s motors?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In Figure 2 (left), describe how the tilt response changes as tau_m goes from 0 to 0.13 s. Why does the motor lag make the tilt overshoot more, even though the gains did not change?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the motors are replaced by cheaper ones with tau_m = 0.10 s. Choose Kp_att and Kd_att so that the 1 m move settles within 4 s, the tilt stays at or below 15 degrees, and the lag limit has a safety factor of 2. Justify your choice and state the trade-off.

Answer: ______________________________________________

## Mini-project
Tune the attitude loop of a camera drone: compare candidates A to D with `check_design` and recommend one.

Recommendation and reason: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
