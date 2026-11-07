# Experiment sheet: does salt hold a floater higher? (openbuoyancy, Session 1)

Name: ____________________   Date: ____________

**Question.** Sea water is about 2.5 percent denser than fresh water. Does adding salt to a bucket of fresh water make a floating bottle sit higher, and by how much?

**You need:** a bucket holding exactly 10 litres of tap water, about 1 kg of table salt, a kitchen scale, a straight-sided plastic bottle (a drinks bottle with straight sides) with sand or small stones in the bottom so that it floats upright, a ruler or a strip of tape marked in millimetres, a spoon, and a cloth for spills. Do not drink the salt water.

**Set up the floater.** Seal the bottle. Weigh it on the scale (mass m in kg) and measure the diameter of its straight part to get the base area A = pi x (diameter / 2)^2 in m^2. The predictions below use the example bottle m = 0.60 kg and A = 0.0050 m^2 (diameter 8.0 cm). If yours is different, use the formula in the box at the bottom.

**Method.**
1. Stand the bottle in the bucket. It must float upright and must not touch the sides or the bottom.
2. Read the draft (the depth of the bottle's base below the water line) from the tape stuck to the outside, to the nearest millimetre. This is the 0 g row.
3. Add 200 g of salt, stir until it has all dissolved, wait until the water is still, and read the draft again. Repeat until you have added 1000 g in total.
4. Write each reading in the table and subtract it from the prediction.

**Predictions from the lesson** (`salt_experiment` in `lesson.py`, density = 1000 + 0.714 x grams of salt per litre, draft = m / (density x A)):

| Salt added (g) | Salt per litre (g/L) | Predicted density (kg/m^3) | Predicted draft (mm) | Measured draft (mm) | Measured minus predicted (mm) |
|---|---|---|---|---|---|
| 0 | 0 | 1000 | 120 | | |
| 200 | 20 | 1014 | 118 | | |
| 400 | 40 | 1029 | 117 | | |
| 600 | 60 | 1043 | 115 | | |
| 800 | 80 | 1057 | 114 | | |
| 1000 | 100 | 1071 | 112 | | |

Expected pattern: the draft falls by about 1.6 mm for every 200 g of salt, 8 mm in all. A change this small is the reason to use a tall, narrow floater and to read the ruler carefully.

**Your own floater.** m = ________ kg, A = ________ m^2. For each row: density = 1000 + 0.714 x (salt in g / 10 litres), then draft = m / (density x A).

**Why your measurements will differ from the table.**
- The 0 g reading is the best check of your m and A. If it is off by more than 2 mm, fix m and A first, because every other row inherits the error.
- Adding salt also adds a little volume, and the salt-density rule is a straight-line fit that gets less accurate above about 100 g per litre.
- The bottle is not perfectly straight-sided, and the curved shoulder near the water line changes the area as the draft changes.
- Reading the water line against a ruler has an error of about 1 mm, which is a large share of the 8 mm change. Reading the line from a different eye height changes the value.
- Salt that has not fully dissolved sinks to the bottom and does not add to the density near the bottle. Stir and wait.
- Water temperature changes the density a little (about 0.2 kg/m^3 per degree), so keep the bucket at room temperature.

**Think.** If the measured draft barely moved, was the model wrong or the measurement too coarse? Which one can you test by repeating the 0 g reading three times?
