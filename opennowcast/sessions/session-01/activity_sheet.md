# Activity sheet: opennowcast, Session 1: A rain cell drifts with the wind

Name: ____________________   Date: ____________

**Objectives**

- Read a radar picture as a grid of rain rates (mm/h) with 1 km pixels and one frame every 5 minutes.
- Turn the movement of a cell between two frames into a wind speed in km/h.
- Say when a cell reaches a town and when the rain there first reaches 5 mm/h.
- Explain why a small change in wind direction can mean a miss.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Between two frames 5 minutes apart a cell (width 6 km, centre rain rate 40 mm/h) moved 3 pixels east. The town is 36 km east of the cell. What is the wind, when does the centre arrive, and when does the rain at the town first reach 5 mm/h?

1. ______________________________  (hint: Wind = 12 x 3 = 36 km/h towards the east (3 km in 1/12 hour)....)
2. ______________________________  (hint: The centre arrives after 36 km / 36 km/h = 1 hour = 60 minutes....)
3. ______________________________  (hint: The 5 mm/h edge of the cell is r = 6 x sqrt(2 ln(40/5)) = 6 x sqrt(2 x...)
4. ______________________________  (hint: Rain of 5 mm/h reaches the town when the centre is 12.24 km away, that...)
5. ______________________________  (hint: Check: after 39.6 minutes the distance is 12.24 km and R = 40 exp(-12....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do we need two radar pictures to get the wind, and why do we assume the wind stays the same during the forecast?

Answer: ______________________________________________


**B. Numerical.** A cell moves 5 pixels east in 5 minutes. A town is 45 km east of its centre. What is the wind and when does the centre arrive?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the graph of rain at the town, the wind straight at the town and the wind turned by 20 degrees give very different peaks. Read both peaks and explain the difference.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a town wants at least 20 minutes of warning before rain of 5 mm/h or more, for a cell moving straight at it at 36 km/h. How far away must the cell centre be at the moment the forecast is issued?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
