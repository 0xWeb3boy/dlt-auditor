---
case_id: case_20260420_519d9057a
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2026-04-20
source_refs:
  - git:519d9057a19185c151fcde4e30fe0b7acd877554
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:1742"
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:1706"
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:1670"
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:1685"
bug_class: invariant-enforcement
impact_type:
  - ledger-integrity
  - permission-boundary-hardening
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - invariant-check
  - permissioned-domains
  - ledger-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch improves Permissioned Domain invariant checking in rippled by changing how affected Permissioned Domain ledger entries are recorded and finalized. The evidence supports an invariant-coverage or ledger-consistency fix, not an established vulnerability such as authorization bypass, credential forgery, funds theft, or domain takeover.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `return (sleStatus_[0] ? check(*sleStatus_[0], j) : true) &&` with `if (view.rules().enabled(fixPermissionedDomainInvariant))`.

2. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch removes `if (tx.getTxnType() != ttPERMISSIONED_DOMAIN_SET || result != tesSUCCESS)`.

3. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `auto check = [](SleStatus& sleStatus,` with `auto check = [isDel](`.

4. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `sleStatus.isSorted_ = (cred.first == credTx[sfIssuer]) &&` with `ss.isSorted_ = (cred.first == credTx[sfIssuer]) &&`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/xrpld/app/tx/detail/InvariantCheck.h`, `src/xrpld/app/tx/detail/applySteps.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/InvariantCheck.h`, `src/xrpld/app/tx/detail/applySteps.cpp`. The strongest project-level identifiers around this patch are `const`, `sleStatus`, `sleStatus_`, and `beast::Journal`.

## Before/After Behavior

Before the patch, `ValidPermissionedDomain::finalize` returned early unless the transaction was a successful `ttPERMISSIONED_DOMAIN_SET`, and it checked fixed status slots. After the patch, `visitEntry` records affected Permissioned Domain entries into a collection, and `finalize` applies amendment-gated logic that treats Permissioned Domain changes on non-`tesSUCCESS` results as invalid and validates collected entries on successful paths.

# Root Cause

The pre-fix invariant checker scoped Permissioned Domain validation too narrowly to successful PermissionedDomainSet transactions and fixed before/after status handling. The provided evidence does not show missing authorization or a concrete attacker path; it shows insufficient invariant coverage for affected Permissioned Domain ledger entries.

## Walkthrough

1. `visitEntry` observes before/after ledger-entry state during transaction application.

2. For `ltPERMISSIONED_DOMAIN` entries, it inspects `sfAcceptedCredentials`.

3. The checker derives credential uniqueness and ordering information using sorted credential data.

4. Previously, `finalize` skipped validation unless the transaction type was `ttPERMISSIONED_DOMAIN_SET` and the result was `tesSUCCESS`.

5. The patch records affected Permissioned Domain entry status records in `sleStatus_` instead of relying on fixed slots.

6. Under `fixPermissionedDomainInvariant`, `finalize` returns failure if a non-successful transaction has affected Permissioned Domain entries.

7. For successful transactions under the new gate, the finalizer checks collected credential structure state.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 1664 | Collects before/after Permissioned Domain ledger entries touched during transaction application and records credential ordering/uniqueness state. |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 1700 | Finalizes Permissioned Domain invariant validation after transaction application. |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 1736 | Adds feature-gated behavior requiring failed transactions to leave Permissioned Domain entries unaffected. |
| src/xrpld/app/tx/detail/InvariantCheck.h | 51 | Defines the invariant checker visit/finalize lifecycle used by transaction application. |
| include/xrpl/protocol/detail/features.macro | 0 | Introduces or references the amendment gate for the corrected Permissioned Domain invariant behavior. |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:1742` (changes a sensitive control or state-update path)

Before
```cpp
};

    return (sleStatus_[0] ? check(*sleStatus_[0], j) : true) &&
        (sleStatus_[1] ? check(*sleStatus_[1], j) : true);
}
```
After
```cpp
};

    if (view.rules().enabled(fixPermissionedDomainInvariant))
    {
        // No permissioned domains should be affected if the transaction failed
        if (result != tesSUCCESS)
            // If nothing changed, all is good. If there were changes, that's
            // bad.
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:1706` (changes a sensitive control or state-update path)

Before
```cpp
beast::Journal const& j)
{
    if (tx.getTxnType() != ttPERMISSIONED_DOMAIN_SET || result != tesSUCCESS)
        return true;

    auto check = [](SleStatus const& sleStatus, beast::Journal const& j) {
        if (!sleStatus.credentialsSize_)
```
After
```cpp
beast::Journal const& j)
{
    auto check = [](SleStatus const& sleStatus, beast::Journal const& j) {
        if (!sleStatus.credentialsSize_)
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:1670` (changes a sensitive control or state-update path)

Before
```cpp
return;

    auto check = [](SleStatus& sleStatus,
                    std::shared_ptr<SLE const> const& sle) {
        auto const& credentials = sle->getFieldArray(sfAcceptedCredentials);
        sleStatus.credentialsSize_ = credentials.size();
        auto const sorted = credentials::makeSorted(credentials);
        sleStatus.isUnique_ = !sorted.empty();
```
After
```cpp
return;

    auto check = [isDel](
                     std::vector<SleStatus>& sleStatus,
                     std::shared_ptr<SLE const> const& sle) {
        auto const& credentials = sle->getFieldArray(sfAcceptedCredentials);
        auto const sorted = credentials::makeSorted(credentials);
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:1685` (changes a sensitive control or state-update path)

Before
```cpp
{
                auto const& credTx = credentials[i++];
                sleStatus.isSorted_ = (cred.first == credTx[sfIssuer]) &&
                    (cred.second == credTx[sfCredentialType]);
                if (!sleStatus.isSorted_)
                    break;
            }
        }
```
After
```cpp
{
                auto const& credTx = credentials[i++];
                ss.isSorted_ = (cred.first == credTx[sfIssuer]) &&
                    (cred.second == credTx[sfCredentialType]);
                if (!ss.isSorted_)
                    break;
            }
        }
```

# Fix Pattern

Broaden invariant checking from a narrow transaction-type/result gate to amendment-gated validation based on affected Permissioned Domain ledger entries.

## How It Was Fixed

The patch removes the early return that limited validation to successful PermissionedDomainSet transactions, changes `visitEntry` to append per-entry `SleStatus` records, and adds amendment-gated finalization logic for failed and successful transaction outcomes.

# Why It Matters

1. Improves ledger invariant coverage for Permissioned Domain entries.

2. Aligns validation with observed ledger-entry mutations rather than only transaction type.

3. Adds explicit handling for non-successful transaction results in the invariant checker.

4. Security relevance is plausible because this is transaction invariant logic, but the provided evidence does not establish a vulnerability.

# Evidence Notes

Grounded evidence is limited to `InvariantCheck.cpp` changes in `ValidPermissionedDomain::visitEntry` and `ValidPermissionedDomain::finalize`, plus the feature gate. The evidence does not support the heuristic baseline's access-control claim or any concrete exploit impact. Treat helper/test files as support code only. Protocol security invariant: Permissioned Domain ledger entries are expected to satisfy structural invariants for accepted credentials, including non-empty credentials, uniqueness, and sorted order, and the corrected invariant logic treats Permissioned Domain changes on non-successful transaction results as invalid under the amendment gate. Verification notes: The patch does not prove an authorization bypass or missing permission check. The evidence does not show a concrete exploit path or attacker-controlled transaction sequence. The evidence does not prove funds theft, credential forgery, or direct domain takeover. The change is to invariant enforcement/validation, not the core Permissioned Domain transaction authorization logic. Feature-gated behavior means pre-amendment and post-amendment semantics may differ. No concrete exploit path is shown in the provided input. No authorization bypass is evidenced by the changed hunks. No funds theft, credential forgery, or domain takeover is demonstrated. Classification is downgraded from likely security-hardening to unclear. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `invariant-enforcement`
Final impact type: `ledger-integrity, permission-boundary-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, invariant-check, permissioned-domains, ledger-integrity`

The patch does not prove a concrete exploitable vulnerability such as authorization bypass, credential forgery, or funds theft, so it should not be treated as a security-fix. However, the evidence does show a focused tightening of transaction invariant enforcement for Permissioned Domain ledger entries: failed transactions must not affect them, and successful paths validate recorded credential structure across affected entries. Because Permissioned Domains and accepted credentials are security-sensitive ledger state, this is best retained as security-hardening with conservative metadata.

## Security Evidence

1. Adds amendment-gated invariant behavior for Permissioned Domain ledger entries.
2. Explicitly treats Permissioned Domain changes during non-successful transactions as invalid.
3. Broadens validation beyond successful ttPERMISSIONED_DOMAIN_SET transactions to affected Permissioned Domain entries.
4. Checks credential structure properties such as non-empty credentials, uniqueness, and sorted order in invariant logic.

## Missing Evidence

1. No concrete attacker-controlled transaction sequence is shown.
2. No demonstrated authorization bypass or missing permission check is shown.
3. No evidence of funds theft, credential forgery, or domain takeover is provided.
4. No direct explanation from commit body links the change to a disclosed vulnerability.

## Claim Boundaries

1. Retain only as security-hardening, not as a confirmed security-fix.
2. Do not claim access-control bypass from the supplied patch alone.
3. Do not claim exploitability or direct asset loss.
4. The supported claim is improved invariant enforcement for security-sensitive Permissioned Domain ledger state.
