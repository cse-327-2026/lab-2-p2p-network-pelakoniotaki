# Lab 03 — Messaging patterns with ZeroMQ

## Learning goals
- Compare messaging patterns: REQ/REP, PUB/SUB, PUSH/PULL.
- Understand backpressure, buffering, and message loss tradeoffs.
- Contrast brokered vs brokerless designs.

## In-class walkthrough
1. **REQ/REP task server**
   - Implement a worker that answers jobs with a result.
   - Show that REQ/REP enforces strict request/response ordering.
2. **PUB/SUB event stream**
   - Implement a publisher that emits timestamps.
   - Subscribers filter by topic prefix.
3. **Failure experiments**
   - Slow subscriber and dropped messages.
   - Reconnect storm (kill/restart subscribers).

## Student deliverable
- Minimal “event bus” demo with a publisher and N subscribers.
- Each subscriber reports received count and duplicate count.

## Instructor notes
- Emphasize that PUB/SUB is best-effort: missing messages is normal.
- Show how buffering can hide backpressure problems.
- Reinforce why messaging “feels different” than RPC.

## Tools (free + open source)
- ZeroMQ (`pyzmq` or `czmq`).
- Python 3.11+ or Go 1.21+.

## Suggested reading & sources
- ØMQ Guide (patterns): https://zguide.zeromq.org/
- ZeroMQ API reference: https://zeromq.org/languages/
