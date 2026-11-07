# Roadmap: the path to the opendcmotor Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Climb steeper: the 35 degree drive

**You will learn:** Why one motor and one gear stage run out of range, and what voltage, motor choice or a two-stage gearbox changes.

**You will build:** A drive study that extends `window` to compare motors, supply voltages and gear stages.

**Checkpoint (not met by the shipped code):** A drive for the 8 kg robot that climbs 35 degrees at 0.5 m/s or more with at most 1.5 A per motor (the shipped drive finds no gear ratio above 31 degrees).

**Difficulty:** intermediate

## Session 5: Hold the speed: closed-loop control

**You will learn:** Feedback: measure the speed and adjust the PWM duty to remove the sag when the slope changes.

**You will build:** A PI speed controller that sets the duty cycle from the speed error, added to the time-domain simulation.

**Checkpoint (not met by the shipped code):** Speed within 2 percent of 0.5 m/s, 0.3 s after the slope changes from 10 to 25 degrees (open loop at a fixed duty, the shipped robot drive slows from 0.655 to 0.574 m/s, a 12 percent drop).

**Difficulty:** advanced

## Session 6: Measure your own motor

**You will learn:** How to find R, k and b from three simple bench measurements and a data sheet.

**You will build:** A parameter-fitting script and a bench procedure for a real hobby motor.

**Checkpoint (not met by the shipped code):** A predicted no-load speed within 5 percent of a measured one for a motor you own (the shipped code only uses given parameters).

**Difficulty:** intermediate

## Session 7: Battery sag and a thermal limit

**You will learn:** Internal resistance of a battery pack, winding heating and cooling, and what limits continuous current.

**You will build:** A battery model and a one-state thermal model for the winding, wired into the simulation.

**Checkpoint (not met by the shipped code):** A predicted winding temperature after 60 seconds of a 25 degree climb, and the battery voltage at the end of it (the shipped model has constant voltage and no thermal state beyond the stall bound).

**Difficulty:** advanced

## Session 8: Downhill and regenerative braking

**You will learn:** When the load drives the motor: negative current, back-driving and energy returned to the supply.

**You will build:** A descent simulation of the robot with the motor acting as a generator.

**Checkpoint (not met by the shipped code):** A 20 degree descent at 0.5 m/s showing negative current and the average power returned to the battery (the shipped steady-state functions only treat uphill loads).

**Difficulty:** advanced

## The final step

Combine the milestones: a robot drive that holds its speed on changing slopes, runs from a battery that sags, stays inside a thermal limit and recovers some energy downhill. If your result looks like the Target animation, open a pull request and tell us how you did it.
