# Activity sheet: openbuildingsway, Session 2: One storey, one rhythm: resonance and stiffness design

Name: ____________________   Date: ____________

**Objectives**

- Write the equation of motion of a single storey shaken at its base and name each term.
- Use the amplification factor D(r) and show that its maximum is about 1 / (2 zeta).
- Check the formula against a step-by-step numerical solution (Runge-Kutta).
- Solve an inverse design problem: how stiff must the storey be to keep D at or below 2?

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A roof mass m = 200 000 kg sits on columns of period T = 1 s. (a) Find k. (b) For a ground acceleration amplitude of 2 m/s^2 and a period of 1 s with zeta = 0.05, find the steady sway. (c) How stiff must the columns be so that D is at most 2 on the stiff side?

1. ______________________________  (hint: k = m (2 pi / T)^2 = 200 000 * (6.2832)^2 = 200 000 * 39.478 = 7.896e6...)
2. ______________________________  (hint: At T = Tg = 1 s, r = 1, so D = 1 / (2 zeta) = 10....)
3. ______________________________  (hint: a0 / w^2 = 2 / 39.478 = 0.05066 m, so u_max = 0.05066 * 10 = 0.5066 m:...)
4. ______________________________  (hint: For (c) solve D(r) = 2 with r below 1: (1 - r^2)^2 + (0.1 r)^2 = 0.25....)
5. ______________________________  (hint: The building period must be T = r Tg = 0.7107 s, so k = m (2 pi / 0.71...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the amplification factor go above 1 near r = 1 but fall below 1 for large r? What does damping change?

Answer: ______________________________________________


**B. Numerical.** A storey has m = 100 000 kg and k = 4e6 N/m, damping 5 percent. The ground has period 1 s and acceleration amplitude 2 m/s^2. Find w, T, r, D and the steady sway amplitude.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the resonance curves, read D at r = 1 for zeta = 0.02, 0.05, 0.1 and 0.2, and D at r = 1.5 for zeta = 0.05. What does each tell you?

Answer: ______________________________________________


**D. Design and optimisation challenge.** The ground period is 1.5 s (softer soil) and the roof mass is 200 000 kg. Find the stiffness and the building period for D = 2 on the stiff side and on the flexible side, with the sway amplitude for a0 = 2 m/s^2. Which design would you prefer and why?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
