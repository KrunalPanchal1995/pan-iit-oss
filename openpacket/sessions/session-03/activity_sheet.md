# Activity sheet: openpacket, Session 3: A tiny network simulator: queues, loss, failures and validation

Name: ____________________   Date: ____________

**Objectives**

- Write Dijkstra's algorithm and use it to build routing tables.
- Simulate packets forwarded hop by hop through finite queues, and check the measured delay against the analytic sum.
- Verify the stop-and-wait utilisation formula and the effect of a window, and see retransmission repair loss.
- Simulate a link failure with re-routing, a routing loop and a missing route, and check that packets are conserved.
- Choose a buffer size and a packet size for a video stream and justify them.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A burst of 10 packets of 1500 bytes (12000 bits) is sent at once into a link of 10 Mbit/s with 10 ms wire delay and a buffer of 4 waiting packets. How many arrive, how many are dropped, and what is the delay of the last one that arrives?

1. ______________________________  (hint: Time to send one packet x = 12000 / 10e6 = 0.0012 s = 1.2 ms....)
2. ______________________________  (hint: The first packet goes straight onto the wire; the next 4 wait in the b...)
3. ______________________________  (hint: So 1 + 4 = 5 packets arrive, 5 are dropped....)
4. ______________________________  (hint: The k-th packet finishes sending at k * 1.2 ms and arrives 10 ms later...)
5. ______________________________  (hint: The last one (k = 5) has delay 5 * 1.2 + 10 = 16.0 ms, of which queuei...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is stop-and-wait very inefficient on a link with a long delay, and what does a window change?

Answer: ______________________________________________


**B. Numerical.** A sender uses stop-and-wait with 1500 byte packets on a 10 Mbit/s link; the RTT after sending is 20.04 ms. Find x, U and the throughput. Which window fills the pipe?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the re-routing graph, read the delay before the cut, after re-routing, and the number of lost packets. Why are exactly those packets lost, and how many would be lost if the failure were detected after 0.025 s instead of 0.05 s?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the router is upgraded from 16 to 20 buffer slots. A 20000 byte video frame is sent as one burst; each packet has a 40 byte header. What is the smallest payload that loses nothing now, and what happens with a payload of 761 bytes?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
