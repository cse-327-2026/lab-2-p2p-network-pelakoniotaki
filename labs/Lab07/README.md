# Lab 07 — CAP theorem via experiments

## Learning goals
- Distinguish consistency and availability under network partitions.
- Observe how CP vs AP choices change behavior.
- Measure divergence and stale reads experimentally.

## In-class walkthrough
1. **Replicated key-value service**
   - Run 2–3 replicas with a simple replication protocol.
2. **CP mode**
   - Require leader/quorum ack before responding.
   - Under partition, reject writes or return errors.
3. **AP mode**
   - Accept local writes during partition.
   - Show divergence across sides of partition.
4. **Partition with Compose**
   - Use two networks or firewall rules to split cluster.

## Student deliverable
- A driver script that runs a partitioned workload.
- A report summarizing failed ops, stale reads, and divergence.

## Instructor notes
- Emphasize CAP as a runtime tradeoff under partition, not a slogan.
- Use simple JSON logs to compare outcomes.
- Encourage students to reason about client expectations.

## Tools (free + open source)
- Docker Compose.
- Python 3.11+ or Go 1.21+.
- tc/netem (optional) for latency/partition simulation.

## Suggested reading & sources
- Gilbert & Lynch CAP proof: https://www.semanticscholar.org/paper/Brewer's-conjecture-and-the-feasibility-of-Gilbert-Lynch/65c3b6a6a9b5b9d12c9f6ddc0c3b5d98bbeb0e1b
- Brewer, “CAP twelve years later”: https://www.infoq.com/articles/cap-twelve-years-later/
