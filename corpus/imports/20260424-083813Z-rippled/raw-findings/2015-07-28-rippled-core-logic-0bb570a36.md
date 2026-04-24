---
case_id: case_20150728_0bb570a36
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: core-logic
confidence: medium
source_quality: high
date: 2015-07-28
source_refs:
  - git:0bb570a36d29e1eedd96ebda020cbbf9afb96b7a
  - "src/ripple/app/ledger/impl/LedgerMaster.cpp:169"
  - "src/ripple/ledger/View.h:170"
  - "src/ripple/app/misc/NetworkOPs.cpp:1263"
  - "src/ripple/app/misc/NetworkOPs.cpp:1285"
bug_class: consensus-ledger-compatibility
impact_type:
  - state-consistency
  - consensus-safety
tags:
  - blockchain-core
  - consensus
  - ledger-compatibility
  - state-consistency
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds ledger compatibility checks around consensus ledger handling. The strongest visible evidence is in `NetworkOPs::checkLastClosedLedger`, where the node now retrieves or acquires the proposed consensus ledger and refuses to switch to it if `LedgerMaster::isCompatible` reports it is incompatible with the validated ledger. This supports a consensus-safety hardening classification, but the supplied evidence does not prove a concrete exploit, fork, or funds-impacting vulnerability.

## Observed Patch Facts

1. In `src/ripple/app/ledger/impl/LedgerMaster.cpp`, the patch replaces `int getPublishedLedgerAge ()` with `bool isCompatible (Ledger::pointer ledger,`.

2. In `src/ripple/ledger/View.h`, the patch replaces `//------------------------------------------------------------------------------` with `/** Return false if the test ledger is provably incompatible`.

3. In `src/ripple/app/misc/NetworkOPs.cpp`, the patch replaces `m_journal.warning << "We are not running on the consensus ledger";` with `Ledger::pointer consensus = m_ledgerMaster.getLedgerByHash (closedLedger);`.

4. In `src/ripple/app/misc/NetworkOPs.cpp`, the patch replaces `Ledger::pointer consensus = m_ledgerMaster.getLedgerByHash (closedLedger);` with `if (consensus)`.

## Project Context

The changed code sits primarily in `src/ripple/app/ledger/impl`, `src/ripple/app/ledger`, `src/ripple/ledger`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/ripple/app/ledger/impl/LedgerConsensusImp.h`, `src/ripple/app/ledger/impl/LedgerConsensusImp.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/app/ledger/LedgerMaster.h`, `src/ripple/app/ledger/impl/LedgerConsensusImp.h`. The strongest project-level identifiers around this patch are `Ledger::pointer`, `consensus`, `beast::Journal::Stream`, and `InboundLedger::fcCONSENSUS`. Nearby tests or test-like files include `src/ripple/app/ledger/tests/Ledger_test.cpp`, `src/ripple/app/ledger/tests/common_ledger.h`.

## Before/After Behavior

Before the patch, the shown network path could proceed toward switching to the network closed ledger without the visible compatibility check against the node's validated ledger chain. After the patch, the candidate consensus ledger is retrieved or acquired, checked through `LedgerMaster::isCompatible`, and rejected for switching when incompatible. `View.h` also declares shared `areCompatible` helpers, including a form for cases where the valid ledger is identified by hash and index rather than already acquired.

# Root Cause

The evidenced root cause is an insufficient or missing compatibility gate in ledger switching logic. A candidate consensus ledger could reach the switch decision path without the shown code first proving compatibility with the node's validated ledger chain.

## Walkthrough

1. `View.h` declares `areCompatible` helpers that return false when a test ledger is provably incompatible with a valid ledger.

2. `LedgerMaster.cpp` adds `isCompatible`, which obtains the current validated ledger and compares a candidate ledger through `areCompatible` when possible.

3. `NetworkOPs.cpp` now retrieves the proposed consensus ledger by hash or acquires it through `InboundLedger::fcCONSENSUS`.

4. Before switching, `NetworkOPs.cpp` calls `m_ledgerMaster.isCompatible(consensus, ..., "Not switching")`.

5. If the candidate consensus ledger is incompatible, the code blocks the switch by resetting `networkClosed` to the local closed ledger hash.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/ledger/impl/LedgerMaster.cpp | 169 | Adds LedgerMaster::isCompatible gate comparing a candidate ledger against the current validated ledger. |
| src/ripple/ledger/View.h | 170 | Defines ledger compatibility checks for both acquired ledgers and hash/index-based validation when the ledger is not yet acquired. |
| src/ripple/app/misc/NetworkOPs.cpp | 1263 | Acquires or retrieves the network consensus ledger before deciding whether it is safe to switch. |
| src/ripple/app/misc/NetworkOPs.cpp | 1285 | Blocks switching to a consensus ledger when LedgerMaster reports it is incompatible with the validated chain. |

## Code Snippets

## Snippet 1

Context: `src/ripple/app/ledger/impl/LedgerMaster.cpp:169` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
}

    int getPublishedLedgerAge ()
    {
```
After
```cpp
}

    bool isCompatible (Ledger::pointer ledger,
        beast::Journal::Stream s, const char* reason)
    {
        auto validLedger = getValidatedLedger();

        if (validLedger &&
```

## Snippet 2

Context: `src/ripple/ledger/View.h:170` (changes how canonical state is encoded, returned, or reconstructed)

Before
```c
}

//------------------------------------------------------------------------------
//
```
After
```c
}

/** Return false if the test ledger is provably incompatible
    with the valid ledger, that is, they could not possibly
    both be valid. Use the first form if you have both ledgers,
    use the second form if you have not acquired the valid ledger yet
*/
bool areCompatible (ReadView const& validLedger, ReadView const& testLedger,
```

## Snippet 3

Context: `src/ripple/app/misc/NetworkOPs.cpp:1263` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
return false;

    m_journal.warning << "We are not running on the consensus ledger";
    m_journal.info << "Our LCL: " << getJson (*ourClosed);
```
After
```cpp
return false;

    Ledger::pointer consensus = m_ledgerMaster.getLedgerByHash (closedLedger);

    if (!consensus)
        consensus = getApp().getInboundLedgers().acquire (
            closedLedger, 0, InboundLedger::fcCONSENSUS);
```

## Snippet 4

Context: `src/ripple/app/misc/NetworkOPs.cpp:1285` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
setMode (omCONNECTED);

    Ledger::pointer consensus = m_ledgerMaster.getLedgerByHash (closedLedger);

    if (!consensus)
        consensus = getApp().getInboundLedgers().acquire (
            closedLedger, 0, InboundLedger::fcCONSENSUS);
```
After
```cpp
setMode (omCONNECTED);

    if (consensus)
    {
```

# Fix Pattern

Centralize ledger compatibility checking and call it before switching to a candidate consensus ledger.

## How It Was Fixed

The patch introduces shared compatibility APIs, wraps them through `LedgerMaster::isCompatible`, and applies that wrapper in the network ledger switching path before accepting the candidate consensus ledger.

# Why It Matters

1. Reduces the chance that a node follows a ledger outside its validated chain.

2. Makes ledger switching depend on an explicit compatibility check.

3. Hardens consensus behavior, even though exploitability is not shown.

# Evidence Notes

Supported by visible changes in `src/ripple/app/ledger/impl/LedgerMaster.cpp`, `src/ripple/ledger/View.h`, and `src/ripple/app/misc/NetworkOPs.cpp`. The commit subject mentions broader validation and quorum protection, but the provided hunks do not show the quorum implementation and only directly support the compatibility/switching claims. Claims about serialization, RPC boundaries, cryptographic failure, transaction theft, or demonstrated remote exploitation are unsupported. Protocol security invariant: A rippled node should not switch to, follow, or validate a candidate ledger that is provably incompatible with its current validated ledger chain. Verification notes: The patch does not prove remote exploitability by itself. The patch does not show a demonstrated consensus fork or validation failure in the provided evidence. The patch does not establish transaction theft, signature bypass, or cryptographic breakage. The quorum protection is named in the commit subject, but the provided hunks do not show its implementation details. No direct exploit path is established by the supplied evidence. No demonstrated fork or validation failure is shown. Quorum-protection details are not visible in the provided hunks. Classification is security hardening rather than a confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-ledger-compatibility`
Final impact type: `state-consistency, consensus-safety`
Final tags: `blockchain-core, consensus, ledger-compatibility, state-consistency, security-hardening`

The supplied evidence supports retaining this as security hardening, not as a concrete vulnerability fix. The patch adds explicit compatibility checks before validating or switching to a candidate consensus ledger, and the commit subject frames the change around avoiding incompatible ledgers and quorum risk. The evidence does not prove exploitation, funds impact, cryptographic failure, or an observed consensus fork, so stronger security-fix claims would be overconfident.

## Security Evidence

1. Adds LedgerMaster::isCompatible to compare a candidate ledger against the current validated ledger.
2. Declares areCompatible helpers for ledgers that could not both be valid.
3. NetworkOPs retrieves or acquires the proposed consensus ledger before switching decisions.
4. NetworkOPs refuses to switch when the candidate consensus ledger is incompatible with the validated chain.
5. Commit subject explicitly says not to validate or switch to incompatible ledgers and to protect against small quorum.

## Missing Evidence

1. No demonstrated exploit path is provided.
2. No shown consensus fork, validation failure, or attacker-controlled input path is proven.
3. No funds loss, transaction theft, signature bypass, or cryptographic break is evidenced.
4. The quorum-protection implementation is named in the subject but not shown in the supplied hunks.

## Claim Boundaries

1. Classify as consensus-safety hardening rather than a confirmed exploitable vulnerability.
2. Do not claim serialization or canonical state representation as the root bug class from the supplied evidence.
3. Do not claim concrete client divergence beyond the general risk reduced by refusing incompatible ledgers.
4. Do not infer cryptographic or replay-sensitive failure from the patch alone.
