# Prompt Family: Timer Retry And Service Liveness

## Use This For

- Block producers, consensus services, importers, relayers, sync loops, mempool workers, background tasks, and health-managed services.
- Interval timers, retry loops, watchdogs, stream select loops, service continuation flags, and error handling.
- Bugs where one expected error permanently stops progress without stopping the process clearly.

## Prompt

```text
Hunt for liveness bugs where a long-running service schedules its next wakeup, retry, heartbeat, or cleanup only on the success path, while an expected error path returns early and leaves the service alive but idle.

Focus on:
- interval block production and consensus timers
- manual vs automatic trigger modes
- relayer polling and sync retries
- peer request retry/backoff loops
- mempool selection and block-building loops
- health/continuation flags that allow the node to keep running after a subservice stops making progress

Search patterns:
- timer deadline, sleep, interval, alarm, or wakeup reset after fallible work
- `?`, early `return`, `break`, or `continue` before rescheduling/releasing/rearming
- cleanup/reschedule code at the bottom of a function rather than in a guard/finally/drop path
- select loops where one branch errors and exits the branch without arranging the next event
- expected execution/import/validation failures treated like fatal service errors or silent no-ops
- manual request paths that recover but automatic interval paths do not, or vice versa
- "continue on error" settings that keep the process alive while a producer/relayer/sync task has stopped
- timers overwritten or min-merged differently in manual and interval modes
- retry state updated before fallible work but not reverted on failure
- queue items removed before work succeeds and never restored or marked terminal on error

Questions to answer:
1. What event schedules the next unit of work?
2. Is the next event scheduled before or after fallible work?
3. For every `?` or early return, who re-arms the timer/retry/wakeup?
4. Is the error expected from untrusted input, normal resource exhaustion, or local operator action?
5. Does the service stop loudly, restart, mark unhealthy, or keep running without progress?
6. Are manual and automatic modes equivalent after failure?
7. Does a continuation flag hide a stalled critical subservice from operators or dependent services?
8. Can a single bad block, event, transaction, peer response, or request wedge the loop indefinitely?

Severity guidance:
- Low to Medium for single-node liveness stalls.
- Raise when the same deterministic input can stall a quorum, block production, bridge processing, or network-wide progress.
```
