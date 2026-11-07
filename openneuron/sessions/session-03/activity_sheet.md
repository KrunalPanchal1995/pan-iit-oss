# Activity sheet: openneuron, Session 3: The Hodgkin-Huxley nerve: a simulation you can validate

Name: ____________________   Date: ____________

**Objectives**

- State the four Hodgkin-Huxley equations with the classic squid-axon parameters and their sign convention.
- Integrate them with your own RK4 and reproduce the action potential, the threshold and the refractory period.
- Measure the onset of repetitive firing and the maximum firing rate, and validate the model against the resting state, a charge balance and the leaky closed form.
- Explain how temperature, sodium conductance and axon diameter change the signal, and why too large a time step blows up the simulation.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Find the smallest 1 ms pulse that fires a spike, and show that the spike is all or nothing.

1. ______________________________  (hint: Integrate the four equations with RK4 (dt = 0.02 ms) from the resting ...)
2. ______________________________  (hint: Apply a 1 ms pulse of amplitude A at t = 1 ms and bisect on A: the sma...)
3. ______________________________  (hint: A pulse of 6.5 uA/cm^2 peaks at only -59.1 mV and decays: no spike....)
4. ______________________________  (hint: Pulses of 7.5, 15 and 30 uA/cm^2 all produce a spike peaking between 3...)
5. ______________________________  (hint: Cross-check with the charge: a 1 ms pulse of 6.92 uA/cm^2 delivers 6.9...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a spike appear suddenly once the stimulus passes a threshold, and why is it the same size for every stronger stimulus?

Answer: ______________________________________________


**B. Numerical.** For a tiny current of 0.1 uA/cm^2 the membrane acts, for the first moments, like a leaky capacitor with g_0 = 0.6775 mS/cm^2. Calculate by hand the voltage rise after 0.2 ms and compare it with the simulation.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the f-I curve, what happens at currents below 6.27, just above it, and at very large currents? What does this say about the cell?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a spike must travel 1 m in 20 ms, that is 50 m/s. Using the scaling v proportional to sqrt(a) and the simulated 7.97 m/s for a 100 um radius, what radius would an unmyelinated axon need? What does this suggest, and what temperature effect would you expect?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
