# Project form (Hello FOSS)

**Project name:** openpacket

**Short description:** Cut a message into packets, route them hop by hop and simulate queues, loss and link failures, from scratch in 3 sessions.

**Full description:** openpacket is a beginner-friendly learning repo about how a message travels from a browser to a server. In three short sessions you go from the idea of packets passed between routers like parcels between post offices, to the mathematics of headers, 32-bit addresses, subnets, longest-prefix routing and the latency budget, to a tiny network simulator written in plain Python. The simulator builds routing tables with Dijkstra's algorithm, forwards packets through finite queues, and is checked against the delay formulas, the stop-and-wait utilisation formula and the conservation of packets. You also break the network on purpose: a full buffer, a cut link, a routing loop and a missing route. Everything is a simplified educational model that runs on your computer; no real network traffic is generated. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as distributed routing, fair sharing of a link and queue management.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openpacket
