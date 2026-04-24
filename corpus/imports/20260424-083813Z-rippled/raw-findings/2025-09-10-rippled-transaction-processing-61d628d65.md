---
case_id: case_20250910_61d628d65
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: access-control
impact_type:
  - privilege-misuse
confidence: medium
source_quality: high
date: 2025-09-10
source_refs:
  - git:61d628d654fd03135a47bf0dea28f56b03a8bd22
  - "src/xrpld/app/tx/detail/Payment.cpp:266"
  - "src/xrpld/app/tx/detail/DelegateSet.cpp:51"
  - "src/libxrpl/protocol/Permissions.cpp:143"
  - "src/xrpld/app/tx/detail/DelegateSet.cpp:73"
tags:
  - blockchain-core
  - transaction-processing
  - access-control
  - permission-delegation
  - protocol-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch tightens delegated-permission validation under the fixDelegateV1_1 amendment. DelegateSet now rejects invalid, unknown, non-delegatable, or amendment-disabled permission values during preflight, and delegated PaymentMint/PaymentBurn checks reject mismatched SendMax and Amount assets.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/Payment.cpp`, the patch replaces `auto const& amountIssue = dstAmount.issue();` with `// post-amendment: disallow cross currency payments for PaymentMint and`.

2. In `src/xrpld/app/tx/detail/DelegateSet.cpp`, the patch adds `if (ctx.rules.enabled(fixDelegateV1_1) &&`.

3. In `src/libxrpl/protocol/Permissions.cpp`, the patch replaces `auto const it = delegatableTx_.find(permissionValue - 1);` with `auto const txType = permissionToTxType(permissionValue);`.

4. In `src/xrpld/app/tx/detail/DelegateSet.cpp`, the patch replaces `auto const permissionValue = permission[sfPermissionValue];` with `if (!ctx.view.rules().enabled(fixDelegateV1_1) &&`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, `src/libxrpl/protocol`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/libxrpl/protocol/Rules.cpp`, `src/xrpld/app/tx/detail/applySteps.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/applySteps.cpp`, `src/xrpld/app/tx/detail/apply.cpp`. The strongest project-level identifiers around this patch are `Permission::getInstance`, `auto`, `const`, and `rules`.

## Before/After Behavior

Before the patch, the provided DelegateSet::preflight evidence only shows duplicate sfPermissionValue rejection, while delegatability checks occurred later in preclaim. The added comments state that before fixDelegateV1_1, transactions from amendments not yet enabled could still be delegated. Permission::isDelegatable previously looked up delegatableTx_ using permissionValue - 1. Payment::checkPermission checked PaymentMint/PaymentBurn using the Amount issue without the shown SendMax/Amount asset mismatch rejection. After the patch, DelegateSet::preflight calls rules-aware isDelegatable when fixDelegateV1_1 is enabled and returns temMALFORMED for invalid unavailable permissions; Permission::isDelegatable maps through permissionToTxType and rejects unknown or disabled-amendment transaction permissions; Payment::checkPermission rejects delegated PaymentMint/PaymentBurn paths where sfSendMax.asset() differs from sfAmount.asset().

# Root Cause

The delegated-permission path did not consistently reject invalid or amendment-disabled permission values before accepting a DelegateSet under the new amendment semantics. Separately, delegated PaymentMint/PaymentBurn authorization did not explicitly require SendMax and Amount to refer to the same asset, allowing broader payment behavior than the stated permission intent.

## Walkthrough

1. A DelegateSet transaction includes sfPermissions entries with sfPermissionValue values.

2. Before the fix, the extracted preflight code only shows duplicate-value rejection, not rules-aware delegatability validation.

3. The preclaim comments added by the patch state that transactions from amendments not yet enabled could still be delegated before fixDelegateV1_1.

4. Permission::isDelegatable previously used permissionValue - 1 to find a transaction permission entry.

5. The patched Permission::isDelegatable uses permissionToTxType, rejects unmapped transaction permissions under fixDelegateV1_1, and consults feature metadata for amendment availability.

6. The patched DelegateSet::preflight rejects non-delegatable or unavailable permission values when fixDelegateV1_1 is enabled.

7. For delegated Payment handling, the patched code rejects a present sfSendMax whose asset differs from sfAmount.asset(), limiting PaymentMint/PaymentBurn delegation to same-asset behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/DelegateSet.cpp | 51 | preflight rejects duplicate and, post-amendment, non-delegatable or invalid permission values before DelegateSet is accepted |
| src/xrpld/app/tx/detail/DelegateSet.cpp | 73 | preclaim preserves pre-amendment behavior while moving post-amendment invalid-permission rejection into preflight semantics |
| src/libxrpl/protocol/Permissions.cpp | 143 | maps permission values to transaction types and, post-amendment, rejects unknown or amendment-disabled transaction permissions |
| src/xrpld/app/tx/detail/Payment.cpp | 266 | enforces delegated PaymentMint/PaymentBurn asset restrictions and rejects cross-currency SendMax/Amount combinations |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/Payment.cpp:266` (changes a sensitive control or state-update path)

Before
```cpp
auto const& dstAmount = tx.getFieldAmount(sfAmount);
    auto const& amountIssue = dstAmount.issue();

    if (granularPermissions.contains(PaymentMint) && !isXRP(amountIssue) &&
        amountIssue.account == tx[sfAccount])
```
After
```cpp
auto const& dstAmount = tx.getFieldAmount(sfAmount);
    // post-amendment: disallow cross currency payments for PaymentMint and
    // PaymentBurn
    if (view.rules().enabled(fixDelegateV1_1))
    {
        auto const& amountAsset = dstAmount.asset();
        if (tx.isFieldPresent(sfSendMax) &&
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/DelegateSet.cpp:51` (changes an authorization or privilege gate)

Before
```cpp
if (!permissionSet.insert(permission[sfPermissionValue]).second)
            return temMALFORMED;
    }
```
After
```cpp
if (!permissionSet.insert(permission[sfPermissionValue]).second)
            return temMALFORMED;

        if (ctx.rules.enabled(fixDelegateV1_1) &&
            !Permission::getInstance().isDelegatable(
                permission[sfPermissionValue], ctx.rules))
            return temMALFORMED;
    }
```

## Snippet 3

Context: `src/libxrpl/protocol/Permissions.cpp:143` (changes a sensitive control or state-update path)

Before
```cpp
return true;

    auto const it = delegatableTx_.find(permissionValue - 1);
    if (it != delegatableTx_.end() && it->second == Delegation::notDelegatable)
        return false;
```
After
```cpp
return true;

    auto const txType = permissionToTxType(permissionValue);
    auto const it = delegatableTx_.find(txType);

    if (rules.enabled(fixDelegateV1_1))
    {
        if (it == delegatableTx_.end())
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/DelegateSet.cpp:73` (changes an authorization or privilege gate)

Before
```cpp
for (auto const& permission : permissions)
    {
        auto const permissionValue = permission[sfPermissionValue];
        if (!Permission::getInstance().isDelegatable(permissionValue))
            return tecNO_PERMISSION;
    }
```
After
```cpp
for (auto const& permission : permissions)
    {
        if (!ctx.view.rules().enabled(fixDelegateV1_1) &&
            !Permission::getInstance().isDelegatable(
                permission[sfPermissionValue], ctx.view.rules()))
        {
            // Before fixDelegateV1_1:
            //   - The check was performed during preclaim.
```

# Fix Pattern

Add amendment-gated, rules-aware permission validation at transaction validation boundaries and enforce same-asset constraints for delegated PaymentMint/PaymentBurn behavior.

## How It Was Fixed

The patch added fixDelegateV1_1-gated validation in DelegateSet::preflight, updated Permission::isDelegatable to use explicit permission-to-transaction mapping plus active rules and feature metadata, preserved legacy preclaim behavior before the amendment, and added a Payment::checkPermission guard returning tecNO_DELEGATE_PERMISSION when SendMax and Amount assets differ.

# Why It Matters

1. Delegated permissions are constrained to valid and available authority.

2. Transaction permissions gated by disabled amendments are treated as unavailable.

3. Invalid permission values are rejected earlier in validation.

4. PaymentMint and PaymentBurn delegation no longer covers cross-currency exchange behavior.

5. The supplied evidence does not establish funds theft, code execution, or consensus failure.

# Evidence Notes

Evidence comes from DelegateSet.cpp preflight and preclaim changes, Permissions.cpp isDelegatable changes, Payment.cpp checkPermission changes, and the commit body. The evidence supports a delegated-permission authorization/validation fix. It does not show a concrete exploit transaction, demonstrated impact, or a separate security claim for MPT support. Protocol security invariant: Delegated permissions should authorize only valid and currently available transaction or granular permission values, and delegated PaymentMint/PaymentBurn permission should not authorize cross-currency SendMax/Amount exchange behavior. Verification notes: No concrete exploit transaction is shown in the provided evidence. No privilege escalation beyond delegated transaction permission misuse is proven. No evidence is provided for consensus failure, funds theft, or remote code execution. Pre-amendment behavior is intentionally preserved, so the classification is scoped to fixDelegateV1_1 behavior. MPT support changes are mentioned but not enough evidence is provided to classify them as security-relevant independently. No commands or external context were used. Classification is limited to the supplied snippets and commit text. Confidence is medium because the security invariant is clear, but exploitability and impact are not demonstrated. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final tags: `blockchain-core, transaction-processing, access-control, permission-delegation, protocol-hardening`

The supplied evidence supports retaining this as security hardening, not a proven security fix. The patch tightens delegated transaction permission validation, rejects invalid or unavailable permission values under the new amendment, and constrains delegated PaymentMint/PaymentBurn behavior to avoid cross-currency SendMax/Amount combinations. These are security-sensitive authorization restrictions, but the evidence does not show a concrete exploit, demonstrated privilege escalation, theft, consensus failure, or signature-related issue.

## Security Evidence

1. DelegateSet preflight now rejects non-delegatable permission values when fixDelegateV1_1 is enabled.
2. Permission::isDelegatable now maps permission values through permissionToTxType and rejects unknown transaction permissions under the amendment.
3. Added comments state that before fixDelegateV1_1, transactions from amendments not yet enabled could still be delegated.
4. Payment::checkPermission now rejects delegated PaymentMint/PaymentBurn paths where SendMax.asset differs from Amount.asset.

## Missing Evidence

1. No exploit transaction or demonstrated attack path is provided.
2. No concrete funds theft, consensus failure, or remote compromise impact is shown.
3. No evidence supports the original signature tag.
4. MPT support is mentioned in the commit body but not shown as security-relevant in the supplied snippets.

## Claim Boundaries

1. Classify as amendment-gated delegated-permission hardening rather than a proven exploitable vulnerability fix.
2. Scope the finding to DelegateSet permission validation and PaymentMint/PaymentBurn asset restrictions.
3. Do not claim signature validation impact from the supplied evidence.
4. Do not claim consensus failure or direct asset theft without additional evidence.
