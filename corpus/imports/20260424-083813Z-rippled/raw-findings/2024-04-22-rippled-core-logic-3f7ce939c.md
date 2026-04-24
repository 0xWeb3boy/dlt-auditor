---
case_id: case_20240422_3f7ce939c
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
confidence: medium
source_quality: medium
date: 2024-04-22
source_refs:
  - git:3f7ce939c8cdea08d4161762e5d2a8d9d93c6790
  - "src/ripple/ledger/impl/View.cpp:1148"
  - "src/ripple/protocol/AmountConversions.h:188"
  - "src/ripple/protocol/AmountConversions.h:205"
  - "src/ripple/protocol/AmountConversions.h:144"
bug_class: amm-rounding-invariant-hardening
impact_type:
  - protocol-accounting-integrity
  - economic-invariant-preservation
tags:
  - blockchain-core
  - amm
  - rounding
  - consensus-amendment
  - invariant-preservation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports a likely security-relevant AMM accounting fix. The commit states that swap rounding could sometimes violate the AMM balance-product invariant by very small amounts and introduces the `fixAMMRounding` amendment so rounding favors the AMM. The visible hunks mostly show supporting guard and type-safety changes, not the exact rounding expression, so claims about exploitability or material loss should be avoided.

## Observed Patch Facts

1. In `src/ripple/ledger/impl/View.cpp`, the patch replaces `assert(saAmount >= beast::zero);` with `if (view.rules().enabled(fixAMMRounding))`.

2. In `src/ripple/protocol/AmountConversions.h`, the patch replaces `if constexpr (std::is_same_v<XRPAmount, T>)` with `else if constexpr (std::is_same_v<XRPAmount, T>)`.

3. In `src/ripple/protocol/AmountConversions.h`, the patch replaces `if constexpr (std::is_same_v<XRPAmount, T>)` with `else if constexpr (std::is_same_v<XRPAmount, T>)`.

4. In `src/ripple/protocol/AmountConversions.h`, the patch adds `else`.

## Project Context

The changed code sits primarily in `src/ripple/ledger/impl`, `src/ripple/ledger`, `src/ripple/protocol`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/ripple/protocol/STAmount.h`, `src/ripple/protocol/AMMCore.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/app/tx/impl/XChainBridge.cpp`, `src/ripple/app/tx/impl/OfferStream.cpp`. The strongest project-level identifiers around this patch are `std::is_same_v`, `constexpr`, `is_same_v`, and `beast::zero`. Nearby tests or test-like files include `src/ripple/beast/unit_test/thread.h`, `src/ripple/beast/unit_test/suite_list.h`.

## Before/After Behavior

Before the patch, AMM swap rounding could sometimes produce post-swap balances whose product was slightly below the pre-swap product, according to the commit message. The shown `accountSend` code relied on `assert(saAmount >= beast::zero)` for non-negative amounts. After the patch, `fixAMMRounding` changes rounding behavior to preserve the AMM invariant, and the shown `accountSend` path adds an amendment-gated runtime return of `tecINTERNAL` for negative `saAmount`. The `AmountConversions.h` changes add compile-time unsupported-type failures and appear to be supporting cleanup rather than the root cause.

# Root Cause

Rounding in AMM swap accounting could favor the swap outcome enough to slightly violate the AMM's expected balance-product invariant. The supplied snippets do not show the exact arithmetic change, so the root cause is grounded primarily in the commit message rather than visible diff hunks.

## Walkthrough

1. AMM swaps are expected to preserve `new_balance_1 * new_balance_2 >= old_balance_1 * old_balance_2`.

2. The commit message states that rounding could sometimes violate this invariant by very small amounts.

3. The patch introduces the `fixAMMRounding` amendment to make rounding favor the AMM and maintain the invariant.

4. The shown `View.cpp` hunk adds an amendment-gated runtime check that rejects negative `saAmount` with `tecINTERNAL`.

5. The shown `AmountConversions.h` hunks tighten template helper behavior with `else if constexpr` chains and unsupported-type `static_assert`s.

6. Those helper changes are supporting evidence only; they do not independently establish the AMM rounding defect.

7. No provided evidence demonstrates a concrete attack transaction, quantified loss, or drain scenario.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/ledger/impl/View.cpp | 1142 | accountSend now converts the non-negative amount assumption into an amendment-gated runtime tecINTERNAL guard for fixAMMRounding |
| src/ripple/protocol/AmountConversions.h | 138 | amount conversion helper adds unsupported-type static assertion used by AMM and amount math paths |
| src/ripple/protocol/AmountConversions.h | 182 | issue extraction helper cleanup for typed amount conversions |
| src/ripple/protocol/AmountConversions.h | 199 | STAmount typed extraction helper cleanup for IOU/XRP/STAmount conversions |
| src/ripple/app/paths/impl/AMMLiquidity.cpp | 45 | traced AMM liquidity balance-fetch path where AMM asset balances are read and typed for swap calculations |

## Code Snippets

## Snippet 1

Context: `src/ripple/ledger/impl/View.cpp:1148` (changes the branch that decides whether execution stops or continues)

Before
```cpp
WaiveTransferFee waiveFee)
{
    assert(saAmount >= beast::zero);

    /* If we aren't sending anything or if the sender is the same as the
```
After
```cpp
WaiveTransferFee waiveFee)
{
    if (view.rules().enabled(fixAMMRounding))
    {
        if (saAmount < beast::zero)
        {
            return tecINTERNAL;
        }
```

## Snippet 2

Context: `src/ripple/protocol/AmountConversions.h:188` (changes a sensitive control or state-update path)

Before
```c
if constexpr (std::is_same_v<IOUAmount, T>)
        return noIssue();
    if constexpr (std::is_same_v<XRPAmount, T>)
        return xrpIssue();
    if constexpr (std::is_same_v<STAmount, T>)
        return amt.issue();
}
```
After
```c
if constexpr (std::is_same_v<IOUAmount, T>)
        return noIssue();
    else if constexpr (std::is_same_v<XRPAmount, T>)
        return xrpIssue();
    else if constexpr (std::is_same_v<STAmount, T>)
        return amt.issue();
    else
    {
```

## Snippet 3

Context: `src/ripple/protocol/AmountConversions.h:205` (changes a sensitive control or state-update path)

Before
```c
if constexpr (std::is_same_v<IOUAmount, T>)
        return a.iou();
    if constexpr (std::is_same_v<XRPAmount, T>)
        return a.xrp();
    if constexpr (std::is_same_v<STAmount, T>)
        return a;
}
```
After
```c
if constexpr (std::is_same_v<IOUAmount, T>)
        return a.iou();
    else if constexpr (std::is_same_v<XRPAmount, T>)
        return a.xrp();
    else if constexpr (std::is_same_v<STAmount, T>)
        return a;
    else
    {
```

## Snippet 4

Context: `src/ripple/protocol/AmountConversions.h:144` (changes a sensitive control or state-update path)

Before
```c
return STAmount(issue, n.mantissa(), n.exponent());
    }
}
```
After
```c
return STAmount(issue, n.mantissa(), n.exponent());
    }
    else
    {
        constexpr bool alwaysFalse = !std::is_same_v<T, T>;
        static_assert(alwaysFalse, "Unsupported type for toAmount");
    }
}
```

# Fix Pattern

Use a consensus amendment to change AMM rounding semantics so arithmetic preserves the protocol accounting invariant, with adjacent runtime and compile-time guards around amount handling.

## How It Was Fixed

The fix is the `fixAMMRounding` amendment. Per the commit message, it changes AMM rounding so swap calculations favor the AMM and preserve the invariant. The visible code also adds an amendment-gated negative-amount guard in `accountSend` and tightens amount conversion helpers with unsupported-type `static_assert`s.

# Why It Matters

1. AMM balance math is consensus-sensitive economic logic.

2. Rounding that lowers the AMM invariant can violate expected pool accounting.

3. The amendment gating indicates a behavior change that validators must coordinate on.

4. The evidence does not support stronger claims about practical exploitability or material loss.

# Evidence Notes

Strongest evidence is the commit message explicitly describing the AMM invariant, the rounding violation, and the `fixAMMRounding` amendment. The listed files include AMM helper and numeric code, but the provided snippets do not show the actual rounding diff. The `View.cpp` guard is relevant adjacent hardening. The `AmountConversions.h` hunks should be treated as support cleanup/type-safety changes unless further evidence ties them directly to the invariant violation. Protocol security invariant: AMM swap execution should preserve the pool accounting invariant `new_balance_1 * new_balance_2 >= old_balance_1 * old_balance_2`; rounding must not make a completed swap reduce the AMM's invariant below its prior value. Verification notes: The patch evidence does not prove an externally exploitable attack transaction. The patch evidence does not quantify any profit, loss, or drain magnitude beyond the commit's statement of very small rounding violations. The AmountConversions.h hunks alone look like type-safety/API cleanup and are not independently security fixes. The provided snippets do not show the exact arithmetic rounding change in AMMHelpers.h or Number.h. This mapping should not be generalized to non-AMM payment or offer paths without additional evidence. Do not claim a demonstrated exploit path from the supplied evidence. Do not claim quantified loss or pool drain impact. Do not treat `AmountConversions.h` helper cleanup as the root cause. Confidence remains medium because the core rounding diff is not shown, but the commit message directly states the invariant violation and fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `amm-rounding-invariant-hardening`
Final impact type: `protocol-accounting-integrity, economic-invariant-preservation`
Final tags: `blockchain-core, amm, rounding, consensus-amendment, invariant-preservation`

The evidence supports retaining this as security hardening rather than a confirmed security fix. The commit metadata directly states that AMM swap rounding could violate the balance-product invariant and that a consensus amendment changes rounding to favor the AMM. In blockchain AMM logic, preserving accounting invariants is security-sensitive economic hardening. However, the supplied hunks mostly show adjacent runtime/type-safety guards and do not include the actual rounding arithmetic or demonstrate exploitability, loss, or a concrete attack path.

## Security Evidence

1. Commit body identifies an AMM swap invariant: new_balance_1 * new_balance_2 >= old_balance_1 * old_balance_2.
2. Commit body says rounding could sometimes violate that invariant.
3. Patch introduces the fixAMMRounding amendment, indicating a consensus-sensitive behavior change.
4. Commit body says rounding is changed to always favor the AMM to maintain the invariant.
5. View.cpp adds an amendment-gated runtime guard returning tecINTERNAL for negative saAmount.

## Missing Evidence

1. The supplied hunks do not show the actual AMM rounding arithmetic change.
2. No transaction-level exploit, proof of profit, or drain scenario is provided.
3. No quantified impact beyond very small invariant violations is shown.
4. AmountConversions.h changes appear to be compile-time/type-safety cleanup and do not independently prove the AMM invariant bug.

## Claim Boundaries

1. Treat this as AMM invariant hardening, not a demonstrated exploitable vulnerability.
2. Do not claim material fund loss or pool draining from the supplied evidence.
3. Do not treat the AmountConversions.h helper changes as the root cause.
4. Do not generalize the issue beyond AMM swap rounding behavior without additional evidence.
