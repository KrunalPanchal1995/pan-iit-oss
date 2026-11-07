# Activity sheet: opendronecontrol, Session 2: Altitude hold with a PID controller

Name: ____________________   Date: ____________

**Objectives**

- Explain the feedback loop: error, controller, thrust, drone, measurement.
- Say what each of P, I and D does and predict the response from Kp, Ki and Kd.
- Compute the natural frequency, damping ratio, overshoot and steady-state error of an altitude loop by hand.
- Simulate the loop step by step, check it against the formulas, and tune gains to meet a specification.

## Before you start: predict
In your own words, what do you think will happen when you move the Kd slider from 0 to 6 in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A PD altitude controller with Kp = 4 N/m and Kd = 3 N s/m believes the drone weighs 1.2 kg, but it really weighs 1.4 kg. Find wn, zeta, the overshoot and the settling time of a climb to 2 m, and the final height. Then add Ki = 1.5 N/(m s) and check it is stable.

1. ______________________________  (hint: Natural frequency: wn = sqrt(4 / 1.4) = 1.690 rad/s....)
2. ______________________________  (hint: Damping ratio: zeta = 3 / (2 sqrt(4 x 1.4)) = 0.634....)
3. ______________________________  (hint: Overshoot: exp(-0.634 x 3.1416 / 0.773) = 0.076; settling about 3.7 s....)
4. ______________________________  (hint: Steady-state error: (1.4 - 1.2) x 9.81 / 4 = 0.4905 m....)
5. ______________________________  (hint: With Ki = 1.5: Kd Kp = 12 > m Ki = 2.1, so stable....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a PD controller leave the heavier drone below its target, and how does adding the I term fix it? What does the I term cost?

Answer: ______________________________________________


**B. Numerical.** For the 1.4 kg drone choose Kp = 8 N/m. What Kd gives zeta = 0.7? Find wn, the overshoot, the settling time and the PD steady-state error. Check that the answers are reasonable compared with the worked example.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In Figure 2 (left), Kd = 0.8, 1.5, 3 and 6 N s/m. Predict the overshoot of each from the formula and say which curve has none. Why is the Kd = 6 curve the slowest to rise even though it has the most "control"?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the drone (1.4 kg, controller believes 1.2 kg) must reach 2 m with overshoot below 10 percent, settle within 4 s, and end within 2 cm of the target. The thrust is limited to 40 N. Choose Kp, Ki and Kd and justify them. What is the largest Ki the Routh test allows?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
