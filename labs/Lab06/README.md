# Lab 06 — Fault tolerance patterns

## Learning goals
- Understand at-least-once vs at-most-once semantics.
- Implement retries with backoff and timeouts.
- Use idempotency keys to deduplicate requests.
- Apply circuit breakers and bulkheads to limit blast radius.

## In-class walkthrough
1. **Add retries to Lab 2 client**
   - Respect gRPC deadlines and retry idempotent calls.
2. **Idempotency keys**
   - Add `idempotency_key` to `Put` request.
   - Store recent keys to drop duplicates.
3. **Circuit breaker demo**
   - Simulate a failing shard and open the breaker.
   - Show half-open recovery.

## Student deliverable
- A resilient client wrapper with retries + backoff.
- Tests that verify duplicate suppression and breaker behavior.

## Instructor notes
- Emphasize “retry storms” and why jitter matters.
- Encourage clear metrics/logs for retry outcomes.
- Discuss when not to retry (non-idempotent operations).

## Tools (free + open source)
- gRPC client libs.
- pytest or Go test.
- tenacity (Python) or backoff libraries (optional).

## Suggested reading & sources
- gRPC deadlines and timeouts: https://grpc.io/docs/guides/concepts/
- Google SRE book (retries/backoff overview): https://sre.google/sre-book/handling-overload/
