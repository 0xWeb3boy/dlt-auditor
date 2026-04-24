---
case_id: case_20251114_362ecbd1c
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: core-logic
confidence: medium
source_quality: high
date: 2025-11-14
source_refs:
  - git:362ecbd1cb5a4e7cd943ddc759d44cd2dba2bc6a
  - "src/xrpld/app/tx/detail/VaultDelete.cpp:147"
  - "src/xrpld/app/tx/detail/VaultCreate.cpp:80"
  - "src/xrpld/app/tx/detail/VaultCreate.cpp:136"
  - "src/xrpld/app/tx/detail/VaultDelete.cpp:199"
bug_class: resource-accounting
impact_type:
  - reserve-undercharging
  - ledger-state-accounting
tags:
  - blockchain-core
  - core-logic
  - vault
  - resource-accounting
  - reserve-accounting
  - ledger-consistency
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is reserve underaccounting for vault pseudo-accounts, not an authorization flaw. VaultCreate previously incremented OwnerCount by 1 even though the patched comment and code state that creating a vault creates both a Vault and a PseudoAccount. The fix increments by 2, makes VaultDelete decrement by 2, removes the custom VaultCreate base-fee reserve path shown in the diff, and adds consistency checks before removing the pseudo-account.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/VaultDelete.cpp`, the patch replaces `view().erase(view().peek(keylet::account(pseudoID)));` with `auto vaultPseudoSLE = view().peek(keylet::account(pseudoID));`.

2. In `src/xrpld/app/tx/detail/VaultCreate.cpp`, the patch replaces `XRPAmount` with `TER`.

3. In `src/xrpld/app/tx/detail/VaultCreate.cpp`, the patch replaces `adjustOwnerCount(view(), owner, 1, j_);` with `// We will create Vault and PseudoAccount, hence increase OwnerCount by 2`.

4. In `src/xrpld/app/tx/detail/VaultDelete.cpp`, the patch replaces `adjustOwnerCount(view(), owner, -1, j_);` with `// We are destroying Vault and PseudoAccount, hence decrease by 2`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, `src/xrpld/app/tx/detail/VaultDeposit.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, `src/xrpld/app/tx/detail/VaultDeposit.cpp`. The strongest project-level identifiers around this patch are `view`, `owner`, `keylet::account`, and `vault`.

## Before/After Behavior

Before the patch, VaultCreate linked a vault, adjusted the owner's count by 1, and checked the reserve against that count. After the patch, it adjusts the owner's count by 2 before the reserve check. Before the patch, VaultDelete directly erased the pseudo-account SLE returned by peek and decremented OwnerCount by 1. After the patch, it verifies the pseudo-account exists, is tied to the vault through sfVaultID, has zero balance, and then decrements OwnerCount by 2 for the destroyed vault and pseudo-account.

# Root Cause

Vault lifecycle accounting treated creation and deletion as a one-object owner-reserve change even though the changed path creates and destroys two vault-related ledger objects. The delete path also lacked explicit local consistency checks proving the pseudo-account being removed was the expected vault pseudo-account and had no remaining balance.

## Walkthrough

1. VaultCreate::doApply creates a Vault SLE and links it into the owner's directory.

2. The old create path called adjustOwnerCount(view(), owner, 1, j_) before checking accountReserve(ownerCount).

3. The patch states that VaultCreate creates both Vault and PseudoAccount and changes the increment to adjustOwnerCount(view(), owner, 2, j_).

4. The shown VaultCreate::calculateBaseFee implementation that returned calculateOwnerReserveFee(view, tx) is removed.

5. VaultDelete previously erased view().peek(keylet::account(pseudoID)) directly.

6. The patched delete path stores vaultPseudoSLE and rejects missing or mismatched pseudo-accounts with tefBAD_LEDGER.

7. The patched delete path rejects a nonzero pseudo-account balance with tecHAS_OBLIGATIONS.

8. VaultDelete changes the owner-count decrement from -1 to -2, matching the two destroyed vault-related objects.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/VaultCreate.cpp | 136 | creates vault and pseudo-account, increments owner reserve count for both objects, then enforces account reserve |
| src/xrpld/app/tx/detail/VaultDelete.cpp | 147 | validates the vault pseudo-account belongs to the vault and has no remaining balance before erase |
| src/xrpld/app/tx/detail/VaultDelete.cpp | 199 | decrements owner reserve count for both destroyed vault-related objects |
| src/xrpld/app/tx/detail/VaultCreate.cpp | 80 | removes custom base-fee owner reserve charging path, aligning reserve enforcement with OwnerCount accounting |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/VaultDelete.cpp:147` (changes persisted or aggregate state handling)

Before
```cpp
// Destroy the pseudo-account.
    view().erase(view().peek(keylet::account(pseudoID)));

    // Remove the vault from its owner's directory.
```
After
```cpp
// Destroy the pseudo-account.
    auto vaultPseudoSLE = view().peek(keylet::account(pseudoID));
    if (!vaultPseudoSLE || vaultPseudoSLE->at(~sfVaultID) != vault->key())
        return tefBAD_LEDGER;  // LCOV_EXCL_LINE

    // Making the payment and removing the empty holding should have deleted any
    // obligations associated with the vault or vault pseudo-account.
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/VaultCreate.cpp:80` (changes aggregate state or economic accounting)

Before
```cpp
}

XRPAmount
VaultCreate::calculateBaseFee(ReadView const& view, STTx const& tx)
{
    // One reserve increment is typically much greater than one base fee.
    return calculateOwnerReserveFee(view, tx);
}
```
After
```cpp
}

TER
VaultCreate::preclaim(PreclaimContext const& ctx)
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/VaultCreate.cpp:136` (changes an authorization or privilege gate)

Before
```cpp
if (auto ter = dirLink(view(), account_, vault))
        return ter;
    adjustOwnerCount(view(), owner, 1, j_);
    auto ownerCount = owner->at(sfOwnerCount);
    if (mPriorBalance < view().fees().accountReserve(ownerCount))
        return tecINSUFFICIENT_RESERVE;
```
After
```cpp
if (auto ter = dirLink(view(), account_, vault))
        return ter;
    // We will create Vault and PseudoAccount, hence increase OwnerCount by 2
    adjustOwnerCount(view(), owner, 2, j_);
    auto const ownerCount = owner->at(sfOwnerCount);
    if (mPriorBalance < view().fees().accountReserve(ownerCount))
        return tecINSUFFICIENT_RESERVE;
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/VaultDelete.cpp:199` (changes an authorization or privilege gate)

Before
```cpp
// LCOV_EXCL_STOP
    }
    adjustOwnerCount(view(), owner, -1, j_);

    // Destroy the vault.
```
After
```cpp
// LCOV_EXCL_STOP
    }

    // We are destroying Vault and PseudoAccount, hence decrease by 2
    adjustOwnerCount(view(), owner, -2, j_);

    // Destroy the vault.
```

# Fix Pattern

Make reserve accounting match the number of persistent ledger objects created and destroyed, and add ledger consistency checks before deleting related state.

## How It Was Fixed

VaultCreate::doApply now increases OwnerCount by 2 before enforcing the account reserve. VaultDelete::doApply now validates the pseudo-account's existence, vault association, and zero balance before deletion, then decreases OwnerCount by 2. The custom VaultCreate base-fee owner-reserve calculation shown in the evidence was removed.

# Why It Matters

1. Prevents vault pseudo-accounts from being left out of owner-reserve accounting.

2. Keeps create and delete reserve accounting symmetric.

3. Adds consistency guards around pseudo-account deletion.

4. Does not establish asset theft, vault takeover, or access-control bypass.

# Evidence Notes

The evidence supports reserve underaccounting and ledger consistency hardening in VaultCreate.cpp and VaultDelete.cpp. It does not support the heuristic baseline's access-control framing. Related deposit, withdraw, clawback, and settings files are not evidence of vulnerable behavior. The security relevance is economic/resource-accounting hardening; no direct exploit path beyond undercharged persistent ledger state is demonstrated. Protocol security invariant: Vault creation should reserve for every persistent ledger object it creates, including both the Vault object and its pseudo-account, and deletion should symmetrically release those counts only for the expected pseudo-account with no remaining balance or obligations. Verification notes: Not shown to be an access-control or privilege-check fix. No evidence of asset theft, unauthorized withdrawal, or vault takeover. No proof of arbitrary account deletion; added checks are ledger consistency guards around the expected pseudo-account. No demonstrated network-level denial of service; only reserve underaccounting for persistent ledger objects is supported by the patch. No claim that deposit, withdraw, clawback, or vault setting authorization paths were vulnerable. Confirmed by diff: OwnerCount create path changes from +1 to +2. Confirmed by diff: OwnerCount delete path changes from -1 to -2. Confirmed by diff: pseudo-account existence, sfVaultID, and balance checks were added before deletion. No evidence provided for unauthorized withdrawal, asset theft, arbitrary account deletion, or network-level denial of service. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-accounting`
Final impact type: `reserve-undercharging, ledger-state-accounting`
Final tags: `blockchain-core, core-logic, vault, resource-accounting, reserve-accounting, ledger-consistency`

The patch evidence supports a security-hardening classification, not an access-control or privilege-misuse finding. Vault creation previously counted one owner-reserve object while the patched code states it creates both a Vault and a PseudoAccount, then changes accounting to reserve for two objects. The delete path is made symmetric and adds consistency checks before pseudo-account removal. In a blockchain ledger, undercharging persistent state is security-relevant hardening, but the evidence does not prove a concrete exploit, theft, takeover, or authorization bypass.

## Security Evidence

1. VaultCreate changes OwnerCount adjustment from +1 to +2 before enforcing account reserve.
2. VaultDelete changes OwnerCount adjustment from -1 to -2, matching destruction of both Vault and PseudoAccount.
3. VaultDelete now checks the pseudo-account exists and is associated with the expected vault via sfVaultID before erasing it.
4. VaultDelete now rejects deletion when the pseudo-account still has a nonzero balance.

## Missing Evidence

1. No demonstrated exploit path showing network-level denial of service or ledger bloat at scale.
2. No evidence of unauthorized vault access, asset theft, withdrawal, or takeover.
3. No evidence that an attacker could delete arbitrary accounts; the added checks are local ledger consistency guards.
4. No commit body or tests are provided that explicitly frame this as a security vulnerability.

## Claim Boundaries

1. Treat this as reserve/accounting hardening for persistent ledger objects, not access control.
2. Do not claim privilege escalation, unauthorized withdrawal, or vault takeover from this evidence.
3. Do not claim a concrete security-fix unless additional evidence shows exploitability or security impact.
4. Supported impact is limited to under-reserved vault pseudo-account state and related ledger consistency checks.
