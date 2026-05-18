---
id: monad-c4-2025-09-m-06
source: Code4rena 2025-09 Monad report
source_report: /testing/learning/2025-09-monad-report.md
report_date: 2026-02-26
audit_start_date: 2025-09-16
severity: medium
---

## [[M-06] Vote timer callback uses potentially stale timer round instead of actual vote round, causing vote misrouting](https://code4rena.com/audits/2025-09-monad/submissions/F-790)

*Submitted by [ZeroEx](https://code4rena.com/audits/2025-09-monad/submissions/S-782), also found by [JuggerNaut63](https://code4rena.com/audits/2025-09-monad/submissions/S-360) and [minato7namikazi](https://code4rena.com/audits/2025-09-monad/submissions/S-210)*

`bft/monad-consensus-state/src/lib.rs` [#L1061](https://github.com/code-423n4/2025-09-monad/blob/bcc1592fcf38f47a417190b1ea159934926f1f12/bft/monad-consensus-state/src/lib.rs#L1061)

In `handle_vote_timer()`, when a vote timer fires, the callback extracts the stored vote but uses the **timer’s round parameter** instead of the **vote’s actual round** when calling `send_vote_and_reset_timer()`:

```rust
pub fn handle_vote_timer(
    &mut self,
    round: Round,  // ← Timer's round
) -> Vec<ConsensusCommand<...>> {
    let Some(OutgoingVoteStatus::VoteReady(v)) = self.consensus.scheduled_vote else {
        self.consensus.scheduled_vote = Some(OutgoingVoteStatus::TimerFired);
        return vec![];
    };

    self.send_vote_and_reset_timer(round, v)  // ← Uses timer's round, not v.round
}
```

In `send_vote_and_reset_timer()`, vote recipients are computed from the **passed round parameter**:

```rust
let next_leader = get_leader(round + Round(1));  // ← Derives from parameter
let current_leader = get_leader(round);           // ← Derives from parameter
```

Vote timers are scheduled one round ahead when sending votes:

```rust
cmds.push(ConsensusCommand::ScheduleVote {
    round: round + Round(1),  // ← Schedules for next round
    duration: vote_pace,
});
```

### Trigger Scenario

1. Node votes on round R, schedules timer for round R+1
2. Before timer fires, node rapidly advances through R+1 → R+2 (via QC messages and/or consecutive proposals)
3. Node processes proposal for R+2, updates `scheduled_vote = VoteReady(v_R+2)`
4. **Stale timer for R+1 fires**
5. `handle_vote_timer(R+1)` extracts vote `v_R+2` but passes `round = R+1` to `send_vote_and_reset_timer()`

### Impact

**Vote Misrouting:**

- **Advance by 2 rounds**: Vote sent to current leader but not next leader

  - Next-round leader (R+3) never receives vote for R+2
  - Slows QC(R+2) formation → increases timeout risk
- **Advance by 3+ rounds** *(more severe)*: Vote sent to neither current nor next leader

  - Current leader (R+N) doesn’t receive vote for R+N
  - **Completely blocks QC formation** for round R+N
  - Forces timeout and TC generation
  - Severely degrades liveness

**Cascading Timer Drift:**

- Next timer scheduled for round R+2 (should be R+3)
- Subsequent stale timers compound the misrouting

Can occur during fast network conditions, burst QC message processing, or catch-up after brief partitions, where rapid round advancement causes stale vote timers to fire after consensus has progressed multiple rounds ahead.

[View detailed Proof of Concept](https://code4rena.com/audits/2025-09-monad/submissions/F-790)

---
