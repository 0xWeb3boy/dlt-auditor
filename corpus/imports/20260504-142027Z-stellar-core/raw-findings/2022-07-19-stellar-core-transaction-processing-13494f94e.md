---
case_id: case_20220719_13494f94e
project: stellar-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2022-07-19
source_refs:
  - git:13494f94e2f87e33a63b72cd5a19b26951ac8581
  - "src/herder/TxSetFrame.cpp:522"
  - "src/herder/TxSetFrame.cpp:848"
bug_class: canonical-order-validation-hardening
impact_type:
  - consensus-integrity-hardening
  - input-validation-hardening
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - txset-validation
  - canonical-ordering
  - untrusted-input-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an explicit hash-order validation check for TxSetFrame::mTxs and re-sorts filtered transactions after surge pricing. This is a focused ordering correctness or hardening change in transaction-set handling. The evidence supports a canonical-ordering fix, but not a confirmed or likely security vulnerability.

## Observed Patch Facts

1. In `src/herder/TxSetFrame.cpp`, the patch replaces `if (std::adjacent_find(mTxs.begin(), mTxs.end(),` with `if (!std::is_sorted(mTxs.begin(), mTxs.end(), &TxSetUtils::hashTxSorter))`.

2. In `src/herder/TxSetFrame.cpp`, the patch replaces `mTxs = filteredTxs;` with `mTxs = TxSetUtils::sortTxsInHashOrder(filteredTxs);`.

## Project Context

The changed code sits primarily in `src/herder`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/herder/TxSetUtils.cpp`, `src/herder/HerderSCPDriver.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/herder/TxSetUtils.cpp`, `src/herder/HerderSCPDriver.h`. The strongest project-level identifiers around this patch are `mTxs`, `std::is_sorted`, `TxSetUtils::hashTxSorter`, and `TxSetUtils::sortTxsInHashOrder`. Nearby tests or test-like files include `src/herder/test/TxSetTests.cpp`, `src/herder/test/TestTxSetUtils.cpp`.

## Before/After Behavior

Before the patch, the provided validation hunk only shows an adjacent_find-based check beginning at the location now followed by the new ordering check; the full prior predicate is not provided. After the patch, checkValid rejects mTxs when std::is_sorted with TxSetUtils::hashTxSorter returns false. Before the patch, surgePricingFilter assigned filteredTxs directly to mTxs. After the patch, it assigns TxSetUtils::sortTxsInHashOrder(filteredTxs) to mTxs.

# Root Cause

TxSetFrame did not visibly enforce or restore full canonical hash ordering at the changed points. The patch indicates filtered transaction lists could be stored without re-sorting, and validation lacked the newly added explicit is_sorted check.

## Walkthrough

1. TxSetFrame stores transaction sets in mTxs.

2. The patch adds a checkValid condition requiring mTxs to be sorted with TxSetUtils::hashTxSorter.

3. If the order check fails, checkValid logs that the txSet is not in hash order and returns false.

4. surgePricingFilter previously wrote filteredTxs directly back to mTxs.

5. surgePricingFilter now sorts filteredTxs with TxSetUtils::sortTxsInHashOrder before assigning mTxs.

6. Related context shows TxSetUtils provides the sorter and sorting helper, and TxSetFrame::makeFromWire treats wire txsets as untrusted and requiring validation.

7. The evidence does not show a concrete exploit path, production denial of service, consensus split, fund loss, replay, or signature bypass.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/herder/TxSetFrame.cpp | 522 | checkValid rejects transaction sets whose mTxs are not sorted by TxSetUtils::hashTxSorter |
| src/herder/TxSetFrame.cpp | 848 | surgePricingFilter re-sorts filteredTxs into hash order before storing them in mTxs |

## Code Snippets

## Snippet 1

Context: `src/herder/TxSetFrame.cpp:522` (changes signature or replay validation logic)

Before
```cpp
}

    if (std::adjacent_find(mTxs.begin(), mTxs.end(),
                           [](auto const& lhs, auto const& rhs) {
```
After
```cpp
}

    if (!std::is_sorted(mTxs.begin(), mTxs.end(), &TxSetUtils::hashTxSorter))
    {
        CLOG_DEBUG(Herder, "Got bad txSet: {} is not in hash order",
                   hexAbbrev(mPreviousLedgerHash));
        return false;
    }
```

## Snippet 2

Context: `src/herder/TxSetFrame.cpp:848` (changes a sensitive control or state-update path)

Before
```cpp
}
    }
    mTxs = filteredTxs;
}
```
After
```cpp
}
    }
    mTxs = TxSetUtils::sortTxsInHashOrder(filteredTxs);
}
```

# Fix Pattern

Add explicit invariant validation and restore the invariant after internal mutation.

## How It Was Fixed

The patch added an std::is_sorted check using TxSetUtils::hashTxSorter in TxSetFrame::checkValid and changed surgePricingFilter to store a hash-sorted copy of filteredTxs back into mTxs.

# Why It Matters

1. Canonical ordering can matter for deterministic transaction-set handling.

2. The changed code is in transaction-set validation and filtering.

3. The security impact is not established by the supplied evidence.

4. The commit body mentions test crashes, not a demonstrated production attack.

# Evidence Notes

Primary evidence is limited to two TxSetFrame.cpp hunks: the new is_sorted validation around line 522 and the sorted assignment in surgePricingFilter around line 848. Related context supports that hashTxSorter and sortTxsInHashOrder are canonical-ordering helpers. Claims that the old adjacent_find check was weaker in a specific way, or that this caused exploitable consensus or denial-of-service behavior, are not proven by the provided snippets. Protocol security invariant: Transaction sets may need to be kept in canonical hash order before validation succeeds or before later hashing/consensus-adjacent processing, but the provided evidence does not establish that violating this invariant created an exploitable security vulnerability. Verification notes: No concrete attacker-controlled exploit path is proven by the patch evidence. No direct fund loss, signature bypass, or transaction replay vulnerability is shown. The crash mentioned in the commit body is test fallout from adding the check, not proof of a production denial-of-service issue. The patch evidence supports canonical ordering hardening more strongly than a confirmed vulnerability. No tests or external context were provided proving exploitability. The previous adjacent_find predicate is incomplete in the evidence. The commit message supports an ordering fix and test fallout, not a security incident. Classified as unclear rather than security-fix or security-hardening for corpus purposes. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `canonical-order-validation-hardening`
Final impact type: `consensus-integrity-hardening, input-validation-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, txset-validation, canonical-ordering, untrusted-input-validation`

The evidence supports retaining this as security hardening, not a confirmed security fix. The patch adds explicit rejection of transaction sets that are not in canonical hash order in checkValid, and project context says wire transaction sets are untrusted and must be validated. It also restores hash ordering after surge pricing mutation. This tightens validation on consensus-adjacent transaction-set handling, but the supplied evidence does not prove an exploitable vulnerability or concrete impact.

## Security Evidence

1. checkValid now rejects mTxs when not sorted by TxSetUtils::hashTxSorter.
2. The rejected condition is logged as a bad txSet and returns false.
3. Project context states makeFromWire creates a TxSetFrame from an untrusted XDR message that must be validated via checkValid.
4. surgePricingFilter now re-sorts filtered transactions before storing them back into mTxs.
5. The affected code is transaction-set handling in blockchain core, adjacent to validation and content hashing.

## Missing Evidence

1. No demonstrated exploit path is shown.
2. No evidence of production denial of service, consensus split, replay, signature bypass, or fund loss is provided.
3. The prior adjacent_find predicate is incomplete, so the exact old validation weakness is not fully proven.
4. The commit body mentions test crashes from adding the check, not a security incident.

## Claim Boundaries

1. Classify as security-hardening only, not security-fix.
2. Do not claim a confirmed vulnerability or attacker exploitability.
3. Do not claim specific financial, replay, or consensus-split impact from the supplied patch alone.
4. The supported claim is canonical transaction-set ordering validation for untrusted or consensus-adjacent data.
