---
case_id: case_20250430_ceeb11aee
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: access-control
source_quality: medium
date: 2025-04-30
source_refs:
  - git:ceeb11aee04d5126d5bf9effcfa749f7301de2fa
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:474"
bug_class: ledger-state-invariant-hardening
impact_type:
  - ledger-state-integrity
confidence: medium
tags:
  - blockchain-core
  - ledger-invariant
  - state-consistency
  - account-deletion
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch strengthens an AccountRoot deletion invariant in rippled by adding a check that a deleted account must not have a non-zero owner count. The evidence supports ledger-state invariant hardening, but it does not establish an exploitable vulnerability, consensus failure, authorization bypass, fund loss, or denial-of-service impact.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `"account deletion left behind a non-zero balance");` with `"deleted account has zero balance");`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, which anchors the finding in the `access-control` area of the project. Historical context from `src/xrpld/app/tx/detail/DeleteAccount.cpp`, `src/xrpld/app/tx/detail/VaultWithdraw.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, `src/xrpld/app/tx/detail/VaultDeposit.cpp`. The strongest project-level identifiers around this patch are `account`, `zero`, `ripple::AccountRootsDeletedClean::finalize`, and `enforce`.

## Before/After Behavior

Before the patch, AccountRootsDeletedClean::finalize checked that a deleted AccountRoot did not retain a non-zero sfBalance. After the patch, that balance check remains and a new check rejects or asserts when the deleted AccountRoot has sfOwnerCount != 0, depending on enforcement mode.

# Root Cause

The prior invariant did not explicitly check sfOwnerCount when validating deleted AccountRoot cleanliness. The supplied evidence does not prove that normal transaction processing could actually delete an account with a non-zero owner count.

## Walkthrough

1. The changed implementation is in src/xrpld/app/tx/detail/InvariantCheck.cpp inside AccountRootsDeletedClean::finalize.

2. The existing code checked deleted account balance against beast::zero.

3. The patch adjusts the assertion text for the balance check.

4. The patch adds a new comment stating that an account should not be deleted with a non-zero owner count.

5. The new code checks after->at(sfOwnerCount) != 0.

6. If the owner count is non-zero, the invariant logs a fatal message, asserts through XRPL_ASSERT, and returns false when enforce is enabled.

7. No supplied evidence shows a changed authorization path, transaction admission rule, or concrete exploit scenario.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 468 | AccountRootsDeletedClean invariant checks deleted AccountRoot balance after a transaction |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 474 | new invariant check rejects deleted accounts with non-zero sfOwnerCount |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:474` (changes an authorization or privilege gate)

Before
```cpp
enforce,
                "ripple::AccountRootsDeletedClean::finalize : "
                "account deletion left behind a non-zero balance");
            if (enforce)
                return false;
```
After
```cpp
enforce,
                "ripple::AccountRootsDeletedClean::finalize : "
                "deleted account has zero balance");
            if (enforce)
                return false;
        }
        // An account should not be deleted with a non-zero owner count
        if (after->at(sfOwnerCount) != 0)
```

# Fix Pattern

Extend an existing ledger invariant with an additional field-level consistency check for deleted AccountRoot state.

## How It Was Fixed

The implementation adds an sfOwnerCount validation to AccountRootsDeletedClean::finalize using the same enforcement style as the existing deleted-account balance check: fatal logging, XRPL_ASSERT tied to enforce, and returning false when enforcement is active. The file list also indicates tests were updated, but the supplied evidence does not include the test diff.

# Why It Matters

1. Improves detection of inconsistent deleted AccountRoot state.

2. Keeps deleted-account cleanup checks aligned with owner-count accounting.

3. Security impact is not established by the provided evidence.

# Evidence Notes

The access-control framing in the heuristic baseline is unsupported and should be rejected. The supplied hunk only shows a ledger invariant check being extended. Related Vault and DeleteAccount snippets are contextual and do not show changed behavior. Claims about orphaned objects, exploitability, consensus failure, or authorization bypass are not proven by the provided input. Protocol security invariant: A deleted AccountRoot should have zero balance and zero sfOwnerCount. The patch extends AccountRootsDeletedClean::finalize to check sfOwnerCount == 0 for deleted accounts. Verification notes: No access-control or privilege-check fix is shown by the patch evidence. No concrete exploit path is proven. No proof is shown that DeleteAccount itself previously allowed this state transition. No denial-of-service, fund theft, or consensus failure impact is established beyond ledger invariant hardening. Related vault files are traced context only and are not shown as part of the changed behavior. Confirmed from supplied diff that sfOwnerCount check was added to AccountRootsDeletedClean::finalize. Confirmed no provided evidence of an access-control change. Confirmed no provided evidence of a concrete attack path or vulnerability impact. Test changes are listed in commit metadata but not available in the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `ledger-state-invariant-hardening`
Final impact type: `ledger-state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, ledger-invariant, state-consistency, account-deletion`

The supplied patch clearly strengthens a ledger-state invariant for deleted AccountRoot entries by rejecting deletion when sfOwnerCount is non-zero. In a blockchain core transaction/invariant path, this is security-relevant hardening of ledger integrity, but the evidence does not prove a concrete exploitable vulnerability, authorization bypass, fund loss, or consensus failure. The original access-control and privilege-misuse framing is too strong and should be replaced with ledger invariant hardening.

## Security Evidence

1. Patch adds an sfOwnerCount != 0 check to AccountRootsDeletedClean::finalize for deleted accounts.
2. The new check follows existing invariant enforcement behavior with fatal logging, XRPL_ASSERT, and false return when enforce is enabled.
3. The changed code is in a blockchain ledger transaction invariant path, a security-sensitive state-integrity boundary.
4. Commit subject explicitly targets preventing account deletion with a non-zero owner count.

## Missing Evidence

1. No supplied evidence shows normal transaction processing could previously delete such an account.
2. No concrete exploit path, attacker-controlled trigger, fund loss, or denial-of-service impact is shown.
3. No proof is provided that this changes authorization, privilege checks, or transaction admission rules.
4. Test diff is mentioned in metadata but not included in the supplied evidence.

## Claim Boundaries

1. Validate only as security hardening, not a confirmed vulnerability fix.
2. Do not classify as access-control or privilege misuse from the supplied patch.
3. Do not claim consensus failure, asset theft, or denial of service without additional evidence.
4. The supported claim is limited to added ledger-state invariant enforcement for deleted AccountRoot owner counts.
