# Lab 08 — One round of Paxos (single-decree)

## Learning goals
- Identify proposer, acceptor, and learner roles.
- Implement prepare/promise and accept/accepted phases.
- Reason about safety vs liveness and quorum intersection.

## In-class walkthrough
1. **Single-decree Paxos**
   - Build a simulator with in-memory message passing.
2. **Phase 1: prepare/promise**
   - Show how higher proposal numbers supersede lower ones.
3. **Phase 2: accept/accepted**
   - Learner decides value after quorum accept.
4. **Failure scenarios**
   - Competing proposers.
   - Dropped messages.
   - Acceptor restart (state persistence discussion).

## Student deliverable
- A Paxos single-decree simulator with deterministic tests.
- Scripted scenarios demonstrating safety under failures.

## Instructor notes
- Stress why proposal numbers must be unique and increasing.
- Use deterministic test seeds to make grading reproducible.
- Discuss persistence and what happens after acceptor restart.

## Tools (free + open source)
- Python 3.11+ or Go 1.21+.
- pytest or Go test.

## Suggested reading & sources
- Lamport, “Paxos Made Simple”: https://lamport.azurewebsites.net/pubs/paxos-simple.pdf
