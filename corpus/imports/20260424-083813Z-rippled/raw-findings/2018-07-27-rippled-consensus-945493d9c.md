---
case_id: case_20180727_945493d9c
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: consensus
source_quality: high
date: 2018-07-27
source_refs:
  - git:945493d9cfebadc77974889925eaa053f369a184
  - "src/ripple/app/ledger/impl/BuildLedger.cpp:85"
  - "src/ripple/app/consensus/RCLConsensus.cpp:714"
  - "src/ripple/app/consensus/RCLConsensus.cpp:89"
  - "src/ripple/app/consensus/RCLConsensus.cpp:113"
bug_class: censorship-detection-observability
impact_type:
  - censorship-detection
  - security-monitoring
  - auditability
confidence: medium
tags:
  - blockchain-core
  - consensus
  - censorship-detection
  - security-monitoring
  - observability
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best classified as security hardening for censorship observability in rippled consensus processing. The commit message explicitly says it adds an automated censorship detector, and the supplied code evidence shows new detector state plus plumbing for failed and retriable transaction outcomes. The evidence does not establish a pre-existing exploitable vulnerability, consensus-safety bug, cryptographic flaw, replay bug, authorization issue, fund-loss condition, or censorship prevention mechanism.

## Observed Patch Facts

1. In `src/ripple/app/ledger/impl/BuildLedger.cpp`, the patch replaces `@param txns Consensus transactions to apply` with `@param txns the set of transactions to apply,`.

2. In `src/ripple/app/consensus/RCLConsensus.cpp`, the patch replaces `RCLTxSet const& txns,` with `CanonicalTXSet& retriableTxs,`.

3. In `src/ripple/app/consensus/RCLConsensus.cpp`, the patch replaces `RCLConsensus::Adaptor::acquireLedger(LedgerHash const& ledger)` with `RCLConsensus::Adaptor::acquireLedger(LedgerHash const& hash)`.

4. In `src/ripple/app/consensus/RCLConsensus.cpp`, the patch replaces `assert(!buildLCL->open() && buildLCL->isImmutable());` with `assert(!built->open() && built->isImmutable());`.

## Project Context

The changed code sits primarily in `src/ripple/app/ledger/impl`, `src/ripple/app/ledger`, `src/ripple/app/consensus`, which anchors the finding in the `consensus` area of the project. Historical context from `src/ripple/app/ledger/impl/LedgerMaster.cpp`, `src/ripple/app/ledger/impl/LedgerCleaner.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/app/consensus/RCLConsensus.h`, `src/ripple/app/ledger/impl/LedgerMaster.cpp`. The strongest project-level identifiers around this patch are `buildLCL`, `ledger`, `param`, and `built`.

## Before/After Behavior

Before the patch, the supplied evidence shows the ledger build path exposing consensus transactions and retriable transactions, but does not show cross-round tracking of transactions omitted from validated ledgers. After the patch, the build path distinguishes applied count, failed transaction IDs, and retriable transactions, and consensus code includes a new RCLCensorshipDetector with transaction-ID tracking state. Some acquireLedger changes are identifier renames and surrounding round-transition context, not evidence of the core security change.

# Root Cause

The grounded root cause is an observability gap: the provided evidence does not show prior machinery for tracking transaction IDs across ledger rounds to warn when transactions expected by the server were repeatedly omitted. This is not enough to claim a consensus failure or exploitable vulnerability.

## Walkthrough

1. Consensus ledger construction processes candidate transactions during RCLConsensus::Adaptor::buildLCL.

2. Before the patch, the shown signature accepted consensus transactions and retriable transactions, without a failed transaction ID set in that interface.

3. BuildLedger.cpp is changed to document separate outcomes: applied transaction count, failed transactions, and retryable transactions left in the transaction set.

4. RCLConsensus::Adaptor::buildLCL is changed to receive CanonicalTXSet& retriableTxs and std::set<TxID>& failedTxs.

5. RCLCensorshipDetector.h adds detector state keyed by TxID and ledger sequence, supporting cross-round omission tracking.

6. The commit message states the detector warns with increasing severity when transactions that should have been included remain absent after several rounds.

7. The acquireLedger hunks mostly support surrounding consensus-round context and should not be treated as an independent vulnerability fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/consensus/RCLCensorshipDetector.h | 30 | new detector state tracking transaction IDs across ledger sequences for omission warnings |
| src/ripple/app/consensus/RCLConsensus.cpp | 708 | consensus ledger build path now passes retriable transactions and failed transaction IDs into the ledger-building flow |
| src/ripple/app/ledger/impl/BuildLedger.cpp | 79 | ledger transaction application path documents and returns applied count while separating failed and retriable transactions |
| src/ripple/app/consensus/RCLConsensus.cpp | 83 | ledger acquisition path used by consensus before notifying inbound transaction tracking of a new round |

## Code Snippets

## Snippet 1

Context: `src/ripple/app/ledger/impl/BuildLedger.cpp:85` (changes bounds, limits, or capacity handling)

Before
```cpp
@param app Handle to application
  @param txns Consensus transactions to apply
  @param view Ledger to apply to
  @param buildLCL Ledger to check if transaction already exists
  @param j Journal for logging
  @return Any retriable transactions
*/
```
After
```cpp
@param app Handle to application
  @param txns the set of transactions to apply,
  @param failed set of transactions that failed to apply
  @param view ledger to apply to
  @param j Journal for logging
  @return number of transactions applied; transactions to retry left in txns
*/
```

## Snippet 2

Context: `src/ripple/app/consensus/RCLConsensus.cpp:714` (changes signature or replay validation logic)

Before
```cpp
RCLConsensus::Adaptor::buildLCL(
    RCLCxLedger const& previousLedger,
    RCLTxSet const& txns,
    NetClock::time_point closeTime,
    bool closeTimeCorrect,
    NetClock::duration closeResolution,
    std::chrono::milliseconds roundTime,
    CanonicalTXSet& retriableTxs)
```
After
```cpp
RCLConsensus::Adaptor::buildLCL(
    RCLCxLedger const& previousLedger,
    CanonicalTXSet& retriableTxs,
    NetClock::time_point closeTime,
    bool closeTimeCorrect,
    NetClock::duration closeResolution,
    std::chrono::milliseconds roundTime,
    std::set<TxID>& failedTxs)
```

## Snippet 3

Context: `src/ripple/app/consensus/RCLConsensus.cpp:89` (changes signature or replay validation logic)

Before
```cpp
boost::optional<RCLCxLedger>
RCLConsensus::Adaptor::acquireLedger(LedgerHash const& ledger)
{
    // we need to switch the ledger we're working from
    auto buildLCL = ledgerMaster_.getLedgerByHash(ledger);
    if (!buildLCL)
    {
```
After
```cpp
boost::optional<RCLCxLedger>
RCLConsensus::Adaptor::acquireLedger(LedgerHash const& hash)
{
    // we need to switch the ledger we're working from
    auto built = ledgerMaster_.getLedgerByHash(hash);
    if (!built)
    {
```

## Snippet 4

Context: `src/ripple/app/consensus/RCLConsensus.cpp:113` (changes signature or replay validation logic)

Before
```cpp
}

    assert(!buildLCL->open() && buildLCL->isImmutable());
    assert(buildLCL->info().hash == ledger);

    // Notify inbound transactions of the new ledger sequence number
    inboundTransactions_.newRound(buildLCL->info().seq);
```
After
```cpp
}

    assert(!built->open() && built->isImmutable());
    assert(built->info().hash == hash);

    // Notify inbound transactions of the new ledger sequence number
    inboundTransactions_.newRound(built->info().seq);
```

# Fix Pattern

Add monitoring-oriented consensus plumbing: separate transaction application outcomes and maintain detector state across rounds so repeated omission can be warned about.

## How It Was Fixed

The patch adds RCLCensorshipDetector to the consensus subsystem and threads failed and retriable transaction information through ledger construction. This gives consensus-side code enough information to distinguish failed application from continued omission and to track omitted transaction IDs across ledger sequences for warning purposes.

# Why It Matters

1. Improves detection of possible transaction censorship.

2. Makes transaction outcome accounting less ambiguous.

3. Supports auditability when expected transactions repeatedly fail to appear.

4. Does not prove censorship prevention or a fixed exploitable bug.

# Evidence Notes

Strongest evidence is the commit message and the added RCLCensorshipDetector state in src/ripple/app/consensus/RCLCensorshipDetector.h, plus interface changes in RCLConsensus.cpp and BuildLedger.cpp that separate failed and retriable transaction outcomes. The supplied evidence does not include detector warning logic or test excerpts, though the file list includes RCLCensorshipDetector_test.cpp. Claims about cryptography, replay protection, access control, fund loss, or consensus divergence are unsupported. Protocol security invariant: While a server is in sync, transactions that it believes should have been included in validated ledgers should be accounted for as included, failed, retriable, or repeatedly omitted so possible censorship can be detected and warned about. The evidence supports detectability and warning, not automatic prevention or consensus-rule enforcement. Verification notes: The patch does not prove that censorship is prevented. The patch does not prove an exploitable pre-existing vulnerability. The patch does not show a consensus rule change requiring validators to include specific transactions. The patch does not show a cryptographic signature or replay bug fix. The patch does not prove ledger divergence, fund loss, or authorization bypass. The acquireLedger evidence appears partly to be variable renaming and should not be over-weighted as a security fix. Classified as security hardening, not a confirmed vulnerability fix. Downgraded confidence from high to medium because only selected excerpts are provided. Kept in security corpus because the commit and code evidence directly concern censorship detection. Excluded acquireLedger renaming from the core fix rationale. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `censorship-detection-observability`
Final impact type: `censorship-detection, security-monitoring, auditability`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, censorship-detection, security-monitoring, observability`

The supplied evidence supports retaining this as security hardening, not as a concrete security bug fix. The commit message explicitly adds an automated detector for transaction censorship attempts, and the patch evidence shows consensus and ledger-build plumbing for failed and retriable transaction outcomes plus a new RCLCensorshipDetector state object. However, the excerpts do not prove a pre-existing exploitable vulnerability, consensus-safety failure, replay flaw, cryptographic issue, or censorship prevention mechanism.

## Security Evidence

1. Commit message directly frames the change as detecting transaction censorship attempts in XRP Ledger consensus.
2. RCLConsensus.h includes RCLCensorshipDetector, and traced context shows detector state keyed by TxID and ledger sequence.
3. buildLCL and buildLedger interfaces are changed to distinguish retriable and failed transactions, supporting omission tracking.
4. The detector is warning/observability oriented, which is security-relevant for censorship resistance.

## Missing Evidence

1. No excerpt shows a concrete exploit, attack reproduction, or prior vulnerability condition.
2. No evidence shows consensus rules were changed to prevent censorship or force transaction inclusion.
3. No evidence supports cryptographic, replay-protection, authorization, or fund-loss claims.
4. The acquireLedger hunks appear to be mostly variable renaming and do not independently establish security impact.

## Claim Boundaries

1. Classify as censorship-detection hardening rather than consensus-safety bug fix.
2. Do not claim censorship is prevented; only detection and warning are supported.
3. Do not claim consensus failure, ledger divergence, or validator compromise from the supplied patch.
4. Do not rely on generated reason labels such as access control, cryptographic, or replay-sensitive changes unless supported by shown code.
