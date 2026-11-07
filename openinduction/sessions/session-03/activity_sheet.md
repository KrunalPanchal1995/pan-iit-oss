# Activity sheet: openinduction, Session 3: A loaded generator, transformer losses and saturation

Name: ____________________   Date: ____________

**Objectives**

- Simulate a generator with armature resistance and inductance driving a load, using RK4, and validate it against the exact steady state.
- Check energy conservation (mechanical work in = electrical energy out + losses) and see Lenz's law in the sign of the torque.
- Compute transformer efficiency and voltage regulation from a simple copper and core loss model, and find where efficiency peaks.
- Show how core saturation distorts the output, and use the model to size a bicycle dynamo (mini-project).

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
(a) A generator with N B A = 0.08 V s runs at 50 Hz with Ra = 2 ohm, L = 30 mH and RL = 10 ohm. Find the peak EMF, Z, RMS current, load power, armature heat and the mechanical power needed. (b) For the 460 : 24 turn transformer with RL = 6 ohm on its secondary and 230 V on the primary, find V2, efficiency and regulation.

1. ______________________________  (hint: (a) w = 2 pi x 50 = 314.16 rad/s. Em = 0.08 x 314.16 = 25.13 V. w L = ...)
2. ______________________________  (hint: Z = sqrt((2 + 10)^2 + 9.425^2) = sqrt(144 + 88.83) = 15.26 ohm. Irms =...)
3. ______________________________  (hint: Load power = 1.165^2 x 10 = 13.56 W. Armature heat = 1.165^2 x 2 = 2.7...)
4. ______________________________  (hint: The RK4 simulation gives the same load power (13.565 W) and a mechanic...)
5. ______________________________  (hint: (b) a = 460 / 24 = 19.17, Req = 30 + 19.17^2 x 0.08 = 59.4 ohm, and RL...)
6. ______________________________  (hint: Efficiency = 22.75 / (22.75 + 0.61 + 1.51) = 91.5 percent. Regulation ...)

Final answer: ____________________

## Questions
**A. Conceptual.** A bicycle dynamo is harder to pedal when the lamp is on than when the lamp is off. Explain why using Lenz's law, and say where the energy for the lamp comes from.

Answer: ______________________________________________


**B. Numerical.** A generator has Em = 20 V peak, Ra = 1 ohm, RL = 9 ohm and negligible inductance. Find the RMS current, the power in the load, the heat in the armature and the mechanical power, and check that they balance.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the transformer efficiency figure, the output power is 0.29 W at a load of 500 ohm. Roughly what is the efficiency there (the curve starts near 16 percent), why is it so low, and why does it fall again beyond the peak at about 33 W?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for the generator in the worked example (Ra = 2 ohm, L = 30 mH, 50 Hz, Em = 25.13 V), which RL gives the largest load power, and what share of the mechanical power does the armature waste there? What RL would you choose if the armature must waste no more than 10 percent, and what load power do you get?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
