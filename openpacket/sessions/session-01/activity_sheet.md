# Activity sheet: openpacket, Session 1: A message is cut into packets that hop from router to router

Name: ____________________   Date: ____________

**Objectives**

- Explain why a message is cut into numbered packets and what a label (header) is for.
- Cut a message into packets and rebuild it, even when packets arrive in the wrong order.
- Follow a route hop by hop using only next-hop tables.
- Count the time steps a message needs with steps = hops + packets - 1, and explain why very small and very large packets are both slow.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 1000 byte message is sent in packets of 300 bytes of payload over 3 hops. Links run at 1 Mbit/s and every packet has a 40 byte label. How many packets are there, how many steps, and how long does the delivery take?

1. ______________________________  (hint: N = ceil(1000 / 300) = ceil(3.33) = 4 packets (300, 300, 300 and 100 b...)
2. ______________________________  (hint: Steps = H + N - 1 = 3 + 4 - 1 = 6....)
3. ______________________________  (hint: One step = (300 + 40) * 8 / 1 000 000 = 0.00272 s = 2.72 ms....)
4. ______________________________  (hint: T = 6 * 2.72 ms = 16.32 ms....)
5. ______________________________  (hint: Check by simulation: journey_steps(4, 3) moves the packets one step at...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does every packet carry a sequence number? What goes wrong without it?

Answer: ______________________________________________


**B. Numerical.** A 900 byte message is sent in packets of 250 bytes of payload over 4 hops at 1 Mbit/s, with a 40 byte label per packet. Find the number of packets, their sizes, the steps and the delivery time.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the graph of delivery time against payload size (1000 byte message, 5 hops), the time is 25.92 ms for 20 byte packets, 15.68 ms for 100 byte packets and 41.6 ms for one 1000 byte packet. Explain the shape of the curve.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for the 1000 byte message over 5 hops, compare payloads of 50, 100, 200 and 500 bytes and choose one. What would make you choose a larger size in real life?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
