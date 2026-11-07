# Roadmap: the path to the openhousehold Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Fifteen-minute steps and duty cycles

**You will learn:** Why hourly averages hide short peaks, and how thermostat and compressor cycling is modelled.

**You will build:** A load profile in 15-minute steps with appliances that switch on and off.

**Checkpoint (not met by the shipped code):** A 1.5 kW heater that runs for 20 minutes from 06:50 gives a 15-minute peak of at least 1.6 kW (the shipped hourly model reports only 0.39 kW for the same day).

**Difficulty:** intermediate

## Session 5: Time-of-use tariffs and load shifting

**You will learn:** Prices that change with the hour, and how moving a load changes the bill without changing the energy.

**You will build:** A bill function that takes a price for each hour of the day.

**Checkpoint (not met by the shipped code):** With Rs 4 per kWh from 22:00 to 06:00 and Rs 8 otherwise, moving the 2 h heater from 18:00 to 22:00 cuts the heater's cost by 50 percent (the shipped slab model changes the bill by 0.0 percent when the heater moves).

**Difficulty:** intermediate

## Session 6: Add a battery

**You will learn:** State of charge, charge and discharge limits and efficiency, and how a battery moves the afternoon sun to the evening.

**You will build:** A battery that charges from surplus solar and discharges to cover the load.

**Checkpoint (not met by the shipped code):** With a 2 kWp array and a 4 kWh battery and no credit for exports, the average-weather monthly bill is Rs 300 or less (the shipped model without a battery gives Rs 639.5).

**Difficulty:** advanced

## Session 7: Calibrate the model to a real meter log

**You will learn:** Fitting model parameters to measurements and reporting the uncertainty.

**You will build:** A fitting step that estimates appliance hours from seven days of meter readings.

**Checkpoint (not met by the shipped code):** On a seven-day synthetic log, the fitted heater time is within 0.25 h of the hidden true value and the predicted daily energy is within 5 percent on average (the shipped model always assumes 2 h and 8.26 kWh).

**Difficulty:** advanced

## Session 8: Animate the day with a Sankey diagram

**You will learn:** Accumulating energy flows frame by frame and drawing them as bands.

**You will build:** A 48-frame GIF of the stacked load, the sun and a Sankey diagram of the flows so far.

**Checkpoint (not met by the shipped code):** At every frame the energy entering from solar, battery and grid equals the energy leaving to the appliances, battery charging and export to within 1e-6 kWh, and the GIF is under 3 MB.

**Difficulty:** advanced

## The final step

Combine the milestones: a day simulator in 15-minute steps with a time-of-use tariff, solar and a battery, calibrated to your own meter, that draws the animated day view and Sankey of the Target. If your result looks like the Target animation, open a pull request and tell us how you did it.
