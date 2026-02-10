# Lab 04 — Time, ordering, and Lamport clocks

## Learning goals
- Understand happened-before and partial ordering.
- Implement Lamport logical clocks correctly.
- Build a total order using tie-breakers (time + node ID).

## In-class walkthrough
1. **Simulate nodes**
   - 3–5 nodes exchange messages over in-memory queues.
2. **Lamport clock rules**
   - Increment on local event.
   - `clock = max(clock, msg.clock) + 1` on receive.
3. **Distributed log viewer**
   - Collect events from all nodes.
   - Sort by `(lamport_time, node_id)` to show total order.

## Student deliverable
- A small library/module that provides Lamport clock operations.
- A demo program that logs events and prints sorted output.

## Instructor notes
- Show that partial order is more realistic than wall-clock time.
- Demonstrate concurrent events with different node IDs.
- Use a stable sorting strategy to make results deterministic.

## Tools (free + open source)
- Python 3.11+ or Go 1.21+.
- pytest or Go test for quick checks.

## Suggested reading & sources
- Lamport, “Time, Clocks, and the Ordering of Events in a Distributed System”: https://lamport.azurewebsites.net/pubs/time-clocks.pdf
