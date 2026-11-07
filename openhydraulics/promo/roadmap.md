# Roadmap: the path to the openhydraulics Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Pump strokes with check valves

**You will learn:** How two one-way valves let a hand pump raise the ram in steps and hold it between strokes.

**You will build:** A stroke-by-stroke model of the jack with a suction and a delivery valve, replacing the continuous pump flow.

**Checkpoint (not met by the shipped code):** After lifting the car 10 cm and releasing the handle, the car sinks by less than 1 mm in 60 s with new seals (without a check valve the shipped Session 3 leakage alone would lower it by about 55 mm in 60 s).

**Difficulty:** intermediate

## Session 5: Air in the oil

**You will learn:** Why a trapped air bubble makes a jack spongy, and how the effective bulk modulus of oil with air is much lower.

**You will build:** A pump model with a dead volume between the valves that is squeezed on every stroke.

**Checkpoint (not met by the shipped code):** With a dead volume of 20 cm^3 and an effective bulk modulus of 0.1 GPa, the 50 mm jack of Session 2 needs at least 1.7 pumps per centimetre (the ideal Session 2 model gives 1.56).

**Difficulty:** intermediate

## Session 6: Cylinder wall and pressure rating

**You will learn:** How the wall of a cylinder carries pressure (thin-wall hoop stress) and why every pressure vessel has a safety factor.

**You will build:** A small calculator that gives wall thickness from pressure, bore and allowable stress.

**Checkpoint (not met by the shipped code):** For a 50 mm bore at 100 bar with an allowable hoop stress of 60 MPa the wall thickness is at least 4.2 mm (the shipped sessions have no wall model at all).

**Difficulty:** intermediate

## Session 7: Controlled lowering with an orifice

**You will learn:** How a car is lowered smoothly by letting oil escape through a small throttle opening, using the orifice flow equation.

**You will build:** A lowering simulation with a throttle valve and a chosen opening.

**Checkpoint (not met by the shipped code):** Lowering the 1200 kg car at 2 cm/s through an orifice (discharge coefficient 0.62, oil density 870 kg/m^3) needs an opening of about 0.54 mm^2, within 5 percent.

**Difficulty:** advanced

## The final step

Combine the milestones: a pumping jack with check valves, air in the oil, a rated cylinder wall and a controlled descent, with a clean animation of the lever, the gauge and the force-speed trade-off. If your result looks like the Target animation, open a pull request and tell us how you did it.
