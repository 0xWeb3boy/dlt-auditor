---
case_id: case_20250411_da10ba6fd
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2025-04-11
source_refs:
  - git:da10ba6fd0528af5524620a55c99dec03d7438a8
  - "src/xrpld/app/tx/detail/LoanBrokerDelete.cpp:139"
  - "src/xrpld/app/tx/detail/LoanBrokerDelete.cpp:81"
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:436"
bug_class: ledger-state-integrity
impact_type:
  - ledger-integrity
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - ledger-state-integrity
  - obligation-validation
  - invariant-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is a ledger-state integrity fix in LoanBrokerDelete, not an access-control fix. The patch stops erasing the broker pseudo-account immediately after payment cleanup and first verifies that the pseudo-account has no remaining balance and owns no ledger objects.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/LoanBrokerDelete.cpp`, the patch replaces `view.erase(brokerPseudoSLE);` with `// Making the payment should have deleted any obligations`.

2. In `src/xrpld/app/tx/detail/LoanBrokerDelete.cpp`, the patch replaces `JLOG(ctx.j.warn()) << "LoanBrokerSet: Owner count is not zero";` with `JLOG(ctx.j.warn()) << "LoanBrokerDelete: Owner count is not zero";`.

3. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch removes `view.rules().enabled(featureSingleAssetVault) ||`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/xrpld/app/tx/detail/SetAccount.cpp`, `src/xrpld/app/tx/detail/DeleteAccount.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/Transactor.cpp`, `src/xrpld/app/tx/detail/OfferStream.cpp`. The strongest project-level identifiers around this patch are `view`, `warn`, `rules`, and `enabled`.

## Before/After Behavior

Before the patch, LoanBrokerDelete::doApply() retrieved brokerPseudoSLE and erased it directly with view.erase(brokerPseudoSLE). After the patch, the code checks sfBalance and sfOwnerCount on the pseudo-account and returns tecHAS_OBLIGATIONS if either indicates remaining obligations. The preclaim change is only a corrected warning string. The InvariantCheck change adjusts feature gating but is not enough by itself to establish a vulnerability.

# Root Cause

LoanBrokerDelete::doApply() relied on the assumption that the preceding payment step had removed all obligations from the broker pseudo-account, then deleted the account root without validating that assumption.

## Walkthrough

1. LoanBrokerDelete::preclaim() already checked that the submitting account matched the broker owner; the changed preclaim line only fixes diagnostic text.

2. The preclaim path also already rejected a broker with nonzero owner count.

3. In doApply(), the transaction performs a payment step expected to clear obligations tied to the broker or pseudo-account.

4. Before the patch, the code then erased brokerPseudoSLE directly.

5. After the patch, the code rejects deletion if the pseudo-account still has a nonzero sfBalance.

6. After the patch, the code also rejects deletion if the pseudo-account still has a nonzero sfOwnerCount.

7. The InvariantCheck feature-gate change is related ledger consistency context, but the provided evidence does not establish it as the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/LoanBrokerDelete.cpp | 139 | Prevents deleting the broker pseudo-account when balance or owned objects remain after payment cleanup. |
| src/xrpld/app/tx/detail/LoanBrokerDelete.cpp | 75 | Existing owner authorization and broker owner-count preclaim path; changed line is diagnostic text only. |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 436 | Adjusts account-root deletion invariant enforcement feature gating for related ledger consistency checks. |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/LoanBrokerDelete.cpp:139` (changes persisted or aggregate state handling)

Before
```cpp
return tefBAD_LEDGER;

    view.erase(brokerPseudoSLE);
```
After
```cpp
return tefBAD_LEDGER;

    // Making the payment should have deleted any obligations
    // associated with the broker or broker pseudo-account.
    if (*brokerPseudoSLE->at(sfBalance))
    {
        JLOG(j_.warn()) << "LoanBrokerDelete: Pseudo-account has a balance";
        return tecHAS_OBLIGATIONS;
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/LoanBrokerDelete.cpp:81` (changes an authorization or privilege gate)

Before
```cpp
if (sleBroker->at(sfOwnerCount) != 0)
    {
        JLOG(ctx.j.warn()) << "LoanBrokerSet: Owner count is not zero";
        return tecHAS_OBLIGATIONS;
    }
```
After
```cpp
if (sleBroker->at(sfOwnerCount) != 0)
    {
        JLOG(ctx.j.warn()) << "LoanBrokerDelete: Owner count is not zero";
        return tecHAS_OBLIGATIONS;
    }
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:436` (changes a sensitive control or state-update path)

Before
```cpp
[[maybe_unused]] bool const enforce =
        view.rules().enabled(featureInvariantsV1_1) ||
        view.rules().enabled(featureSingleAssetVault) ||
        view.rules().enabled(featureLendingProtocol);
```
After
```cpp
[[maybe_unused]] bool const enforce =
        view.rules().enabled(featureInvariantsV1_1) ||
        view.rules().enabled(featureLendingProtocol);
```

# Fix Pattern

Validate account-root cleanup conditions immediately before deletion, and reject the transaction if any balance or owned objects remain.

## How It Was Fixed

The direct view.erase(brokerPseudoSLE) path was replaced with explicit checks for sfBalance and sfOwnerCount that return tecHAS_OBLIGATIONS when obligations remain. The patch also corrected a misleading LoanBrokerDelete log message and adjusted AccountRootsDeletedClean feature gating.

# Why It Matters

1. Prevents deleting a broker pseudo-account with remaining balance.

2. Prevents deleting a broker pseudo-account that still owns ledger objects.

3. Protects a ledger-state invariant in a transaction apply path.

4. Does not support an access-control classification.

# Evidence Notes

The strongest evidence is src/xrpld/app/tx/detail/LoanBrokerDelete.cpp line 139, where direct deletion is replaced by balance and owner-count checks. The owner permission check was already present in the provided context, so access-control claims are unsupported. The InvariantCheck.cpp hunk is not independently sufficient to prove a vulnerability or exploit path. Protocol security invariant: A LoanBrokerDelete transaction must not delete the broker pseudo-account while that account still has ledger obligations, including a nonzero balance or owned ledger objects. Verification notes: The patch does not prove an attacker could exploit this on an enabled production network. The patch does not show a missing owner authorization check; owner validation was already present in the provided context. The log message correction is not security-relevant by itself. The evidence does not prove loss of funds, only prevention of deleting an account root with remaining obligations. The featureSingleAssetVault invariant-gate removal is not enough on its own to classify a vulnerability. Classified as missing obligation validation, not authorization bypass. Exploitability and concrete loss impact are not proven by the provided evidence. Confidence remains medium because the invariant violation is clear, but production attackability is not shown. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `ledger-state-integrity`
Final impact type: `ledger-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, ledger-state-integrity, obligation-validation, invariant-hardening`

The evidence supports keeping this as security hardening, not as a proven security fix and not as access control. The main implementation change prevents LoanBrokerDelete from erasing a broker pseudo-account while it still has a balance or owned objects, which tightens a security-sensitive ledger-state invariant in transaction processing. However, the provided patch does not prove exploitability, attacker control, production exposure, or concrete fund loss.

## Security Evidence

1. LoanBrokerDelete::doApply changed from directly erasing brokerPseudoSLE to checking sfBalance before deletion.
2. LoanBrokerDelete::doApply now returns tecHAS_OBLIGATIONS if the pseudo-account still has a nonzero balance.
3. LoanBrokerDelete::doApply now checks sfOwnerCount and rejects deletion if the pseudo-account still owns objects.
4. The changed code is in a blockchain transaction apply path where invalid ledger-state deletion is security-sensitive.

## Missing Evidence

1. No evidence shows an attacker could trigger the stale-obligation condition on a live network.
2. No evidence proves loss of funds, unauthorized asset movement, or consensus impact.
3. No evidence supports the original access-control or privilege-misuse classification.
4. The preclaim hunk is only a log-message correction.
5. The InvariantCheck feature-gating hunk is not independently tied to a demonstrated vulnerability.

## Claim Boundaries

1. Validate only as ledger-state integrity hardening around LoanBrokerDelete pseudo-account deletion.
2. Do not claim authorization bypass or privilege misuse from the supplied evidence.
3. Do not claim concrete exploitability or fund loss.
4. Do not treat the diagnostic log-message change as security-relevant by itself.
5. Do not rely on the InvariantCheck hunk as the primary root cause without more context.
