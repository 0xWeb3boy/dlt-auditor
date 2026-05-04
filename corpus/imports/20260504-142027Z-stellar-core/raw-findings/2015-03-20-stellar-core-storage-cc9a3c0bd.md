---
case_id: case_20150320_cc9a3c0bd
project: stellar-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
source_quality: high
date: 2015-03-20
source_refs:
  - git:cc9a3c0bde0838dbf3228259a16c46e013aed39c
  - "src/transactions/ChangeTrustOpFrame.cpp:27"
  - "src/xdr/Stellar-transaction.x:252"
  - "src/ledger/LedgerMaster.cpp:46"
bug_class: missing-transaction-validation
impact_type:
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - transaction-validation
  - trustline
  - ledger-invariant
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is a trustline transaction-validation fix. The patch adds validation in ChangeTrustOpFrame::doApply so an existing trustline cannot be changed to a negative limit or to a limit below its current balance, and adds an INVALID_LIMIT result code for that rejection. The LedgerMaster change is comment-only and is not part of the behavioral fix. The evidence supports a likely security-relevant ledger invariant fix, but not a confirmed exploit, remote attack path, or consensus failure.

## Observed Patch Facts

1. In `src/transactions/ChangeTrustOpFrame.cpp`, the patch replaces `trustLine.getTrustLine().limit = mChangeTrust.limit;` with `if( mChangeTrust.limit < 0 ||`.

2. In `src/xdr/Stellar-transaction.x`, the patch replaces `NO_ACCOUNT = 1` with `NO_ACCOUNT = 1,`.

3. In `src/ledger/LedgerMaster.cpp`, the patch removes `// TODO.1 wire up catch up. turn off ledger close when catching up.`.

## Project Context

The changed code sits primarily in `src/transactions`, `src/xdr`, `src/ledger`, which anchors the finding in the `storage` area of the project. Historical context from `src/transactions/PaymentOpFrame.cpp`, `src/transactions/OfferExchange.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/transactions/PaymentOpFrame.cpp`, `src/transactions/OfferExchange.cpp`. The strongest project-level identifiers around this patch are `limit`, `ChangeTrust::INVALID_LIMIT`, `mChangeTrust`, and `trustLine`.

## Before/After Behavior

Before the patch, the shown existing-trustline path assigned trustLine.getTrustLine().limit = mChangeTrust.limit without the displayed non-negative or balance-covering validation. After the patch, the operation returns false with ChangeTrust::INVALID_LIMIT when mChangeTrust.limit is negative or lower than trustLine.getTrustLine().balance. The XDR enum gains INVALID_LIMIT so the new rejection can be represented. The LedgerMaster hunk only removes a TODO comment.

# Root Cause

The existing ChangeTrust modification path lacked an explicit validation check that the requested trustline limit must be non-negative and at least the already-held trustline balance before accepting the new limit.

## Walkthrough

1. A ChangeTrust operation reaches ChangeTrustOpFrame::doApply and loads an existing trustline.

2. In the pre-patch evidence, that branch directly assigns the requested limit to the trustline.

3. The patch adds a check for mChangeTrust.limit < 0 and mChangeTrust.limit < trustLine.getTrustLine().balance before accepting the change.

4. If either condition is true, the operation sets ChangeTrust::INVALID_LIMIT and returns false.

5. The transaction XDR result enum is extended with INVALID_LIMIT for this newly rejected case.

6. The LedgerMaster edit is comment-only and does not support any security claim.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/transactions/ChangeTrustOpFrame.cpp | 27 | Enforces ChangeTrust limit validity before modifying an existing trustline. |
| src/xdr/Stellar-transaction.x | 252 | Adds INVALID_LIMIT result code for rejected ChangeTrust operations. |
| src/ledger/LedgerMaster.cpp | 46 | Comment-only cleanup; not part of the security-relevant behavior. |

## Code Snippets

## Snippet 1

Context: `src/transactions/ChangeTrustOpFrame.cpp:27` (changes bounds, limits, or capacity handling)

Before
```cpp
db))
    { // we are modifying an old trustline
        trustLine.getTrustLine().limit = mChangeTrust.limit;
        if (trustLine.getTrustLine().limit == 0 &&
```
After
```cpp
db))
    { // we are modifying an old trustline
        
        if( mChangeTrust.limit < 0 || 
            mChangeTrust.limit < trustLine.getTrustLine().balance)
        { // Can't drop the limit below the balance you are holding with them
            innerResult().code(ChangeTrust::INVALID_LIMIT);
            return false;
```

## Snippet 2

Context: `src/xdr/Stellar-transaction.x:252` (changes a sensitive control or state-update path)

Before
```text
{
    SUCCESS = 0,
    NO_ACCOUNT = 1
};
```
After
```text
{
    SUCCESS = 0,
    NO_ACCOUNT = 1,
    INVALID_LIMIT =2
};
```

## Snippet 3

Context: `src/ledger/LedgerMaster.cpp:46` (changes a sensitive control or state-update path)

Before
```cpp
// TODO.3 we need to store some validation history?
    // TODO.1 wire up catch up. turn off ledger close when catching up.
    // TODO.3 better way to handle quorums when you are booting a network for
instance if all nodes fail.
```
After
```cpp
// TODO.3 we need to store some validation history?
    // TODO.3 better way to handle quorums when you are booting a network for
instance if all nodes fail.
```

# Fix Pattern

Validate transaction input against ledger accounting invariants before mutating existing trustline state, and expose a specific result code for the rejected invalid-input case.

## How It Was Fixed

ChangeTrustOpFrame.cpp now rejects invalid requested trustline limits before proceeding in the existing-trustline branch. Stellar-transaction.x adds INVALID_LIMIT to ChangeTrustResultCode. No supported runtime behavior change comes from the LedgerMaster edit.

# Why It Matters

1. Prevents a trustline limit from being set below the balance already held on that trustline.

2. Prevents negative trustline limits in the shown modification path.

3. Preserves a core ledger accounting invariant for non-native asset trustlines.

4. Does not establish remote exploitability or consensus failure from the provided evidence alone.

# Evidence Notes

Primary evidence is the added guard in src/transactions/ChangeTrustOpFrame.cpp and the added INVALID_LIMIT result code in src/xdr/Stellar-transaction.x. The related payment and offer snippets show nearby trustline usage but are not modified by the patch and should not be used to claim a payment or offer vulnerability. The LedgerMaster hunk is comment-only cleanup. The commit subject references an issue, but the issue contents are not provided, so stronger claims about exploitability or incident impact are unsupported. Protocol security invariant: A ChangeTrust operation modifying an existing trustline must not set the trustline limit to a negative value or to a value below the trustline's current balance. Verification notes: The patch does not prove remote exploitability or consensus failure by itself. The patch does not show whether invalid limits could be committed in every pre-fix path. The patch does not modify payment or offer execution directly. The LedgerMaster hunk is not evidence of a ledger catch-up security fix. Behavioral change is directly supported for existing trustline modification in ChangeTrustOpFrame::doApply. INVALID_LIMIT result-code support is directly supported by the XDR enum change. No tests, issue text, exploit scenario, or consensus-impact evidence are provided. Confidence is downgraded from high to medium because the security impact is inferred from the ledger invariant rather than demonstrated. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-transaction-validation`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-validation, trustline, ledger-invariant, state-integrity`

The patch clearly adds validation to a security-sensitive ledger transaction path, rejecting negative trustline limits and limits below the existing balance before mutating trustline state. That supports retaining it as security hardening around ledger invariants. The evidence does not strongly prove an exploitable vulnerability, consensus failure, or concrete corruption incident, so classifying it as a security-fix/state-corruption case would be too strong.

## Security Evidence

1. ChangeTrustOpFrame::doApply now rejects mChangeTrust.limit < 0.
2. ChangeTrustOpFrame::doApply now rejects limits below trustLine.getTrustLine().balance.
3. The rejected condition occurs before modifying an existing trustline state.
4. Stellar-transaction.x adds INVALID_LIMIT so invalid ChangeTrust operations can be represented as failures.
5. The affected code is transaction validation in blockchain ledger state handling.

## Missing Evidence

1. No issue text for #268 is provided.
2. No tests or exploit scenario are provided.
3. No evidence shows invalid limits were accepted into committed consensus state in practice.
4. No evidence shows payment, offer, or consensus failure impact.
5. LedgerMaster change is comment-only and adds no security evidence.

## Claim Boundaries

1. Supports a trustline limit validation hardening claim only.
2. Does not support confirmed exploitability.
3. Does not support a remote attack or consensus-safety claim from the patch alone.
4. Does not support using the LedgerMaster hunk as behavioral evidence.
5. Original state-corruption/security-fix framing should be downgraded to missing transaction validation/security hardening.
