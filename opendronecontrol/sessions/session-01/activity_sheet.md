# Activity sheet: opendronecontrol, Session 1: Thrust, weight and hover

Name: ____________________   Date: ____________

**Objectives**

- Compute the weight of a drone and the thrust each rotor must give to hover.
- Use the rotor law T = k_T omega^2 to find the hover speed in rad/s and rpm.
- Compute the thrust-to-weight ratio and say why it must be well above 1.
- Use Newton's second law to predict how a drone drifts when the throttle is fixed and the mass is wrong, and explain why this calls for feedback.

## Before you start: predict
In your own words, what do you think will happen when you add a parcel in the live app but leave the rotor speed alone?

______________________________________________________________

## Worked example (fill in as you go)
A 1.2 kg quadrotor has rotors with k_T = 1.0e-5 N/(rad/s)^2 and a top speed of 1000 rad/s. Find its weight, the hover speed in rad/s and rpm, and its thrust-to-weight ratio. Then a 0.2 kg parcel is added with the throttle unchanged: find the acceleration and how long the drone takes to sink 1 m.

1. ______________________________  (hint: Weight: W = 1.2 x 9.81 = 11.772 N, so each rotor carries 2.943 N....)
2. ______________________________  (hint: Hover speed: omega = sqrt(2.943 / 1.0e-5) = 542.5 rad/s = 5180 rpm....)
3. ______________________________  (hint: Top thrust: 4 x 1.0e-5 x 1000^2 = 40 N, thrust-to-weight = 3.40....)
4. ______________________________  (hint: With the parcel: a = 11.772 / 1.4 - 9.81 = -1.40 m/s^2....)
5. ______________________________  (hint: Time to sink 1 m: t = sqrt(2 / 1.40) = 1.19 s....)

Final answer: ____________________

## Questions
**A. Conceptual.** A pilot finds the exact throttle at which the drone hovers, then lets go of the stick. Give three reasons why the drone will still drift up or down after a while.

Answer: ______________________________________________


**B. Numerical.** A smaller 0.9 kg quadrotor uses the same rotors (k_T = 1.0e-5 N/(rad/s)^2, top speed 1000 rad/s). Find the thrust per rotor to hover, the hover speed in rad/s and rpm, and its thrust-to-weight ratio. Check the units and that the answer is reasonable.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the thrust curve, by what factor does the thrust grow when the rotor speed goes from 4000 to 8000 rpm? On the drift graph, the 1.4 kg drone has sunk 2.80 m after 2 s. How far had it sunk after 1 s, and why is that not half?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: you want the 1.2 kg drone to have a thrust-to-weight ratio of at least 2. What top rotor speed (rpm) is needed? What if it must also carry a 0.4 kg parcel? With the real top speed of 1000 rad/s, what is the largest payload that keeps the ratio at 2?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
