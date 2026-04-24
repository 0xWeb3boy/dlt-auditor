---
case_id: case_20251114_b195011ef
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
  - git:b195011effe54b703abc91e0a69a00607efb2c40
  - "src/xrpld/app/tx/detail/VaultDelete.cpp:166"
  - "src/xrpld/app/tx/detail/VaultCreate.cpp:99"
  - "src/xrpld/app/tx/detail/VaultCreate.cpp:155"
  - "src/xrpld/app/tx/detail/VaultDelete.cpp:218"
bug_class: resource-accounting
impact_type:
  - under-reserved-ledger-state
tags:
  - blockchain-core
  - core-logic
  - vault
  - reserve-accounting
  - pseudo-account-validation
  - owner-count-accounting
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is a Vault reserve-accounting fix, not an access-control issue. The patch changes Vault creation from accounting for one owner-reserved object to two, mirrors that on deletion, and adds validation before removing the Vault pseudo-account. The evidence supports security hardening around protocol resource accounting, but not a demonstrated exploit, theft path, authorization bypass, or consensus failure.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/VaultDelete.cpp`, the patch replaces `view().erase(view().peek(keylet::account(pseudoID)));` with `auto vaultPseudoSLE = view().peek(keylet::account(pseudoID));`.

2. In `src/xrpld/app/tx/detail/VaultCreate.cpp`, the patch replaces `XRPAmount` with `TER`.

3. In `src/xrpld/app/tx/detail/VaultCreate.cpp`, the patch replaces `adjustOwnerCount(view(), owner, 1, j_);` with `// We will create Vault and PseudoAccount, hence increase OwnerCount by 2`.

4. In `src/xrpld/app/tx/detail/VaultDelete.cpp`, the patch replaces `adjustOwnerCount(view(), owner, -1, j_);` with `// We are destroying Vault and PseudoAccount, hence decrease by 2`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, `src/xrpld/app/tx/detail/VaultDeposit.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, `src/xrpld/app/tx/detail/VaultDeposit.cpp`. The strongest project-level identifiers around this patch are `view`, `owner`, `keylet::account`, and `vault`.

## Before/After Behavior

Before the patch, VaultCreate::doApply increased OwnerCount by 1 before checking accountReserve even though the changed code states the transaction creates both a Vault and a PseudoAccount. VaultDelete::doApply decreased OwnerCount by 1 and directly erased the pseudo-account lookup result. After the patch, VaultCreate increases OwnerCount by 2 before the reserve check, VaultDelete decreases OwnerCount by 2, and deletion first verifies the pseudo-account exists, is linked to the vault through sfVaultID, and has no remaining balance.

# Root Cause

Vault owner-reserve accounting treated the Vault lifecycle as a one-object change even though the operation also involves a persistent pseudo-account. The delete path also lacked the newly added checks that the pseudo-account selected for removal is the matching empty pseudo-account for the vault.

## Walkthrough

1. VaultCreate::doApply creates and links a Vault ledger entry.

2. Before the fix, the owner count was increased by 1 before checking the required account reserve.

3. The patch changes this to increase OwnerCount by 2, with a comment tying the count to both Vault and PseudoAccount creation.

4. The resulting owner count is used for the accountReserve check, so the pseudo-account is included in reserve requirements.

5. VaultDelete::doApply previously erased the pseudo-account returned by keylet::account(pseudoID) without the new explicit validation shown in the patch.

6. The patched delete path loads vaultPseudoSLE and rejects bad ledger state if it is missing or its sfVaultID does not match the vault key.

7. The patched delete path checks the pseudo-account balance and returns tecHAS_OBLIGATIONS if a balance remains.

8. Deletion now decreases OwnerCount by -2, matching the two-object accounting used on creation.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/VaultCreate.cpp | 99 | removes the prior calculateBaseFee reserve-fee path so reserve enforcement is handled through owner count/account reserve accounting |
| src/xrpld/app/tx/detail/VaultCreate.cpp | 155 | increments owner count by two for the Vault object plus its pseudo-account and checks the resulting account reserve |
| src/xrpld/app/tx/detail/VaultDelete.cpp | 166 | loads and validates the vault pseudo-account before deletion, including vault linkage and empty balance handling |
| src/xrpld/app/tx/detail/VaultDelete.cpp | 218 | decrements owner count by two when destroying the Vault object and pseudo-account |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/VaultDelete.cpp:166` (changes persisted or aggregate state handling)

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

Context: `src/xrpld/app/tx/detail/VaultCreate.cpp:99` (changes aggregate state or economic accounting)

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

Context: `src/xrpld/app/tx/detail/VaultCreate.cpp:155` (changes an authorization or privilege gate)

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

Context: `src/xrpld/app/tx/detail/VaultDelete.cpp:218` (changes an authorization or privilege gate)

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

Make resource accounting match the actual number of persistent ledger objects, and validate dependent ledger objects before removing them.

## How It Was Fixed

VaultCreate::doApply now calls adjustOwnerCount(view(), owner, 2, j_) before checking accountReserve. VaultDelete::doApply validates the pseudo-account linkage and empty balance before removal, then calls adjustOwnerCount(view(), owner, -2, j_) when destroying the Vault and pseudo-account. The removed calculateBaseFee helper is observed in the diff, but the evidence does not fully establish the broader fee-path rationale beyond the reserve-accounting change.

# Why It Matters

1. Prevents Vault creation from being accounted as one owner-reserved object when the patch indicates two persistent objects are created.

2. Keeps create and delete owner-count accounting symmetric.

3. Reduces risk of under-reserved persistent ledger state.

4. Adds checks that deletion targets the matching empty pseudo-account.

5. Does not establish authorization bypass, theft, direct balance manipulation, or consensus divergence.

# Evidence Notes

Grounded evidence comes from src/xrpld/app/tx/detail/VaultCreate.cpp and src/xrpld/app/tx/detail/VaultDelete.cpp. The strongest changes are OwnerCount adjustment from 1 to 2 on create, OwnerCount adjustment from -1 to -2 on delete, and pseudo-account validation using keylet::account(pseudoID), sfVaultID, vault->key(), and sfBalance. The access-control framing in the heuristic baseline is unsupported. Test files were touched, but no detailed test hunks were provided, so specific regression coverage is not claimed. Confidence is medium rather than high because the patch establishes incorrect reserve accounting, but the supplied evidence does not demonstrate a practical exploit or concrete network-level impact. Protocol security invariant: Vault lifecycle accounting should charge and release owner reserve for each persistent ledger object created or destroyed. A Vault operation creates both a Vault object and an associated pseudo-account, so owner reserve accounting must reflect two objects, and deletion should only remove the matching empty pseudo-account. Verification notes: The patch does not prove an authorization bypass or missing privilege check. The patch does not prove direct theft, unauthorized withdrawal, or balance manipulation. The patch does not prove practical ledger spam or denial-of-service impact beyond under-accounted reserve state. The patch does not show consensus divergence by itself. The test changes are not provided in detail, so regression coverage specifics are not established. Verify VaultCreate requires reserve for both Vault and PseudoAccount after OwnerCount increases by 2. Verify VaultDelete releases reserve for both objects by decreasing OwnerCount by 2. Verify deletion fails if the pseudo-account is missing or linked to a different vault. Verify deletion fails with tecHAS_OBLIGATIONS if the pseudo-account balance remains. No supplied evidence proves an authorization bypass or direct asset loss. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-accounting`
Final impact type: `under-reserved-ledger-state`
Final tags: `blockchain-core, core-logic, vault, reserve-accounting, pseudo-account-validation, owner-count-accounting`

The supplied patch evidence supports a Vault reserve-accounting hardening finding, not the original access-control or privilege-misuse framing. Creation now accounts for both the Vault object and pseudo-account in owner reserve requirements, deletion releases both, and deletion adds checks that the pseudo-account exists, belongs to the vault, and has no balance. This tightens security-sensitive protocol resource accounting, but the evidence does not prove a concrete exploit, theft path, authorization bypass, or consensus failure.

## Security Evidence

1. VaultCreate changes OwnerCount adjustment from 1 to 2 before checking accountReserve, matching creation of both Vault and PseudoAccount.
2. VaultDelete changes OwnerCount adjustment from -1 to -2, making deletion accounting symmetric with creation.
3. VaultDelete now verifies the pseudo-account exists and has an sfVaultID matching the vault before deletion.
4. VaultDelete now rejects deletion when the pseudo-account still has a balance.

## Missing Evidence

1. No evidence shows an authorization bypass or privilege misuse.
2. No evidence demonstrates theft, unauthorized withdrawal, or direct asset loss.
3. No evidence proves practical ledger spam, denial of service, or consensus divergence.
4. Test hunks are listed but not provided, so specific regression assertions are not validated.

## Claim Boundaries

1. Keep the finding as security-hardening for protocol resource accounting, not as a confirmed security exploit.
2. Do not classify this as access-control based on the provided patch.
3. Do not claim privilege misuse or asset theft from this evidence.
4. The supported impact is under-reserved persistent ledger state and safer pseudo-account deletion validation.
