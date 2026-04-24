---
case_id: case_20260403_c979643d0
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: access-control
source_quality: high
date: 2026-04-03
source_refs:
  - git:c979643d01be9ffd923bf972ff6db7053c412174
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:2546"
  - "src/xrpld/app/tx/detail/LoanManage.cpp:419"
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:2533"
  - "src/xrpld/app/tx/detail/LoanPay.cpp:150"
bug_class: accounting-invariant
impact_type:
  - economic-integrity
confidence: medium
tags:
  - blockchain-core
  - lending-protocol
  - accounting-invariant
  - amendment-gated
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an amendment-gated LoanBroker accounting invariant and makes adjacent lending protocol adjustments. The strongest grounded change is in ValidLoanBroker::finalize, where sfCoverAvailable is now checked against the broker pseudo-account balance in both directions. The evidence supports an accounting consistency fix or hardening change, but it does not establish an exploitable vulnerability or attacker-controlled path.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `return true;` with `if (view.rules().enabled(fixSecurity3_1_3))`.

2. In `src/xrpld/app/tx/detail/LoanManage.cpp`, the patch replaces `return defaultLoan(view, loanSle, brokerSle, vaultSle, vaultAsset, j_);` with `auto const result = [&]() -> TER {`.

3. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `if (after->at(sfCoverAvailable) < accountHolds(` with `auto const pseudoBalance = accountHolds(`.

4. In `src/xrpld/app/tx/detail/LoanPay.cpp`, the patch replaces `return temINVALID_FLAG;` with `return ctx.view.rules().enabled(fixSecurity3_1_3)`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, which anchors the finding in the `access-control` area of the project. Historical context from `src/xrpld/app/tx/detail/VaultDeposit.cpp`, `src/xrpld/app/tx/detail/VaultClawback.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/VaultDeposit.cpp`, `src/xrpld/app/tx/detail/VaultClawback.cpp`. The strongest project-level identifiers around this patch are `vaultAsset`, `view`, `FreezeHandling::fhIGNORE_FREEZE`, and `AuthHandling::ahIGNORE_AUTH`.

## Before/After Behavior

Before the patch, ValidLoanBroker::finalize failed when sfCoverAvailable was less than the broker pseudo-account's vault asset balance, then returned true without checking whether sfCoverAvailable was greater than that balance. After the patch, the accountHolds result is stored as pseudoBalance, the existing less-than check remains, and under fixSecurity3_1_3 a greater-than mismatch also fails, except for ttLOAN_BROKER_DELETE because sfCoverAvailable is documented as not zeroed during deletion. LoanManage::doApply now routes management actions through a TER-producing lambda before associating vault asset state with loan and broker records. LoanPay::preclaim returns tecNO_PERMISSION instead of temINVALID_FLAG for disallowed overpayment under the same amendment.

# Root Cause

The observable issue is an incomplete LoanBroker accounting invariant: the previous check only rejected one side of a mismatch between sfCoverAvailable and the broker pseudo-account's backing vault asset balance. The provided evidence does not show how such a mismatch could be created or exploited.

## Walkthrough

1. ValidLoanBroker::finalize reads the LoanBroker vault through sfVaultID and obtains the vault asset.

2. It computes the broker pseudo-account's holding of that vault asset with accountHolds using freeze and auth ignoring modes.

3. Before the patch, the invariant failed only if sfCoverAvailable was below the computed balance.

4. The patch names the computed balance pseudoBalance and keeps the existing lower-bound failure.

5. Under fixSecurity3_1_3, the patch also fails if sfCoverAvailable is greater than pseudoBalance.

6. The new greater-than check is skipped for ttLOAN_BROKER_DELETE because the code comment says sfCoverAvailable is not zeroed on deletion.

7. LoanManage::doApply is adjusted so management actions return through a lambda before loan and broker asset association is performed.

8. LoanPay::preclaim changes the amendment-gated result code for disallowed overpayment to tecNO_PERMISSION.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 2533 | computes LoanBroker pseudo-account holdings for the vault asset and compares them with sfCoverAvailable |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 2546 | adds fixSecurity3_1_3 invariant failure when LoanBroker cover available exceeds backing pseudo-account balance, except broker deletion |
| src/xrpld/app/tx/detail/LoanManage.cpp | 419 | routes loan default/impair/unimpair/noop management actions and then associates vault asset state with loan and broker records |
| src/xrpld/app/tx/detail/LoanPay.cpp | 150 | returns tecNO_PERMISSION for disallowed loan overpayment under fixSecurity3_1_3 |

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
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/LoanManage.cpp:419` (changes a sensitive control or state-update path)

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

Context: `src/xrpld/app/tx/detail/LoanPay.cpp:150` (changes a sensitive control or state-update path)

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

Add an amendment-gated invariant check for the missing side of an accounting relationship, while preserving an explicitly documented exceptional transaction case and aligning nearby lending protocol behavior.

## How It Was Fixed

The fix stores the broker pseudo-account asset balance in pseudoBalance and adds a fixSecurity3_1_3-gated comparison that rejects sfCoverAvailable values greater than that balance. It keeps the existing check for sfCoverAvailable values below the balance and excludes LoanBroker deletion from the new check. Nearby changes restructure LoanManage result handling before asset association and adjust LoanPay's amendment-gated error code for disallowed overpayment.

# Why It Matters

1. Improves consistency checking for LoanBroker cover accounting.

2. Detects over-covered as well as under-covered LoanBroker states after the amendment is enabled.

3. Preserves the documented LoanBroker deletion exception.

4. Does not by itself prove theft, unauthorized access, or direct fund loss.

# Evidence Notes

Primary evidence is from src/xrpld/app/tx/detail/InvariantCheck.cpp in ValidLoanBroker::finalize around the sfCoverAvailable and pseudoBalance comparisons. Supporting evidence includes LoanManage::doApply and LoanPay::preclaim changes under the same amendment. The evidence does not include an advisory, exploit scenario, transaction sequence, or proof that an attacker could create the rejected state. The LoanPay result-code change is not enough to classify this as access control. Protocol security invariant: LoanBroker cover accounting appears intended to remain consistent with the backing vault asset balance held by the broker pseudo-account. The patch adds an amendment-gated check that sfCoverAvailable must not exceed the pseudo-account asset balance, while preserving the existing lower-bound check and exempting LoanBroker deletion. Verification notes: The patch does not prove that an attacker could create an over-covered LoanBroker state before the fix. The patch does not prove theft, unauthorized withdrawal, or direct loss of funds. The LoanPay result-code change alone is not enough to establish an access-control vulnerability. The evidence does not show the full transaction sequence that would violate the invariant. The broker-delete exception is documented as an invariant special case, not proof of a deletion exploit. Confirmed as an accounting invariant change from the provided diff excerpts. Security relevance is plausible because the change is amendment-gated and in lending protocol invariant code. Exploitability is not established by the provided evidence. Not kept in the security corpus under strict vulnerability-fix criteria. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `accounting-invariant`
Final impact type: `economic-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, lending-protocol, accounting-invariant, amendment-gated, security-hardening`

The evidence supports retaining this as security hardening, not as a proven exploitable security fix. The strongest patch adds an amendment-gated invariant that rejects LoanBroker states where sfCoverAvailable exceeds the backing pseudo-account asset balance, closing a one-sided accounting consistency gap in a lending protocol path. The provided evidence does not prove attacker control, exploitation, theft, or unauthorized access, so the original access-control framing is too specific.

## Security Evidence

1. Adds fixSecurity3_1_3-gated validation in ValidLoanBroker::finalize.
2. New invariant rejects sfCoverAvailable greater than the broker pseudo-account asset balance.
3. Existing lower-bound check is preserved, making the cover accounting relationship bidirectional.
4. Change is in blockchain lending protocol state validation and invariant enforcement.
5. Patch explicitly handles a deletion exception where sfCoverAvailable is not zeroed.

## Missing Evidence

1. No advisory or security note is provided.
2. No exploit sequence shows how an invalid LoanBroker state could be created.
3. No evidence proves direct fund loss, theft, or unauthorized withdrawal.
4. LoanPay change appears to adjust result code semantics and does not independently prove access-control impact.
5. Tests are mentioned but not supplied with enough detail to establish exploitability.

## Claim Boundaries

1. Classify as security hardening rather than a confirmed vulnerability fix.
2. Do not claim access-control bypass from the supplied patch evidence.
3. Do not claim attacker exploitability or direct asset loss.
4. Ground the finding in LoanBroker accounting invariant enforcement.
5. Treat LoanManage and LoanPay changes as supporting context, not the primary security evidence.
