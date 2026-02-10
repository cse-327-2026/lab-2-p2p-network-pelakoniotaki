# Lab 05 — Sharding & consistent hashing

## Learning goals
- Compare naïve modulo sharding vs consistent hashing.
- Quantify key movement when adding/removing nodes.
- Use virtual nodes to smooth distribution.

## In-class walkthrough
1. **Naïve modulo sharding**
   - Implement `shard = hash(key) % N`.
   - Add a node and show how many keys move.
2. **Consistent hashing ring**
   - Map nodes + keys onto a ring.
   - Show how many keys move when adding a node.
3. **Virtual nodes**
   - Add vnodes per physical node.
   - Compare distribution histograms.

## Student deliverable
- `ShardRouter` module implementing consistent hashing.
- Script that prints:
  - Histogram of key distribution.
  - % keys moved when scaling from 5 → 6 nodes.

## Instructor notes
- Emphasize real-world shard key choices and hotspotting.
- Use a fixed seed to make demos repeatable.
- Discuss rebalancing cost and operational impact.

## Tools (free + open source)
- Python 3.11+ or Go 1.21+.
- matplotlib or simple ASCII histograms (optional).

## Suggested reading & sources
- Karger et al., “Consistent Hashing and Random Trees”: https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf
