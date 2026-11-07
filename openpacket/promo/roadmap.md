# Roadmap: the path to the openpacket Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Routers that talk to each other

**You will learn:** How distance-vector routing builds tables from messages between neighbours, and why it can take time to settle after a failure.

**You will build:** A routing protocol in the simulator where each router knows only its neighbours and exchanges tables, instead of the global Dijkstra.

**Checkpoint (not met by the shipped code):** After any single link failure on the Session 3 test network, the tables settle to the same tables Dijkstra gives, and the number of message rounds is reported.

**Difficulty:** intermediate

## Session 5: Pace the video

**You will learn:** Why spreading the packets of a frame over the frame interval needs far less buffer than a burst.

**You will build:** A paced sender for the video stream.

**Checkpoint (not met by the shipped code):** A stream with payload 761 bytes loses no packet with a buffer of only 4 slots (the shipped burst sender needs 26).

**Difficulty:** intermediate

## Session 6: A sender that finds its own window

**You will learn:** Slow start and congestion avoidance inside the packet simulator instead of the round-trip toy.

**You will build:** A sender that starts with a window of 1 and adapts it to acknowledgements and losses.

**Checkpoint (not met by the shipped code):** Without being told the window, the sender reaches at least 80 percent utilisation of the bottleneck link (the shipped senders keep a fixed window chosen by hand).

**Difficulty:** advanced

## Session 7: Two senders share a link

**You will learn:** Fairness: how two adaptive senders divide a bottleneck.

**You will build:** Two flows through the same router with the adaptive sender from the previous step.

**Checkpoint (not met by the shipped code):** Jain's fairness index of at least 0.95 and a utilisation of at least 90 percent over 20 seconds of simulated time.

**Difficulty:** advanced

## Session 8: Smarter queues

**You will learn:** Why a long full buffer adds delay, and how active queue management drops early to keep it short.

**You will build:** A queue that drops early (for example random early detection) in place of tail drop.

**Checkpoint (not met by the shipped code):** At the same throughput, the median queueing delay is lower than with tail drop; report both numbers.

**Difficulty:** advanced

## The final step

Combine the milestones: a live network where routers discover paths by talking to each other, senders adapt their windows, queues stay short, and a link failure causes a short dip that recovers on its own. If your result looks like the Target animation, open a pull request and tell us how you did it.
