# Roadmap: the path to the opencomfort Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: A roof that stores heat

**You will learn:** How heat soaks into a concrete roof slab during the day and reaches the room hours later (time lag and decrement), and why insulation on top of the slab helps more than below it.

**You will build:** A roof split into 5 to 10 layers, each a small heat store, stepped with the explicit finite-difference method and coupled to the Session 3 room; options for 50 mm of insulation above or below the slab.

**Checkpoint (not met by the shipped code):** For the as-built room the heat flow through the roof peaks at least 2 hours after the outdoor sol-air peak (the shipped roof has no storage, so both peak at noon), and with a constant sol-air temperature the layered roof gives the same steady heat flow as U A dT within 0.5 percent.

**Difficulty:** intermediate

## Session 5: Fins, jaalis and sunlit walls

**You will learn:** Why low east and west sun is so hard to block: fins work only when the sun comes from the side, and a sun almost straight in front needs a screen over the glass, such as a perforated jaali that lets air through while cutting sun.

**You will build:** Shaded fractions for vertical fins and a jaali (open-area ratio as an input), and a sol-air temperature for every wall from its own orientation.

**Checkpoint (not met by the shipped code):** On 15 April at 16:00 in Chennai, a jaali with 40 percent open area cuts the beam sun on a west window by at least 50 percent, while a 0.6 m overhang shades about 4 percent and 0.3 m fins every 0.5 m shade under 5 percent, because the sun is almost straight in front (the shipped code has only overhangs and treats walls as shaded).

**Difficulty:** intermediate

## Session 6: Fans, humidity and comfort

**You will learn:** How air speed and humidity change how hot a room feels, and how to count hours of comfort instead of one peak.

**You will build:** A comfort model with air speed (ceiling fan settings) and relative humidity, and a report of comfortable hours per day for each design.

**Checkpoint (not met by the shipped code):** The comfort limit rises monotonically with air speed from 0.1 to 1.2 m/s, and the best Session 3 design gains at least 3 comfortable hours per day with the fan on high (the shipped model has a fixed 1.8 K fan allowance and ignores humidity).

**Difficulty:** intermediate

## Session 7: A month of real weather

**You will learn:** How to read an hourly weather file (temperature, sun, wind) and why one design day is not enough.

**You will build:** A loader for an hourly climate file for Chennai (for example an open EPW file), a month-long simulation, and wind-driven air changes from Session 2 instead of a fixed number.

**Checkpoint (not met by the shipped code):** Over May the simulation reports discomfort degree-hours for all 18 Session 3 designs, and the energy balance over the month closes within 0.1 percent (the shipped code repeats one synthetic day).

**Difficulty:** advanced

## Session 8: Smart windows

**You will learn:** Simple control: open when outdoor air is cooler than indoor, close when it is hotter, with a small dead band so the window does not flap.

**You will build:** A rule-based window controller inside the simulation, and a sketch for a microcontroller with two temperature sensors that drives a window actuator or a reminder light.

**Checkpoint (not met by the shipped code):** On the design day the controlled window gives a lower peak than both "open" and "night" schedules for the 0.6 m overhang and white roof design, with fewer than 6 open/close switches per day (the shipped schedules are fixed by the clock).

**Difficulty:** advanced

## The final step

Combine the milestones: a layered roof with insulation, fins and jaalis, sunlit walls, a fan and humidity in the comfort model, a month of real weather and smart windows. If your result keeps the Target room comfortable through May without an air conditioner, open a pull request and tell us how you did it.
