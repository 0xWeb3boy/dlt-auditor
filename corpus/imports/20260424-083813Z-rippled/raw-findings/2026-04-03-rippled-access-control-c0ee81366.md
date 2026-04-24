---
case_id: case_20260403_c0ee81366
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: access-control
confidence: medium
source_quality: high
date: 2026-04-03
source_refs:
  - git:c0ee81366674cd7ca395139d3bc2ea2cc0f943b2
  - "src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp:189"
  - "src/libxrpl/tx/transactors/lending/LoanManage.cpp:387"
  - "src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp:176"
  - "src/libxrpl/tx/transactors/lending/LoanPay.cpp:156"
bug_class: ledger-accounting-invariant
impact_type:
  - ledger-integrity
  - accounting-consistency
tags:
  - blockchain-core
  - lending-protocol
  - ledger-invariant
  - accounting-consistency
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The best-supported finding is a Lending Protocol loan-broker accounting invariant hardening. The primary change tightens ValidLoanBroker::finalize from a one-sided lower-bound check into an amendment-gated two-sided consistency check between sfCoverAvailable and the broker pseudo-account's actual vault-asset balance. The evidence does not support the earlier access-control framing or a direct exploit/profit claim.

## Observed Patch Facts

1. In `src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp`, the patch replaces `return true;` with `if (view.rules().enabled(fixSecurity3_1_3))`.

2. In `src/libxrpl/tx/transactors/lending/LoanManage.cpp`, the patch replaces `return impairLoan(view, loanSle, vaultSle, vaultAsset, j_);` with `auto const result = [&]() -> TER {`.

3. In `src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp`, the patch replaces `if (after->at(sfCoverAvailable) < accountHolds(` with `auto const pseudoBalance = accountHolds(`.

4. In `src/libxrpl/tx/transactors/lending/LoanPay.cpp`, the patch replaces `return temINVALID_FLAG;` with `return ctx.view.rules().enabled(fixSecurity3_1_3) ? TER{tecNO_PERMISSION} : temINVALI...`.

## Project Context

The changed code sits primarily in `src/libxrpl/tx/invariants`, `src/libxrpl/tx`, `src/libxrpl/tx/transactors/lending`, which anchors the finding in the `access-control` area of the project. Historical context from `src/libxrpl/tx/transactors/lending/LoanSet.cpp`, `src/libxrpl/tx/transactors/lending/LoanDelete.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/libxrpl/tx/transactors/vault/VaultDeposit.cpp`, `src/libxrpl/tx/transactors/vault/VaultClawback.cpp`. The strongest project-level identifiers around this patch are `vaultAsset`, `view`, `FreezeHandling::fhIGNORE_FREEZE`, and `AuthHandling::ahIGNORE_AUTH`.

## Before/After Behavior

Before the patch, ValidLoanBroker::finalize computed the broker pseudo-account's vault-asset balance and rejected only cases where sfCoverAvailable was less than that balance. After the patch, the computed value is stored as pseudoBalance, the lower-bound check remains, and fixSecurity3_1_3 adds a non-delete upper-bound check rejecting sfCoverAvailable greater than pseudoBalance. LoanManage also routes manage actions through a common result path and associates affected loan and broker entries with vaultAsset. LoanPay changes the result code for disallowed overpayment under the same amendment, but the evidence supports only result-code correction there.

# Root Cause

The pre-patch invariant treated LoanBroker cover consistency as a one-sided constraint. It did not reject live LoanBroker state where recorded sfCoverAvailable exceeded the broker pseudo-account's actual vault-asset holding. The supplied snippets do not establish how such state could be attacker-created or exploited.

## Walkthrough

1. ValidLoanBroker::finalize validates a LoanBroker ledger entry against the vault referenced by sfVaultID.

2. The invariant reads the vault asset and computes the broker pseudo-account's actual holding using accountHolds with freeze and auth ignored.

3. Before the patch, validation failed when sfCoverAvailable was lower than the computed pseudo-balance.

4. The invariant did not fail when sfCoverAvailable was higher than the computed pseudo-balance.

5. After the patch, fixSecurity3_1_3 adds an upper-bound check for non-delete transactions.

6. LoanBroker deletion is excluded because the code comment says sfCoverAvailable is not zeroed on delete.

7. LoanManage changes appear to support consistent vault-asset association for loan and broker entries after manage operations.

8. LoanPay's changed return code is not enough to establish a separate vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp | 176 | Computes the LoanBroker pseudo-account vault-asset balance and enforces sfCoverAvailable is not below that balance. |
| src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp | 189 | Adds the fixSecurity3_1_3 check that rejects live LoanBrokers whose sfCoverAvailable exceeds the pseudo-account asset balance. |
| src/libxrpl/tx/transactors/lending/LoanManage.cpp | 387 | Routes loan manage actions through a common result path and associates the loan and broker entries with the vault asset. |
| src/libxrpl/tx/transactors/lending/LoanPay.cpp | 156 | Changes the failure code for disallowed loan overpayment under fixSecurity3_1_3. |

## Code Snippets

## Snippet 1

Context: `src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp:189` (changes persisted or aggregate state handling)

Before
```cpp
return false;
        }
    }
    return true;
```
After
```cpp
return false;
        }

        if (view.rules().enabled(fixSecurity3_1_3))
        {
            // Don't check the balance when LoanBroker is deleted,
            // sfCoverAvailable is not zeroed
            if (tx.getTxnType() != ttLOAN_BROKER_DELETE &&
```

## Snippet 2

Context: `src/libxrpl/tx/transactors/lending/LoanManage.cpp:387` (changes a sensitive control or state-update path)

Before
```cpp
auto const vaultAsset = vaultSle->at(sfAsset);

    // Valid flag combinations are checked in preflight. No flags is valid -
    // just a noop.
    if (tx.isFlag(tfLoanDefault))
        return defaultLoan(view, loanSle, brokerSle, vaultSle, vaultAsset, j_);
    if (tx.isFlag(tfLoanImpair))
        return impairLoan(view, loanSle, vaultSle, vaultAsset, j_);
```
After
```cpp
auto const vaultAsset = vaultSle->at(sfAsset);

    auto const result = [&]() -> TER {
        // Valid flag combinations are checked in preflight. No flags is valid -
        // just a noop.
        if (tx.isFlag(tfLoanDefault))
            return defaultLoan(view, loanSle, brokerSle, vaultSle, vaultAsset, j_);
        if (tx.isFlag(tfLoanImpair))
```

## Snippet 3

Context: `src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp:176` (changes aggregate state or economic accounting)

Before
```cpp
}
        auto const& vaultAsset = vault->at(sfAsset);
        if (after->at(sfCoverAvailable) < accountHolds(
                                              view,
                                              after->at(sfAccount),
                                              vaultAsset,
                                              FreezeHandling::fhIGNORE_FREEZE,
                                              AuthHandling::ahIGNORE_AUTH,
```
After
```cpp
}
        auto const& vaultAsset = vault->at(sfAsset);
        auto const pseudoBalance = accountHolds(
            view,
            after->at(sfAccount),
            vaultAsset,
            FreezeHandling::fhIGNORE_FREEZE,
            AuthHandling::ahIGNORE_AUTH,
```

## Snippet 4

Context: `src/libxrpl/tx/transactors/lending/LoanPay.cpp:156` (changes a sensitive control or state-update path)

Before
```cpp
{
        JLOG(ctx.j.warn()) << "Requested overpayment on a loan that doesn't allow it";
        return temINVALID_FLAG;
    }
```
After
```cpp
{
        JLOG(ctx.j.warn()) << "Requested overpayment on a loan that doesn't allow it";
        return ctx.view.rules().enabled(fixSecurity3_1_3) ? TER{tecNO_PERMISSION} : temINVALID_FLAG;
    }
```

# Fix Pattern

Tighten a protocol ledger invariant from a one-sided bound to an amendment-gated consistency check, while preserving a documented lifecycle exception for deletion.

## How It Was Fixed

The patch introduces pseudoBalance as the shared computed accountHolds value, keeps the existing sfCoverAvailable < pseudoBalance rejection, and adds a fixSecurity3_1_3-gated rejection when sfCoverAvailable > pseudoBalance for transactions other than ttLOAN_BROKER_DELETE. It also adds related asset association handling in LoanManage and adjusts a LoanPay error code under the same amendment.

# Why It Matters

1. Keeps live LoanBroker cover accounting aligned with actual pseudo-account holdings.

2. Closes an invariant gap where over-reported available cover was not rejected.

3. Supports lending ledger consistency under the security amendment.

4. Does not prove a direct authorization bypass or attacker profit path.

# Evidence Notes

The strongest evidence is in src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp around the accountHolds computation and the new fixSecurity3_1_3 upper-bound check. LoanManage.cpp provides supporting consistency evidence through vaultAsset association. LoanPay.cpp shows an amendment-gated return-code change, but not a standalone security issue. Claims about access control, missing signer checks, or direct exploitation are unsupported by the provided snippets. Protocol security invariant: For a live LoanBroker, recorded sfCoverAvailable should remain consistent with the broker pseudo-account's actual holding of the vault asset. The provided evidence shows the invariant already rejected sfCoverAvailable below the pseudo-balance and, under fixSecurity3_1_3, now also rejects sfCoverAvailable above it, except during LoanBroker deletion where sfCoverAvailable is documented as not zeroed. Verification notes: The patch does not prove a direct exploit path or attacker-controlled profit scenario. The evidence does not show a missing signer, owner, or role authorization check. The LoanPay change alone looks like result-code correction, not a standalone vulnerability fix. The LoanManage asset association change is tied to ledger consistency, but the exact pre-patch failure mode is not fully proven from the snippets. The invariant excludes LoanBroker deletion, so the new equality requirement is not universal across all transaction types. Downgraded bug class from access-control to ledger-accounting-invariant. Downgraded confidence from high to medium because exploitability is not shown. Kept security verdict as likely hardening due to the amendment-gated invariant tightening in a protocol accounting path. Excluded standalone LoanPay vulnerability claims. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `ledger-accounting-invariant`
Final impact type: `ledger-integrity, accounting-consistency`
Final tags: `blockchain-core, lending-protocol, ledger-invariant, accounting-consistency`

The supplied patch evidence supports retaining this as security hardening, but not as an access-control or privilege-misuse finding. The strongest evidence is an amendment-gated LoanBroker invariant tightening that rejects live ledger state where sfCoverAvailable exceeds the broker pseudo-account asset balance. That is security-sensitive protocol accounting hardening in a blockchain lending subsystem, though the snippets do not prove an attacker-controlled exploit path or concrete loss scenario.

## Security Evidence

1. Adds fixSecurity3_1_3-gated invariant logic in LoanBrokerInvariant.cpp.
2. Changes LoanBroker validation from a one-sided lower-bound check to a two-sided consistency check for non-delete transactions.
3. Compares sfCoverAvailable against the pseudo-account's actual vault-asset balance from accountHolds.
4. Applies in a blockchain lending protocol ledger invariant path.

## Missing Evidence

1. No proof of how invalid sfCoverAvailable state could be created by an attacker.
2. No demonstrated authorization bypass, signer bug, or role-check failure.
3. No concrete exploit, asset theft, insolvency, or profit path shown in the provided evidence.
4. LoanPay change appears to be a result-code correction rather than an independently proven security fix.

## Claim Boundaries

1. Validate as protocol accounting invariant hardening, not access control.
2. Do not claim privilege misuse based on the supplied snippets.
3. Do not claim direct exploitability or financial loss.
4. The new equality-style check excludes LoanBroker deletion because sfCoverAvailable is documented as not zeroed there.
