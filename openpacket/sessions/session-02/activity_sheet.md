# Activity sheet: openpacket, Session 2: The mathematics of a packet: headers, addresses, routing tables and delay

Name: ____________________   Date: ____________

**Objectives**

- Build a toy packet from bytes with a header, a payload and a checksum.
- Convert IPv4 addresses between dotted decimal and a 32-bit integer, and use bit masks for subnets.
- Implement longest-prefix-match routing and test it on a small table.
- Add propagation, transmission and queueing delay and compute the minimum round-trip time from Delhi to London.
- Choose a packet size that keeps the header overhead below 5 percent.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 1500 byte packet crosses Delhi to London (6712 km great-circle distance) on a 100 Mbit/s link and waits 2 ms in queues. Find the propagation, transmission and total one-way delay, and the minimum round-trip time.

1. ______________________________  (hint: Propagation = d / v = 6.712e6 m / 2e8 m/s = 0.03356 s = 33.56 ms....)
2. ______________________________  (hint: Transmission = L / B = (1500 * 8 bits) / 100e6 bit/s = 12000 / 1e8 = 0...)
3. ______________________________  (hint: Queueing = 2 ms (given)....)
4. ______________________________  (hint: Total one-way = 33.56 + 0.12 + 2 = 35.68 ms....)
5. ______________________________  (hint: Minimum round trip = 2 d / v = 2 * 33.56 = 67.12 ms (no queueing, zero...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why must a router use the longest matching prefix rather than the first or shortest match? Give an example with the table in the lesson.

Answer: ______________________________________________


**B. Numerical.** How many addresses does a /20 subnet hold? Is 10.1.15.200 inside 10.1.0.0/20? Is 10.1.16.0?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the overhead graph, at about what payload do the toy header (14 bytes) and the 40 byte header cross the 5 percent line? What does a flat tail of the curve tell you?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the header is 40 bytes, the link is 1 Mbit/s and the transmission time of one packet must not exceed 10 ms. Overhead must be below 5 percent. Which payload sizes are allowed? Which would you choose?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
