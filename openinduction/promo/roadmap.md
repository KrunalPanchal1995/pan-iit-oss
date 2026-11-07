# Roadmap: the path to the openinduction Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Three-phase generator

**You will learn:** Why power stations use three coils 120 degrees apart, and why the total power is steady.

**You will build:** A generator with three coils feeding three equal loads, with a plot of each phase and of the total power.

**Checkpoint (not met by the shipped code):** The three EMFs sum to zero within 1e-9 V at every instant and the total power into three equal loads is constant to 1e-9 of its mean (the shipped single-phase generator has a power ripple of 200 percent of its mean).

**Difficulty:** intermediate

## Session 5: AC to DC with a rectifier and capacitor

**You will learn:** How diodes and a smoothing capacitor turn AC into DC, and what ripple is.

**You will build:** A full-wave rectifier model with two diode drops and a capacitor, simulated in time.

**Checkpoint (not met by the shipped code):** A 10 V peak, 50 Hz supply into a 40 ohm load gives a DC output with ripple of at most 5 percent of the mean (the shipped code has no DC output at all).

**Difficulty:** intermediate

## Session 6: A transformer from two coupled coils

**You will learn:** Mutual inductance, coupling coefficient and leakage: the transformer as a circuit of two coupled coils.

**You will build:** A time-domain model of the primary and secondary currents with winding resistance and a resistive load.

**Checkpoint (not met by the shipped code):** For a 1 : 2.5 step-up with coupling coefficient 0.98 the measured voltage gain is within 6 percent of the turns ratio and the efficiency is above 85 percent (the shipped transformer is a fixed equivalent circuit with no coupled coils).

**Difficulty:** advanced

## Session 7: Hysteresis and eddy-current losses

**You will learn:** Why iron wastes energy every cycle and why cores are made of thin insulated laminations.

**You will build:** A core model with a B-H loop whose area gives the energy lost per cycle, plus an eddy-current loss that depends on lamination thickness.

**Checkpoint (not met by the shipped code):** The hysteresis loss per second equals loop area times frequency times core volume within 5 percent, and halving the lamination thickness cuts the eddy loss to one quarter within 2 percent (the shipped core loss is a single constant).

**Difficulty:** advanced

## Session 8: Switch-on inrush current

**You will learn:** Why a transformer can draw a huge current for a few cycles when it is switched on at the wrong moment.

**You will build:** The saturating core started at a voltage zero crossing with some remanent flux.

**Checkpoint (not met by the shipped code):** The first-cycle peak magnetising current is at least 5 times the steady-state peak (the shipped code starts at the voltage peak and shows a ratio of 1.0).

**Difficulty:** advanced

## The final step

Combine the milestones: a three-phase generator whose coils feed a transformer model with realistic losses, followed by a rectifier that makes smooth DC, all in one animation. If your result looks like the Target animation, open a pull request and tell us how you did it.
