# Roadmap: the path to the openheatpump Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Weather-compensated supply temperature

**You will learn:** Why running the radiators only as hot as the weather requires raises the COP, and how heating curves work.

**You will build:** A supply temperature that rises linearly as the outdoor temperature falls, limited to 30 to 45 C, used inside the hourly simulation.

**Checkpoint (not met by the shipped code):** A seasonal COP of at least 3.4 with a 45 C peak supply on the seeded winter (the shipped fixed 45 C supply gives 2.99).

**Difficulty:** intermediate

## Session 5: On/off thermostat with minimum run time

**You will learn:** How a fixed-speed compressor cycles, why short cycling wears machines and how dead band and minimum run time trade comfort against starts.

**You will build:** A hysteresis thermostat at a sub-hourly step that switches the heat pump fully on or off.

**Checkpoint (not met by the shipped code):** At most 6 compressor starts per day on average over the cold week with the indoor temperature always between 19.0 and 21.0 C (the shipped controller has no on/off cycling at all).

**Difficulty:** intermediate

## Session 6: Capital cost and the best size

**You will learn:** How purchase price and running cost together decide the best rated capacity.

**You will build:** A cost model with a price per kW of rated capacity added to the running cost over several winters.

**Checkpoint (not met by the shipped code):** For UA 0.26 kW/K, 45 C supply, 6 kW backup, a price of 350 per kW and 15 winters, the best size is between 8.5 and 9.5 kW with a total near 25100 (the shipped code only reports running cost).

**Difficulty:** intermediate

## Session 7: Make the daily model honest

**You will learn:** Why daily mean temperatures hide the cold hours and how to correct a quick estimate.

**You will build:** A correction to the Session 2 daily method (for example a daily-swing and defrost adjustment) tuned against the hourly simulation.

**Checkpoint (not met by the shipped code):** Seasonal electricity within 2 percent of the hourly result on the seeded winter (the shipped daily method gives 3273 kWh against 3556 kWh hourly, 8 percent low).

**Difficulty:** advanced

## Session 8: Two-node house and night setback

**You will learn:** A fast air node and a slow wall node, and how setback and recovery interact with the heat pump.

**You will build:** A two-capacity house model with a 17 C night set point, integrated with a fourth-order method at a sub-hourly step, drawn like the Target.

**Checkpoint (not met by the shipped code):** A cold week in which the heat pump costs less than 40 percent of the resistance heater and the indoor temperature never falls below 16.5 C (the shipped one-capacity model has no setback).

**Difficulty:** advanced

## The final step

Combine the milestones: a house with fast and slow thermal mass, a weather-compensated supply temperature, a backup heater and a size chosen from running plus purchase cost, animated as a winter week. If your result looks like the Target animation, open a pull request and tell us how you did it.
