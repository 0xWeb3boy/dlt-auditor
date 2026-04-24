---
case_id: case_20240322_cea43099d
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2024-03-22
source_refs:
  - git:cea43099d291e409d58f84312d5e56d690cfc478
  - "src/ripple/consensus/Consensus.cpp:88"
  - "src/ripple/consensus/Consensus.cpp:134"
  - "src/ripple/consensus/Consensus.h:1158"
  - "src/ripple/consensus/Consensus.cpp:172"
bug_class: consensus-desync-hardening
impact_type:
  - consensus-integrity
  - node-desynchronization
confidence: medium
tags:
  - blockchain-core
  - consensus
  - validator-logic
  - desynchronization
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes a consensus timing/desynchronization condition where a peer could declare consensus with no received proposals and close a non-validated ledger. This is in a security-sensitive subsystem, but the provided evidence does not establish attacker control, exploitability, or a concrete security impact. Treat it as unclear rather than a confirmed security fix.

## Observed Patch Facts

1. In `src/ripple/consensus/Consensus.cpp`, the patch replaces `std::size_t minConsensusPct)` with `std::size_t minConsensusPct,`.

2. In `src/ripple/consensus/Consensus.cpp`, the patch replaces `<< previousAgreeTime.count();` with `<< previousAgreeTime.count() << " proposing? " << proposing`.

3. In `src/ripple/consensus/Consensus.h`, the patch replaces `vars << " (working seq: " << previousLedger_.seq() << ", "` with `vars << " consensuslog (working seq: " << previousLedger_.seq() << ", "`.

4. In `src/ripple/consensus/Consensus.cpp`, the patch replaces `currentFinished, currentProposers, false, parms.minCONSENSUS_PCT))` with `currentFinished,`.

## Project Context

The changed code sits primarily in `src/ripple/consensus`, `src/ripple`, which anchors the finding in the `consensus` area of the project. Historical context from `src/ripple/consensus/ConsensusParms.h`, `src/ripple/consensus/Validations.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/consensus/Validations.h`, `src/ripple/overlay/impl/PeerImp.cpp`. The strongest project-level identifiers around this patch are `std::size_t`, `consensus`, `parms`, and `count`. Nearby tests or test-like files include `src/ripple/beast/test/fail_counter.hpp`, `src/ripple/beast/unit_test/reporter.hpp`.

## Before/After Behavior

Before the patch, `checkConsensusReached` returned true immediately when `total == 0`, treating absence of proposals as consensus. After the patch, the helper receives a `reachedMax` argument, and the caller passes `currentAgreeTime > parms.ledgerMAX_CONSENSUS`, so the no-proposal case waits until the configured maximum consensus threshold. Additional logging changes improve diagnostics but are not the core fix.

# Root Cause

The zero-proposer branch was under-constrained: it allowed a local consensus decision based only on absence of proposals, which the commit message says could let a peer get ahead of proposers and desynchronize by closing a non-validated ledger.

## Walkthrough

1. A peer reaches the consensus decision point after the minimum establish phase duration.

2. Under the old behavior, if no proposals had arrived, `checkConsensusReached` saw `total == 0` and returned true.

3. That allowed the peer to advance locally despite not having observed peer proposals.

4. The commit message says this could happen under high transaction volume, a faster previous round, or delayed proposal receipt.

5. The stated consequence is peer desynchronization caused by closing a non-validated ledger.

6. The patch adds a `reachedMax` parameter to the consensus helper.

7. The caller supplies `currentAgreeTime > parms.ledgerMAX_CONSENSUS`, delaying no-proposal consensus until the maximum consensus threshold.

8. Logging was expanded to expose proposer and timing state for diagnostics.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/consensus/Consensus.cpp | 88 | Changes `checkConsensusReached` so a no-proposal state reaches consensus only after the maximum consensus time threshold rather than immediately. |
| src/ripple/consensus/Consensus.cpp | 134 | Adds consensus timing and proposer state to trace logging around the decision path. |
| src/ripple/consensus/Consensus.cpp | 172 | Passes `currentAgreeTime > parms.ledgerMAX_CONSENSUS` into `checkConsensusReached` for the moved-on-validator threshold check. |
| src/ripple/consensus/Consensus.h | 1158 | Adjusts consensus pause diagnostic logging; supporting observability rather than the core invariant change. |

## Code Snippets

## Snippet 1

Context: `src/ripple/consensus/Consensus.cpp:88` (changes a sensitive control or state-update path)

Before
```cpp
std::size_t total,
    bool count_self,
    std::size_t minConsensusPct)
{
    // If we are alone, we have a consensus
    if (total == 0)
        return true;
```
After
```cpp
std::size_t total,
    bool count_self,
    std::size_t minConsensusPct,
    bool reachedMax)
{
    // If we are alone for too long, we have consensus.
    // Delaying consensus like this avoids a circumstance where a peer
    // gets ahead of proposers insofar as it has not received any proposals.
```

## Snippet 2

Context: `src/ripple/consensus/Consensus.cpp:134` (changes a consensus- or validator-sensitive branch)

Before
```cpp
<< " validated=" << currentFinished
                    << " time=" << currentAgreeTime.count() << "/"
                    << previousAgreeTime.count();

    if (currentAgreeTime <= parms.ledgerMIN_CONSENSUS)
```
After
```cpp
<< " validated=" << currentFinished
                    << " time=" << currentAgreeTime.count() << "/"
                    << previousAgreeTime.count() << " proposing? " << proposing
                    << " minimum duration to reach consensus: "
                    << parms.ledgerMIN_CONSENSUS.count() << "ms"
                    << " max consensus time "
                    << parms.ledgerMAX_CONSENSUS.count() << "s"
                    << " minimum consensus percentage: "
```

## Snippet 3

Context: `src/ripple/consensus/Consensus.h:1158` (changes a consensus- or validator-sensitive branch)

Before
```c
std::stringstream vars;
    vars << " (working seq: " << previousLedger_.seq() << ", "
         << "validated seq: " << adaptor_.getValidLedgerIndex() << ", "
         << "am validator: " << adaptor_.validator() << ", "
```
After
```c
std::stringstream vars;
    vars << " consensuslog (working seq: " << previousLedger_.seq() << ", "
         << "validated seq: " << adaptor_.getValidLedgerIndex() << ", "
         << "am validator: " << adaptor_.validator() << ", "
```

## Snippet 4

Context: `src/ripple/consensus/Consensus.cpp:172` (changes a sensitive control or state-update path)

Before
```cpp
// to declare consensus?
    if (checkConsensusReached(
            currentFinished, currentProposers, false, parms.minCONSENSUS_PCT))
    {
        JLOG(j.warn()) << "We see no consensus, but 80% of nodes have moved on";
```
After
```cpp
// to declare consensus?
    if (checkConsensusReached(
            currentFinished,
            currentProposers,
            false,
            parms.minCONSENSUS_PCT,
            currentAgreeTime > parms.ledgerMAX_CONSENSUS))
    {
```

# Fix Pattern

Replace an immediate success condition in consensus with an explicit timing gate for the no-proposal case.

## How It Was Fixed

`checkConsensusReached` was changed to accept `bool reachedMax`, and the caller now passes whether `currentAgreeTime` exceeds `parms.ledgerMAX_CONSENSUS`. The zero-proposer path no longer implies immediate consensus; it depends on that maximum-time condition. Supporting trace and diagnostic logging was also updated.

# Why It Matters

1. Consensus code is security-sensitive, so desynchronization fixes deserve review.

2. The patch addresses premature local ledger closure with no proposals.

3. The evidence supports a timing/desync correctness fix.

4. The evidence does not prove malicious triggerability or concrete exploit impact.

# Evidence Notes

Grounded evidence comes from `src/ripple/consensus/Consensus.cpp`: the old `total == 0` immediate return, the new `reachedMax` parameter, and the caller passing `currentAgreeTime > parms.ledgerMAX_CONSENSUS`. The commit message states the old behavior could desynchronize a peer and close a non-validated ledger. However, there is no evidence of attacker-controlled timing, message validation failure, double spend, theft, ledger forgery, or network-wide consensus compromise. Protocol security invariant: A peer should not declare consensus solely because it has received no peer proposals at the consensus decision point; in that no-proposal case, the decision should wait until the configured maximum consensus time threshold is reached. Verification notes: The patch does not prove a malicious peer can deliberately trigger the timing condition. The patch does not prove transaction theft, double spend, or ledger forgery. The patch does not show a network-wide consensus failure, only a peer desync / premature local close case. The logging changes alone are not security-relevant. The evidence does not show changes to proposal authentication or peer message validation. Downgraded from confirmed security-hardening to unclear. Kept subsystem as consensus, not p2p-networking. Excluded logging changes as root cause. Set `keep_in_security_corpus` to false because the vulnerability thesis is not established by the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-desync-hardening`
Final impact type: `consensus-integrity, node-desynchronization`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, validator-logic, desynchronization, security-hardening`

The evidence supports a conservative security-hardening classification. The patch changes consensus decision logic so a peer no longer treats receiving zero proposals as immediate consensus; it must wait until the configured maximum consensus time. In a blockchain consensus subsystem, preventing premature local consensus and closure of a non-validated ledger is a security-sensitive tightening even though the evidence does not prove attacker control, exploitability, or network-wide compromise.

## Security Evidence

1. Consensus code previously returned true immediately when total proposals were zero.
2. The commit message states this could cause a peer to desync and close a non-validated ledger.
3. The fix adds a reachedMax timing gate before declaring consensus with no proposals.
4. The caller now passes currentAgreeTime > ledgerMAX_CONSENSUS into the consensus-reached check.
5. The changed path is validator/consensus decision logic, not only diagnostics.

## Missing Evidence

1. No proof that an attacker can deliberately trigger delayed proposal delivery or the timing condition.
2. No demonstrated theft, double spend, ledger forgery, or consensus safety break.
3. No evidence of network-wide consensus compromise rather than an individual peer desync.
4. No advisory, CVE, or explicit security disclosure is provided.

## Claim Boundaries

1. Classify as hardening, not a confirmed vulnerability fix.
2. The supported claim is premature no-proposal consensus causing possible peer desynchronization.
3. Do not claim attacker-controlled exploitation from the supplied evidence.
4. Do not treat logging-only changes as part of the security fix.
5. Do not infer transaction integrity loss beyond the stated non-validated ledger closure/desync behavior.
