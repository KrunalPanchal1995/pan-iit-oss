# Roadmap: the path to the openneuron Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Up-and-down current sweep and a live f-I curve

**You will learn:** How to drive the model with a time-dependent current, estimate an instantaneous firing rate from inter-spike intervals, and see hysteresis.

**You will build:** A simulation with a triangle current ramp (zero to 30 and back to zero uA/cm^2 over 2000 ms) whose f-I curve is built point by point, separately for the up and the down branch.

**Checkpoint (not met by the shipped code):** Report the current of the first spike on the way up (19.79 uA/cm^2) and of the last spike on the way down (6.88), each within 0.3, and draw both branches. The shipped code only measures steady steps and reports one onset value (6.27).

**Difficulty:** intermediate

## Session 5: A stable integrator for large steps

**You will learn:** Why explicit RK4 fails at large steps and how exponential-Euler updates for the gates keep them in [0, 1].

**You will build:** A solver that integrates the gating equations with the exact exponential update and V with a stable scheme.

**Checkpoint (not met by the shipped code):** A spike with its peak within 1 mV of the dt = 0.01 reference at dt = 0.5 ms, where the shipped RK4 (which fails at 0.1 ms) blows up.

**Difficulty:** advanced

## Session 6: Saltatory conduction in a myelinated axon

**You will learn:** How insulation with gaps (nodes) makes the speed grow about linearly with diameter.

**You will build:** A cable model with insulated segments and active nodes.

**Checkpoint (not met by the shipped code):** Doubling the diameter multiplies the speed by at least 1.8 (the shipped unmyelinated cable gives 1.41).

**Difficulty:** advanced

## Session 7: Two neurons joined by a synapse

**You will learn:** A synaptic current that follows a presynaptic spike with a delay, and how a postsynaptic neuron integrates it.

**You will build:** Two leaky integrate-and-fire neurons, the first driving the second.

**Checkpoint (not met by the shipped code):** The second neuron fires one spike for each of the first 3 spikes of the first, with a delay set by the synapse.

**Difficulty:** intermediate

## Session 8: Spike-frequency adaptation

**You will learn:** A slow extra potassium current that makes a neuron slow down under constant input.

**You will build:** A leaky integrate-and-fire neuron with an adaptation variable.

**Checkpoint (not met by the shipped code):** Under constant current the last inter-spike interval is at least 1.5 times the first (the shipped neuron gives a ratio of exactly 1).

**Difficulty:** intermediate

## The final step

Combine the milestones: a model neuron driven by a slow current ramp, integrated with a stable solver, with a live f-I curve and a spike that you send along an axon. If your result looks like the Target animation, open a pull request and tell us how you did it.
