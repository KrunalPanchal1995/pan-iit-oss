# Roadmap: the path to the opendaylight Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Clock time, the equation of time and real sunrise

**You will learn:** Why the sun is not highest at 12:00 on your clock: longitude, Indian Standard Time (82.5 E) and the equation of time; how refraction lifts the sun at the horizon.

**You will build:** A function that converts IST at a given longitude to solar time, and a sunrise and sunset in clock time with the standard 0.833 degree correction.

**Checkpoint (not met by the shipped code):** Solar noon in Chennai (80.27 E) on 3 November falls at about 11:52 IST (12:00 + 8.9 min for longitude - 16.4 min equation of time), within 2 minutes (the shipped code uses solar time only, so it says 12:00).

**Difficulty:** intermediate

## Session 5: Side fins and egg-crate shading

**You will learn:** The horizontal shadow angle and why vertical fins, not overhangs, stop low east and west sun.

**You will build:** A fin shading function for one or two fins and a combined overhang-plus-fin (egg-crate) sunlit area, checked with the 3D ray test of Session 3.

**Checkpoint (not met by the shipped code):** A west window in Chennai (WWR 0.25) with 0.5 m fins on both sides and a 0.6 m overhang gains at least 25 percent less solar heat in a year than with the overhang alone (the shipped code has no fins).

**Difficulty:** intermediate

## Session 6: Real weather and the monsoon

**You will learn:** Global, direct and diffuse sunlight in a weather file (EPW), and how clouds change the daylight and the cooling.

**You will build:** A reader for an hourly weather file and a version of `simulate_year` that uses measured direct and diffuse sunlight and the outdoor temperature instead of the clear-sky model and a fixed 4 K.

**Checkpoint (not met by the shipped code):** For Chennai, the June to September solar heat through a south window drops by at least 20 percent compared with the clear-sky model (the shipped model has no clouds).

**Difficulty:** intermediate

## Session 7: A daylight map across the room

**You will learn:** Why the daylight factor is high near the window and low at the back; the sky component, the reflected components and daylight autonomy.

**You will build:** A grid of desk points with a sky component from the visible sky patch and a simple internally reflected component, and the share of working hours each point gets 300 lux.

**Checkpoint (not met by the shipped code):** For the Session 3 room, the point-by-point daylight factors average to within 15 percent of the average daylight factor formula, and the point 1 m from the window is at least three times the point 4 m from it.

**Difficulty:** advanced

## Session 8: Glare and thermal mass

**You will learn:** When direct sun on the desk causes glare, and how heavy walls delay and smooth the cooling load.

**You will build:** A check for sun patches on a desk zone, and a one-node resistance-capacitance (RC) room model that stores heat between hours.

**Checkpoint (not met by the shipped code):** With thermal mass the peak hourly cooling load of the west window room falls by at least 20 percent while the daily total changes by less than 5 percent (the shipped model has no storage).

**Difficulty:** advanced

## The final step

Combine the milestones: clock time, fins, real weather, a daylight map, glare and thermal mass in one planner that recommends the window for any Indian city. If your result looks like the Target, open a pull request and tell us how you did it.
