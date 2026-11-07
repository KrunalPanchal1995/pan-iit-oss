# Activity sheet: openledcontrol, Session 2: The divider, the LED resistor and the transistor

Name: ____________________   Date: ____________

**Objectives**

- Turn the LDR resistance into a voltage with a voltage divider.
- Choose the fixed resistor for a wanted threshold light level.
- Size the LED current-limiting resistor and the transistor base resistor (forced gain 10).
- Solve a design problem: the components of an automatic night light.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Design a night light for 5 V that turns on below 20 lux, using the illustrative LDR, a red LED at about 10 mA, an NPN transistor and V_th = Vcc / 2. Find R, R_led and R_B, and say what threshold you really get.

1. ______________________________  (hint: LDR at 20 lux: R_ldr = 10 000 * (20 / 10) ^ (-0.7) = 10 000 * 0.6156 =...)
2. ______________________________  (hint: With V_th = 2.5 V = Vcc / 2, R = R_ldr = 6 156 ohm. E12 neighbours: 5....)
3. ______________________________  (hint: LED resistor: (5 - 2) / 0.010 = 300 ohm, next E12 value up: 330 ohm, s...)
4. ______________________________  (hint: Base current for forced gain 10: I_B = 9.09 / 10 = 0.909 mA. R_B = (5 ...)
5. ______________________________  (hint: Check: with V_CE(sat) = 0.2 V the LED gets (5 - 2 - 0.2) / 330 = 8.48 ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do we size the base resistor for a forced gain of 10 when the transistor's gain might be 100 or more?

Answer: ______________________________________________


**B. Numerical.** A blue LED has Vf = 3.0 V (typical) and should carry 15 mA from 5 V. Find the LED resistor (pick an E12 value at or above the result) and the actual current, then the base resistor for forced gain 10 with a 5 V drive (E12 at or below).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the divider graph the 15 kilo-ohm curve crosses 2.5 V at a lower light level than the 3.3 kilo-ohm curve. Read the two crossing light levels, and explain why a bigger R trips at a lower light level.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design an automatic night light that turns on below 30 lux with V_th = 2.5 V: choose R from E12 and state the real trip level, choose R_led and R_B for a 10 mA red LED, and say how you would make the threshold adjustable.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
