# Lab 09 — Raft intuition + library glimpse

## Learning goals
- Explain leader election and log replication at a high level.
- Compare Raft’s structure to Paxos’s roles.
- Reason about why odd-sized clusters are preferred.

## In-class walkthrough
1. **Raft paper tour**
   - Leader election, log replication, membership changes.
2. **Leader election mini-sim**
   - Nodes pick randomized timeouts.
   - Heartbeats reset follower timers.
3. **Library glimpse**
   - Show etcd/raft API surface and usage patterns.

## Student deliverable
- Either a leader-election-only simulator **or** a worksheet answering invariants and failure cases.

## Instructor notes
- Emphasize that strong leadership makes reasoning easier.
- Use diagrams for terms/votes/heartbeats.
- Keep the mini-sim simple: focus on intuition.

## Tools (free + open source)
- Python 3.11+ or Go 1.21+.
- etcd raft library (for reading or a tiny demo).

## Suggested reading & sources
- Raft paper: https://raft.github.io/raft.pdf
- etcd raft library: https://pkg.go.dev/go.etcd.io/raft/v3
- etcd overview: https://etcd.io/docs/
