---
case_id: case_20260403_b30b4e1d6
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
  - git:b30b4e1d654106e8d291bc998a0b87617783c868
  - "src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp:189"
  - "src/libxrpl/tx/transactors/lending/LoanManage.cpp:387"
  - "src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp:176"
  - "src/libxrpl/tx/transactors/lending/LoanPay.cpp:156"
bug_class: protocol-accounting-invariant
impact_type:
  - ledger-state-integrity
  - economic-accounting-integrity
tags:
  - blockchain-core
  - lending-protocol
  - accounting-invariant
  - ledger-state-integrity
  - amendment-gated
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The grounded finding is lending protocol accounting hardening, not access control. The strongest supported change is in LoanBrokerInvariant.cpp, where the invariant now computes the pseudo-account balance once and, under fixSecurity3_1_3, rejects non-delete LoanBroker states with sfCoverAvailable greater than that balance. The evidence does not establish an exploit chain, asset theft, or signer bypass.

## Observed Patch Facts

1. In `src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp`, the patch replaces `return true;` with `if (view.rules().enabled(fixSecurity3_1_3))`.

2. In `src/libxrpl/tx/transactors/lending/LoanManage.cpp`, the patch replaces `return impairLoan(view, loanSle, vaultSle, vaultAsset, j_);` with `auto const result = [&]() -> TER {`.

3. In `src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp`, the patch replaces `if (after->at(sfCoverAvailable) < accountHolds(` with `auto const pseudoBalance = accountHolds(`.

4. In `src/libxrpl/tx/transactors/lending/LoanPay.cpp`, the patch replaces `return temINVALID_FLAG;` with `return ctx.view.rules().enabled(fixSecurity3_1_3) ? TER{tecNO_PERMISSION} : temINVALI...`.

## Project Context

The changed code sits primarily in `src/libxrpl/tx/invariants`, `src/libxrpl/tx`, `src/libxrpl/tx/transactors/lending`, which anchors the finding in the `access-control` area of the project. Historical context from `src/libxrpl/tx/transactors/lending/LoanSet.cpp`, `src/libxrpl/tx/transactors/lending/LoanDelete.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/libxrpl/tx/transactors/vault/VaultDeposit.cpp`, `src/libxrpl/tx/transactors/vault/VaultClawback.cpp`. The strongest project-level identifiers around this patch are `vaultAsset`, `view`, `FreezeHandling::fhIGNORE_FREEZE`, and `AuthHandling::ahIGNORE_AUTH`.

## Before/After Behavior

Before the patch, the visible LoanBroker invariant rejected sfCoverAvailable values below the pseudo-account asset balance. After the patch, it keeps that lower-bound check and adds an amendment-gated upper-bound check for non-delete transactions. LoanManage.cpp also wraps management actions and then associates loan and broker entries with vaultAsset, while LoanPay.cpp changes the amendment-gated error code for disallowed overpayment from temINVALID_FLAG to tecNO_PERMISSION.

# Root Cause

The visible root cause is an under-specified LoanBroker accounting invariant: the code enforced one side of the relationship between sfCoverAvailable and the pseudo-account balance but did not show an equivalent upper-bound rejection. The evidence does not prove which transaction could create an overstated sfCoverAvailable state.

## Walkthrough

1. ValidLoanBroker::finalize reads the related vault and derives the vault asset used for the LoanBroker accounting check.

2. The invariant computes the pseudo-account's holdings for the vault asset with freeze and auth ignored.

3. Pre-patch evidence shows a rejection when sfCoverAvailable is less than the pseudo-account balance.

4. The patch stores that balance as pseudoBalance and reuses it for the added comparison.

5. When fixSecurity3_1_3 is enabled, non-delete LoanBroker states now fail the invariant if sfCoverAvailable is greater than pseudoBalance.

6. The upper-bound check is skipped for ttLOAN_BROKER_DELETE because the code comment says sfCoverAvailable is not zeroed during deletion.

7. LoanManage.cpp and LoanPay.cpp contain related lending-protocol fixes, but the provided evidence does not make them the primary vulnerability cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp | 176 | computes pseudo-account vault asset balance and enforces LoanBroker cover accounting bounds |
| src/libxrpl/tx/invariants/LoanBrokerInvariant.cpp | 189 | adds amendment-gated rejection when sfCoverAvailable exceeds pseudo-account balance, except broker deletion |
| src/libxrpl/tx/transactors/lending/LoanManage.cpp | 387 | applies loan management action and then associates loan and broker state with the vault asset |
| src/libxrpl/tx/transactors/lending/LoanPay.cpp | 156 | returns amendment-gated permission-style failure for overpayment when the loan disallows it |

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

Add an amendment-gated invariant check that constrains recorded protocol accounting to the actual backing pseudo-account balance, with an explicit lifecycle exception for deletion.

## How It Was Fixed

The patch computes pseudoBalance from accountHolds for the LoanBroker pseudo-account and vault asset, preserves the existing lower-bound rejection, and adds a fixSecurity3_1_3-gated rejection for sfCoverAvailable greater than pseudoBalance unless the transaction is ttLOAN_BROKER_DELETE. Related lending paths were adjusted to associate managed loan and broker state with vaultAsset and to return tecNO_PERMISSION for disallowed overpayment under the same amendment.

# Why It Matters

1. Protects consistency between recorded LoanBroker cover and backing pseudo-account holdings.

2. Reduces the chance that non-delete ledger states can overstate available cover.

3. Avoids applying the new equality-style constraint to a deletion lifecycle state where the field is intentionally not zeroed.

4. Does not by itself prove external exploitability or asset theft.

# Evidence Notes

Supported by LoanBrokerInvariant.cpp changes at the provided line 176 and line 189 excerpts. The LoanManage.cpp and LoanPay.cpp excerpts are supporting related fixes, but the evidence does not show they are the root cause of a security flaw. Claims of access-control bypass, signer authorization failure, or concrete theft are unsupported and should be excluded. Protocol security invariant: A LoanBroker's recorded sfCoverAvailable should not exceed the actual vault asset balance held by its pseudo-account for non-delete LoanBroker states. The deletion path is explicitly exempted because sfCoverAvailable is not zeroed there. Verification notes: The patch does not prove an externally exploitable asset theft path. The visible evidence does not show missing signer authorization or role bypass. The LoanPay return-code change alone is not enough to establish a security vulnerability. The LoanBroker deletion exception means equality is not enforced for all transaction types. The exact pre-patch state transition that could create overstated sfCoverAvailable is not fully shown. No external advisory or issue text is provided. The exact pre-patch transition that could create sfCoverAvailable greater than pseudoBalance is not shown. The amendment name fixSecurity3_1_3 supports security relevance but does not prove exploitability. Confidence is medium because the invariant change is clear but the full vulnerability thesis is incomplete. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `protocol-accounting-invariant`
Final impact type: `ledger-state-integrity, economic-accounting-integrity`
Final tags: `blockchain-core, lending-protocol, accounting-invariant, ledger-state-integrity, amendment-gated`

The supplied patch evidence supports retaining this as security hardening, but not as an access-control or concrete exploit fix. The strongest evidence is an amendment-gated LoanBroker invariant that rejects non-delete states where recorded sfCoverAvailable exceeds the pseudo-account asset balance. That tightens a security-sensitive blockchain lending accounting invariant, while the patch does not prove asset theft, signer bypass, or a specific exploitable transition.

## Security Evidence

1. LoanBrokerInvariant.cpp adds fixSecurity3_1_3-gated validation for sfCoverAvailable greater than pseudoBalance.
2. The new check compares recorded LoanBroker cover against actual pseudo-account holdings for the vault asset.
3. The check applies to non-delete LoanBroker states and logs an invariant failure on violation.
4. The changed code is in blockchain lending protocol transaction and invariant paths.
5. The amendment name fixSecurity3_1_3 supports security relevance, though not exploitability.

## Missing Evidence

1. No concrete transaction sequence is shown that creates sfCoverAvailable greater than pseudoBalance.
2. No advisory, issue text, or vulnerability description is supplied.
3. No evidence shows asset theft, fund loss, signer bypass, or unauthorized role use.
4. LoanManage and LoanPay excerpts appear related but do not independently establish a security flaw.

## Claim Boundaries

1. Classify as lending protocol accounting hardening, not access control.
2. Do not claim privilege misuse or authorization bypass from this evidence.
3. Do not claim a proven exploitable vulnerability or asset theft path.
4. The validated behavior is limited to enforcing LoanBroker cover accounting consistency for non-delete states.
