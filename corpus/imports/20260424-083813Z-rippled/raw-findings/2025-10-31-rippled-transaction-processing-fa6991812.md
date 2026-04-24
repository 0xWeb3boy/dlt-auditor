---
case_id: case_20251031_fa6991812
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: high
source_quality: high
date: 2025-10-31
source_refs:
  - git:fa6991812471bdde0d771754e8b7e688d774c81f
  - "src/xrpld/app/tx/detail/Payment.cpp:271"
  - "src/xrpld/app/tx/detail/applySteps.cpp:146"
  - "src/xrpld/app/tx/detail/DelegateSet.cpp:63"
  - "src/libxrpl/protocol/Permissions.cpp:175"
bug_class: improper-authorization
impact_type:
  - authorization-bypass
  - unauthorized-delegated-transaction
tags:
  - blockchain-core
  - transaction-processing
  - permission-delegation
  - access-control
  - authorization
  - amendment-gating
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch addresses a permission-delegation authorization flaw. The strongest supported claim is that delegated transaction permission checks were not consistently tied to the current amendment-aware delegability rules and the concrete Payment shape. The fix constrains granular Payment permissions to direct payments and updates delegability checks so transactions are evaluated against feature/amendment metadata rather than relying on deprecated amendment-specific paths.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/Payment.cpp`, the patch replaces `// post-amendment: disallow cross currency payments for PaymentMint and` with `// Granular permissions are only valid for direct payments.`.

2. In `src/xrpld/app/tx/detail/applySteps.cpp`, the patch replaces `return with_txn_type(ctx.tx.getTxnType(), [&]<typename T>() {` with `return with_txn_type(ctx.tx.getTxnType(), [&]<typename T>() -> TER {`.

3. In `src/xrpld/app/tx/detail/DelegateSet.cpp`, the patch replaces `auto const& permissions = ctx.tx.getFieldArray(sfPermissions);` with `return tesSUCCESS;`.

4. In `src/libxrpl/protocol/Permissions.cpp`, the patch replaces `if (rules.enabled(fixDelegateV1_1))` with `auto const txFeaturesIt = txFeatureMap_.find(txType);`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, `src/libxrpl/protocol`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/libxrpl/protocol/Rules.cpp`, `src/xrpld/app/tx/detail/Transactor.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/Transactor.h`, `src/xrpld/app/tx/detail/apply.cpp`. The strongest project-level identifiers around this patch are `auto`, `const`, `rules`, and `fixDelegateV1_1`.

## Before/After Behavior

Before the change, Payment delegated-permission handling included narrower fixDelegateV1_1-gated checks around PaymentMint and PaymentBurn and a special success path for some issued-asset PaymentMint cases. After the change, Payment::checkPermission computes the destination asset unconditionally and rejects granular permissions for cross-asset SendMax behavior or path-based payments. Before the change, DelegateSet::preclaim contained a permission-array delegability loop with comments indicating that transactions from not-yet-enabled amendments could still be delegated in the old flow. After the change, that preclaim function only checks account existence and returns success, while delegability is handled through the updated permission logic. Permissions::isDelegatable now performs the delegatable transaction lookup outside the old fixDelegateV1_1-only branch and consults transaction feature metadata.

# Root Cause

Delegated-authorization checks were split across deprecated amendment-specific behavior and transaction-specific permission checks. That could allow delegated authorization to be evaluated without fully matching the currently enabled amendment rules or the actual submitted Payment shape, especially for granular Payment permissions and transactions tied to amendments.

## Walkthrough

1. A delegate submits a transaction that must be authorized by permissions granted by another account.

2. The permission-delegation subsystem checks whether the requested permission or transaction type is delegatable.

3. Before the fix, some delegability checks were tied to the deprecated fixDelegateV1_1 path, and removed comments state that not-yet-enabled amendment transactions could still be delegated.

4. For delegated Payments, the previous checks focused on specific granular cases rather than enforcing a general direct-payment-only rule.

5. A path-based Payment or a Payment with cross-asset SendMax could therefore fall outside the intended granular permission boundary.

6. After the fix, Payment::checkPermission rejects granular permission use when sfPaths is present or when sfSendMax uses a different asset than sfAmount.

7. After the fix, Permissions::isDelegatable performs transaction lookup and feature metadata checks outside the old deprecated amendment branch.

8. The commit context states that checkPermission now returns terNO_DELEGATE_PERMISSION when a delegate transaction lacks the necessary permissions.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/Payment.cpp | 265 | Enforces granular delegated Payment permissions and restricts them to direct payments without paths or cross-asset SendMax behavior. |
| src/libxrpl/protocol/Permissions.cpp | 169 | Determines whether a transaction or granular permission is delegatable and gates delegability on transaction feature/amendment availability. |
| src/xrpld/app/tx/detail/DelegateSet.cpp | 57 | Handles DelegateSet preclaim validation for accounts and previously contained permission-array delegability checks affected by the amendment transition. |
| src/xrpld/app/tx/detail/applySteps.cpp | 146 | Coordinates preclaim execution and TER result categories before signature checks, relevant to safe transaction admission semantics. |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/Payment.cpp:271` (updates aggregate accounting or lifecycle state)

Before
```cpp
auto const& dstAmount = tx.getFieldAmount(sfAmount);
    // post-amendment: disallow cross currency payments for PaymentMint and
    // PaymentBurn
    if (view.rules().enabled(fixDelegateV1_1))
    {
        auto const& amountAsset = dstAmount.asset();
        if (tx.isFieldPresent(sfSendMax) &&
```
After
```cpp
auto const& dstAmount = tx.getFieldAmount(sfAmount);
    auto const& amountAsset = dstAmount.asset();

    // Granular permissions are only valid for direct payments.
    if ((tx.isFieldPresent(sfSendMax) &&
         tx[sfSendMax].asset() != amountAsset) ||
        tx.isFieldPresent(sfPaths))
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/applySteps.cpp:146` (updates aggregate accounting or lifecycle state)

Before
```cpp
// use name hiding to accomplish compile-time polymorphism of static
        // class functions for Transactor and derived classes.
        return with_txn_type(ctx.tx.getTxnType(), [&]<typename T>() {
            // If the transactor requires a valid account and the transaction
            // doesn't list one, preflight will have already a flagged a
            // failure.
            auto const id = ctx.tx.getAccountID(sfAccount);
```
After
```cpp
// use name hiding to accomplish compile-time polymorphism of static
        // class functions for Transactor and derived classes.
        return with_txn_type(ctx.tx.getTxnType(), [&]<typename T>() -> TER {
            // preclaim functionality is divided into two sections:
            // 1. Up to and including the signature check: returns NotTEC.
            //    All transaction checks before and including checkSign
            //    MUST return NotTEC, or something more restrictive.
            //    Allowing tec results in these steps risks theft or
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/DelegateSet.cpp:63` (updates aggregate accounting or lifecycle state)

Before
```cpp
return tecNO_TARGET;

    auto const& permissions = ctx.tx.getFieldArray(sfPermissions);
    for (auto const& permission : permissions)
    {
        if (!ctx.view.rules().enabled(fixDelegateV1_1) &&
            !Permission::getInstance().isDelegatable(
                permission[sfPermissionValue], ctx.view.rules()))
```
After
```cpp
return tecNO_TARGET;

    return tesSUCCESS;
}
```

## Snippet 4

Context: `src/libxrpl/protocol/Permissions.cpp:175` (updates aggregate accounting or lifecycle state)

Before
```cpp
auto const it = delegatableTx_.find(txType);

    if (rules.enabled(fixDelegateV1_1))
    {
        if (it == delegatableTx_.end())
            return false;

        auto const feature = getTxFeature(txType);
```
After
```cpp
auto const it = delegatableTx_.find(txType);

    if (it == delegatableTx_.end())
        return false;

    auto const txFeaturesIt = txFeatureMap_.find(txType);
    XRPL_ASSERT(
        txFeaturesIt != txFeatureMap_.end(),
```

# Fix Pattern

Move delegated-authorization enforcement to amendment-aware permission checks and validate the concrete transaction shape before accepting a delegated transaction.

## How It Was Fixed

The patch introduces featurePermissionDelegationV1_1 as the replacement amendment path, updates Payment::checkPermission so granular Payment permissions are valid only for direct payments, updates Permissions::isDelegatable to use transaction feature metadata for amendment-aware delegability, and removes the older permission-array delegability loop from DelegateSet::preclaim. The applySteps.cpp change documents and tightens TER return-category expectations around preclaim, but the supplied evidence supports it as adjacent transaction-admission cleanup rather than the main root cause.

# Why It Matters

1. Delegated permissions must not authorize transaction shapes outside the grant.

2. Granular Payment permissions are now bounded to direct payments.

3. Delegability now accounts for transaction feature and amendment availability.

4. The evidence supports a permission-delegation authorization issue, not accounting drift.

5. The evidence does not establish key compromise, exploitation in the wild, or a vulnerability affecting all Payment processing.

# Evidence Notes

Supported by the commit subject and body, plus changes in Payment::checkPermission, Permissions::isDelegatable, and DelegateSet::preclaim. The strongest direct evidence is the new direct-payment check for granular Payment permissions, the amendment-aware delegability lookup, and the commit statement that delegate transactions without necessary permissions now return terNO_DELEGATE_PERMISSION. The applySteps.cpp excerpt is relevant to transaction admission semantics but should not be treated as the core vulnerability without more evidence. Protocol security invariant: A delegated transaction must only be accepted when the delegating account has granted a permission that covers the specific transaction type and transaction shape under the currently enabled amendment rules. Granular Payment permissions must not authorize path-based or cross-asset payments unless such behavior is explicitly permitted. Verification notes: The patch does not by itself prove practical exploitability or a complete attack path. The evidence does not prove key compromise or unauthorized signing; it concerns delegated permission checks after a delegate transaction is submitted. The evidence does not support the heuristic accounting-or-state-drift classification. The affected scope should be limited to permission delegation and granular delegated transaction authorization, not all Payment processing. The patch does not prove that funds theft occurred in the wild. No external verification or file inspection was performed beyond the provided input. The classification rejects the heuristic accounting-or-state-drift theory as unsupported. The finding is limited to permission delegation and granular delegated transaction authorization. Exploitability details and concrete attacker workflow are not proven by the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `improper-authorization`
Final impact type: `authorization-bypass, unauthorized-delegated-transaction`
Final tags: `blockchain-core, transaction-processing, permission-delegation, access-control, authorization, amendment-gating`

The supplied evidence supports retaining this as a security fix, but the original accounting/state-drift framing is misleading. The commit explicitly identifies a permission delegation vulnerability, and the patch tightens delegated transaction authorization by rejecting delegated Payment shapes outside granular permission scope and by moving delegability decisions toward amendment-aware transaction feature checks. The strongest supported classification is improper authorization in delegated transaction permissions, not accounting drift or signature compromise.

## Security Evidence

1. Commit subject says it addresses a permission delegation vulnerability.
2. Commit body says checkPermission now returns terNO_DELEGATE_PERMISSION when a delegate transaction lacks necessary permissions.
3. Payment::checkPermission now rejects granular delegated permissions for path-based payments or SendMax assets that differ from the destination asset.
4. Permissions::isDelegatable now performs delegatable transaction lookup outside the old fixDelegateV1_1-specific branch and consults transaction feature metadata.
5. DelegateSet evidence includes removed comments stating not-yet-enabled amendment transactions could still be delegated before the prior fix path.

## Missing Evidence

1. No full diff or tests are provided to prove the complete exploit scenario.
2. No evidence shows exploitation in the wild or actual fund loss.
3. No evidence proves key compromise, signature bypass, or general Payment-processing compromise.
4. DelegateSet removal alone is ambiguous without the surrounding replacement enforcement path.

## Claim Boundaries

1. Scope should be limited to permission delegation and delegated transaction authorization.
2. Do not classify this as accounting-or-state-drift based on the supplied evidence.
3. Do not claim all Payments were affected; the evidence centers on granular delegated Payment permissions and amendment-aware delegability.
4. The applySteps.cpp TER-category change is adjacent transaction-admission hardening context, not the core vulnerability by itself.
