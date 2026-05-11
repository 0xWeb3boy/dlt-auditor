# Prompt Family: Timer Callback Coordinate Regressions

## Use This For

- Consensus vote/proposal/timeout timers.
- Async callbacks where a queued object has its own round/view/epoch/request coordinate.
- Bugs where a timer's stale coordinate is passed into a send/reset/routing helper after the stored object has moved.

## Prompt

```text
Hunt specifically for timer and callback coordinate regressions.

Build a matrix of every consensus timer, vote timer, proposal timer, timeout-certificate timer, request retry timer, peer timeout, and async callback:
- where it is scheduled
- what coordinate is captured in the timer event
- what object is stored while waiting
- what can replace that stored object before the timer fires
- what handler runs when the timer fires
- what coordinate the handler passes into the sink
- what the sink derives from that coordinate

High-signal target shape:
- A node stores `VoteReady(v)` or equivalent queued vote for round R.
- The timer event carries another round, such as R+1 or an older callback round.
- Before the callback fires, consensus advances and replaces the stored vote with a vote for R+N.
- The callback extracts the current stored vote but calls `send_vote_and_reset_timer(timer_round, v)` or equivalent.
- The sink computes current leader, next leader, retry target, or next scheduled timer from the stale callback round rather than `v.round`.

Required searches:
- Search for `handle_*timer`, `ScheduleVote`, `VoteReady`, `TimerFired`, `scheduled_vote`, `send_vote`, `reset_timer`, `vote_pace`, `get_leader`, `Round(`, `Timeout`, and callback event enums.
- Search both event-routing code and consensus-state methods. The stale coordinate can be introduced in the outer event enum and consumed in an inner state helper.
- Read tests that assert scheduled vote round. Check whether tests ever fire an old timer after `scheduled_vote` was replaced by a newer vote.

Questions to answer:
1. Does the callback drop stale events whose coordinate no longer matches the queued object?
2. Does the send/reset sink need the queued object's coordinate or the timer event coordinate?
3. What route changes when using the stale coordinate: current leader, next leader, broadcast group, timer reschedule, or timeout state?
4. Can fast QC processing, catch-up, replay, or partitions replace the queued object before an older timer fires?
5. Is the bug local liveness, vote misrouting, timeout amplification, or broader consensus disruption?

False-positive filters:
- A timer carrying R+1 is not automatically wrong if the sink explicitly derives from the queued vote's R or verifies equality before sending.
- A stale timer is harmless only if it is dropped or cannot extract a newer stored object.
- Do not reject because the vote itself is signed for the right round. Routing and rescheduling can still use the wrong coordinate.

Output requirements:
- Include a timer/callback matrix.
- Include a candidate if any handler extracts a queued object and passes the callback coordinate to a sink without equality checking.
- Include a minimal rapid-progress sequence showing coordinate divergence.
```
