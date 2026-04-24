---
case_id: case_20260402_111edef28
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
date: 2026-04-02
source_refs:
  - git:111edef284e05d19fee985f53bb7b6afcdad1a94
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:2546"
  - "src/xrpld/app/tx/detail/LoanManage.cpp:420"
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:2533"
  - "src/xrpld/app/tx/detail/LoanPay.cpp:151"
bug_class: ledger-accounting-invariant
impact_type:
  - ledger-integrity
  - protocol-accounting-integrity
tags:
  - blockchain-core
  - lending
  - loanbroker
  - ledger-accounting-invariant
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is a lending LoanBroker accounting-invariant hardening, not an access-control flaw or proven funds-theft vulnerability. The main code change in ValidLoanBroker::finalize keeps the existing lower-bound check and adds an amendment-gated upper-bound check rejecting LoanBroker state where sfCoverAvailable is greater than the pseudo-account's actual vault-asset balance.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `return true;` with `if (view.rules().enabled(fixSecurity3_1_3))`.

2. In `src/xrpld/app/tx/detail/LoanManage.cpp`, the patch replaces `return defaultLoan(view, loanSle, brokerSle, vaultSle, vaultAsset, j_);` with `auto const result = [&]() -> TER {`.

3. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `if (after->at(sfCoverAvailable) < accountHolds(` with `auto const pseudoBalance = accountHolds(`.

4. In `src/xrpld/app/tx/detail/LoanPay.cpp`, the patch replaces `return temINVALID_FLAG;` with `return ctx.view.rules().enabled(fixSecurity3_1_3)`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, which anchors the finding in the `access-control` area of the project. Historical context from `src/xrpld/app/tx/detail/VaultDeposit.cpp`, `src/xrpld/app/tx/detail/VaultClawback.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/VaultDeposit.cpp`, `src/xrpld/app/tx/detail/VaultClawback.cpp`. The strongest project-level identifiers around this patch are `view`, `vaultAsset`, `FreezeHandling::fhIGNORE_FREEZE`, and `AuthHandling::ahIGNORE_AUTH`.

## Before/After Behavior

Before the patch, the visible invariant rejected LoanBroker state when sfCoverAvailable was less than the pseudo-account's vault-asset balance, then returned true. After the patch, the code stores that balance in pseudoBalance, preserves the lower-bound rejection, and under fixSecurity3_1_3 also rejects non-delete transactions where sfCoverAvailable is greater than pseudoBalance. LoanManage and LoanPay were also changed, but the supplied evidence does not establish them as the root cause of this invariant issue.

# Root Cause

The grounded root cause is incomplete LoanBroker cover accounting validation: the invariant was one-sided and did not check that recorded sfCoverAvailable was no greater than the pseudo-account's actual vault-asset holdings.

## Walkthrough

1. ValidLoanBroker::finalize reads the LoanBroker's vault and extracts the vault asset.

2. It computes the pseudo-account's holdings of that vault asset with accountHolds while ignoring freeze and authorization handling.

3. Before the patch, the invariant failed only when sfCoverAvailable was below the computed holdings.

4. The patch assigns the computed holdings to pseudoBalance so the same baseline can be reused.

5. The existing lower-bound failure is retained.

6. When fixSecurity3_1_3 is enabled, the patch adds a new failure if sfCoverAvailable exceeds pseudoBalance.

7. The new upper-bound check is skipped for ttLOAN_BROKER_DELETE because the changed code says sfCoverAvailable is not zeroed during deletion.

8. The evidence does not show the exact transaction sequence that could create an excessive sfCoverAvailable value.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 2533 | Computes the LoanBroker pseudo-account's vault-asset balance used as the accounting baseline for sfCoverAvailable. |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 2546 | Adds fixSecurity3_1_3-gated rejection when sfCoverAvailable exceeds the pseudo-account asset balance, excluding LoanBroker deletion. |
| src/xrpld/app/tx/detail/LoanManage.cpp | 420 | Lending state-change dispatcher for default, impair, and unimpair operations touched by the assorted lending fix. |
| src/xrpld/app/tx/detail/LoanPay.cpp | 151 | Changes the amendment-gated TER returned when overpayment is requested on a loan that does not allow it. |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:2546` (changes persisted or aggregate state handling)

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
                after->at(sfCoverAvailable) > pseudoBalance)
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/LoanManage.cpp:420` (changes a sensitive control or state-update path)

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
            return defaultLoan(
                view, loanSle, brokerSle, vaultSle, vaultAsset, j_);
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:2533` (changes aggregate state or economic accounting)

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

Context: `src/xrpld/app/tx/detail/LoanPay.cpp:151` (changes a sensitive control or state-update path)

Before
```cpp
JLOG(ctx.j.warn())
            << "Requested overpayment on a loan that doesn't allow it";
        return temINVALID_FLAG;
    }
```
After
```cpp
JLOG(ctx.j.warn())
            << "Requested overpayment on a loan that doesn't allow it";
        return ctx.view.rules().enabled(fixSecurity3_1_3)
            ? TER{tecNO_PERMISSION}
            : temINVALID_FLAG;
    }
```

# Fix Pattern

Compute the authoritative accounting baseline once and enforce both sides of the consistency invariant, with an explicit exception for a documented deletion lifecycle case.

## How It Was Fixed

InvariantCheck.cpp now stores the pseudo-account vault-asset balance in pseudoBalance, checks sfCoverAvailable against it in both directions under the relevant amendment, logs a fatal invariant failure on excess cover, and returns false. The deletion path is excluded from the new upper-bound check.

# Why It Matters

1. Prevents recorded LoanBroker cover from exceeding the pseudo-account's actual vault-asset balance.

2. Strengthens a one-sided ledger consistency check into a two-sided accounting invariant.

3. Keeps the finding scoped to lending accounting, not generic authorization.

4. Does not prove theft, signature bypass, or a complete exploit path from the provided evidence.

# Evidence Notes

Primary evidence is in src/xrpld/app/tx/detail/InvariantCheck.cpp around the ValidLoanBroker::finalize changes. The LoanPay return-code change and LoanManage lambda restructuring are related lending changes but do not independently establish the vulnerability thesis. The evidence supports security hardening of a protocol accounting invariant, with medium confidence because exploitability and the pre-patch path to invalid state are not shown. Protocol security invariant: A LoanBroker's recorded sfCoverAvailable should not diverge from the pseudo-account's actual holdings of the vault asset, using freeze/auth-ignored holdings as the accounting baseline. The patch adds the missing upper-bound check so sfCoverAvailable must not exceed the pseudo-account balance, except during LoanBroker deletion where the field is documented as not zeroed. Verification notes: The patch does not prove a caller could steal funds or bypass signatures. The evidence does not show a generic access-control flaw. The LoanPay return-code change alone is not enough to establish a security bug. The LoanManage lambda restructuring is not independently proven security-relevant from the supplied context. The exact pre-patch sequence that could create an over-reported sfCoverAvailable value is not shown. Confirmed supported subsystem is lending LoanBroker accounting, not access-control. Confirmed supported bug class is ledger-accounting-invariant. Downgraded impact claims that imply theft, privilege bypass, or generic authorization failure. Kept confidence at medium because the invariant change is clear but exploitability is not demonstrated. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `ledger-accounting-invariant`
Final impact type: `ledger-integrity, protocol-accounting-integrity`
Final tags: `blockchain-core, lending, loanbroker, ledger-accounting-invariant, security-hardening`

The supplied patch evidence supports keeping this as security hardening for a blockchain lending accounting invariant. The strongest change adds an amendment-gated invariant rejection when LoanBroker sfCoverAvailable exceeds the pseudo-account's actual vault-asset balance, excluding a documented delete lifecycle case. The evidence does not support the original access-control or privilege-misuse framing, nor does it prove a concrete exploit or funds theft path.

## Security Evidence

1. InvariantCheck.cpp adds a fixSecurity3_1_3-gated upper-bound check for sfCoverAvailable against pseudoBalance.
2. The check rejects non-delete LoanBroker state where recorded cover exceeds actual pseudo-account holdings.
3. The code logs a fatal invariant failure and returns false on the new excessive-cover condition.
4. The changed code is in ledger transaction/invariant handling for lending, a security-sensitive blockchain accounting path.

## Missing Evidence

1. No transaction sequence is shown that can create an excessive sfCoverAvailable value before the fix.
2. No exploit path, funds theft, signature bypass, or privilege escalation is demonstrated.
3. LoanManage lambda restructuring is not independently shown to fix security behavior.
4. LoanPay return-code change alone does not establish a security vulnerability.

## Claim Boundaries

1. Validate as lending LoanBroker accounting-invariant hardening, not access-control.
2. Do not claim privilege misuse or generic authorization bypass from this evidence.
3. Do not claim confirmed exploitability or asset theft.
4. Scope the corpus entry to protocol ledger-integrity hardening under fixSecurity3_1_3.
