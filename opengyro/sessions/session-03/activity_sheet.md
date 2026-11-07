# Activity sheet: opengyro, Session 3: Simulating the heavy top: Euler angles, precession and nutation

Name: ____________________   Date: ____________

**Objectives**

- State the Lagrangian of the heavy symmetric top in Euler angles and find its two conserved momenta.
- Integrate the equations with RK4 and validate with energy, p_phi and p_psi.
- Compare the simulated precession rate with m g r / (I3 w3) and measure the nutation frequency.
- Check the classical sleeping-top bound and recognise a top that falls over.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Top: m = 0.5 kg, R = 5 cm, r = 4 cm, spin w3 = 300 rad/s, released at 60 degrees. Predict the precession rate, its period and the nutation frequency, then compare with the simulation.

1. ______________________________  (hint: I3 = m R^2 / 2 = 6.25e-4 kg m^2; I1 = m R^2 / 4 + m r^2 = 3.125e-4 + 8...)
2. ______________________________  (hint: I3 w3 = 6.25e-4 * 300 = 0.1875 kg m^2/s....)
3. ______________________________  (hint: Precession: Omega_p = 0.1962 / 0.1875 = 1.0464 rad/s, so one circle ta...)
4. ______________________________  (hint: Nutation: w_n = I3 w3 / I1 = 0.1875 / 1.1125e-3 = 168.5 rad/s, i.e. 26...)
5. ______________________________  (hint: Simulation (RK4, dt = 0.2 ms, 3 s): precession 1.0496 rad/s (0.3 perce...)
6. ______________________________  (hint: Validation: relative drift of p_psi, p_phi and energy is below 1e-11....)

Final answer: ____________________

## Questions
**A. Conceptual.** The simulation does not build conservation into the integration. Why is it still a good test that p_phi, p_psi and the energy stay constant?

Answer: ______________________________________________


**B. Numerical.** Use the classical bound w3^2 > 4 m g r I1 / I3^2 to find the minimum spin for a vertical top for this disc (m = 0.5 kg, r = 4 cm, I1 = 1.1125e-3, I3 = 6.25e-4 kg m^2).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the tilt-versus-time graph at 300 rad/s the tilt ripples with a period of about 0.037 s while the axis circles once in about 6 s. What do these two periods tell you about Omega_p and w_n?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a toy maker pulls a string that gives at most 120 rad/s. The top (same disc) must stand safely above the sleeping limit (use a 30 percent margin) and precess slower than 3 rad/s when tilted. Choose a spin and justify it.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
