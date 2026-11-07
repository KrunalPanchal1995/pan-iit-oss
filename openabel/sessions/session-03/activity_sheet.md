# Activity sheet: openabel, Session 3: Back from the photo: onion peeling, noise and smoothing

Name: ____________________   Date: ____________

**Objectives**

- Recover a radial emission profile from a brightness profile by onion peeling and check it against an exact analytic pair.
- Measure how much the inversion amplifies noise, and where.
- Use a smoothed (Tikhonov) inversion and explain the trade-off between bias and noise.
- Recognise a failure case (over-smoothing a ring-shaped flame) and apply the method to a candle-like flame photo.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Three rings of width 1 mm (R = 3 mm) give measured brightness I = (12, 9.121, 4.472) a.u. at y = 0, 1 and 2 mm. Recover the emission of each ring by onion peeling.

1. ______________________________  (hint: The ring matrix (Session 2 formula) has rows (2, 2, 2), (0, 3.464, 2.1...)
2. ______________________________  (hint: Outermost ring first: eps_2 = 4.472 / 4.472 = 1....)
3. ______________________________  (hint: Next ring: eps_1 = (9.121 - 2.192 * 1) / 3.464 = 6.929 / 3.464 = 2....)
4. ______________________________  (hint: Innermost ring: eps_0 = (12 - 2 * 2 - 2 * 1) / 2 = 6 / 2 = 3....)
5. ______________________________  (hint: Check by the forward model: 2*3 + 2*2 + 2*1 = 12, 3.464*2 + 2.192*1 = ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the noise in the recovered emission grow towards the axis, and why does smoothing help but not for free?

Answer: ______________________________________________


**B. Numerical.** For N = 40 rings the noise gain of the axis ring is 5.9 per mm. The photo noise is sigma = 0.02 a.u. What is the noise in the emission of the axis ring? Compare with a Gaussian flame whose peak emission is 1 a.u. per mm.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the trade-off graph of the Gaussian flame at 1 percent noise, how do the bias, noise and total change as lam goes from 0.00001 to 30? Where is the minimum of the total?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a ring-shaped flame (r0 = 1.5 mm, w = 0.4 mm) is photographed with 1 percent noise and 40 rings. Choose between lam = 0.01, 0.1 and 10 and give the total error of each (use `bias_noise_exact`). What risk does the largest lam bring for a hollow flame?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
