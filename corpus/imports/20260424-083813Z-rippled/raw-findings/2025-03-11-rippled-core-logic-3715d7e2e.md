---
case_id: case_20250311_3715d7e2e
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
bug_class: access-control
impact_type:
  - privilege-misuse
confidence: medium
source_quality: high
tags:
  - blockchain-core
  - core-logic
  - access-control
  - privilege-misuse
date: 2025-03-11
source_refs:
  - git:3715d7e2e49f24d1aa7222f62df7cfb27ad2b5b2
  - "src/xrpld/app/tx/detail/VaultSet.cpp:96"
  - "src/xrpld/ledger/detail/View.cpp:2345"
  - "src/xrpld/app/tx/detail/VaultDeposit.cpp:120"
  - "src/xrpld/app/tx/detail/VaultDeposit.cpp:132"
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch likely fixes access-control bugs in vault deposit and shared MPToken authorization logic. The strongest grounded evidence is that private-vault detection changed from exact flag equality to a bitwise private-flag check, and enforceMPTokenAuthorization now rejects tokens that lack lsfMPTAuthorized. The evidence supports a likely security fix, but not a confirmed exploit chain or claims such as asset theft, unauthorized withdrawal, or consensus failure.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/VaultSet.cpp`, the patch replaces `if (tx.isFieldPresent(sfData))` with `auto const mptIssuanceID = (*vault)[sfMPTokenIssuanceID];`.

2. In `src/xrpld/ledger/detail/View.cpp`, the patch replaces `if (!sleToken)` with `if (sleToken == nullptr || (sleToken->getFlags() & lsfMPTAuthorized) == 0)`.

3. In `src/xrpld/app/tx/detail/VaultDeposit.cpp`, the patch replaces `if (vault->getFlags() == tfVaultPrivate)` with `// Note, vault owner is always authorized`.

4. In `src/xrpld/app/tx/detail/VaultDeposit.cpp`, the patch replaces `if (!sleMpt && account_ != vaultAccount)` with `if (!sleMpt)`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, `src/xrpld/ledger/detail`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, `src/xrpld/app/tx/detail/VaultClawback.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, `src/xrpld/app/tx/detail/VaultClawback.cpp`. The strongest project-level identifiers around this patch are `auto`, `const`, `vault`, and `mptIssuanceID`.

## Before/After Behavior

Before the patch, VaultDeposit checked `vault->getFlags() == tfVaultPrivate`, so private-vault handling could be skipped if other flags were also set. After the patch, it checks `(vault->getFlags() & tfVaultPrivate)` and exempts the vault owner from that authorization branch. Before the patch, enforceMPTokenAuthorization rejected missing tokens but only checked lsfMPTAuthorized when lsfMPTRequireAuth was set on the issuance. After the patch, it rejects both missing tokens and tokens without lsfMPTAuthorized. Before the patch, one no-authorization-needed deposit branch skipped MPToken creation/presence handling for `account_ == vaultAccount`; after the patch, it handles any missing MPToken. VaultSet now loads the associated MPToken issuance before mutable updates, but the provided excerpt does not prove the downstream permission check.

# Root Cause

Authorization-related state checks were inconsistent: private-vault status was tested by exact flag equality rather than by the private flag bit, and the shared MPToken authorization helper could accept an existing token without unconditionally requiring lsfMPTAuthorized. The MPToken presence change appears related, but the security impact of that specific branch is less clearly established by the provided evidence.

## Walkthrough

1. VaultDeposit reads the vault and associated MPToken issuance before applying deposit authorization logic.

2. Old code entered private-vault authorization only when the vault flags exactly equaled tfVaultPrivate.

3. If additional flags were present, the exact comparison could fail even though the private flag was set.

4. Patched code tests the private flag bit and only skips that private-vault authorization branch for the vault owner.

5. The shared authorization helper now returns tecNO_AUTH when the MPToken is missing or lacks lsfMPTAuthorized.

6. A deposit branch that does not require an authorization challenge now still ensures MPToken state exists for all accounts.

7. VaultSet now fetches the associated issuance before mutable updates, but the excerpt only supports treating this as related context, not as the proven root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/VaultDeposit.cpp | 120 | Applies private vault deposit authorization; changed from exact tfVaultPrivate flag comparison to bitwise private-flag enforcement with owner exemption. |
| src/xrpld/app/tx/detail/VaultDeposit.cpp | 132 | Ensures an MPToken is present even on the no-authorization-needed branch, including previously exempt account cases. |
| src/xrpld/ledger/detail/View.cpp | 2345 | Shared MPToken authorization helper; now rejects missing tokens and tokens lacking lsfMPTAuthorized. |
| src/xrpld/app/tx/detail/VaultSet.cpp | 96 | Vault mutation path now loads the associated MPToken issuance before applying mutable field updates. |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/VaultSet.cpp:96` (changes a sensitive control or state-update path)

Before
```cpp
return tecOBJECT_NOT_FOUND;

    // Update mutable flags and fields if given.
    if (tx.isFieldPresent(sfData))
```
After
```cpp
return tecOBJECT_NOT_FOUND;

    auto const mptIssuanceID = (*vault)[sfMPTokenIssuanceID];
    auto const sleIssuance = view().peek(keylet::mptIssuance(mptIssuanceID));
    if (!sleIssuance)
        return tefINTERNAL;

    // Update mutable flags and fields if given.
```

## Snippet 2

Context: `src/xrpld/ledger/detail/View.cpp:2345` (changes a sensitive control or state-update path)

Before
```cpp
}

    if (!sleToken)
        return tecNO_AUTH;

    if (sleIssuance->getFieldU32(sfFlags) & lsfMPTRequireAuth &&
        !(sleToken->getFlags() & lsfMPTAuthorized))
        return tecNO_AUTH;
```
After
```cpp
}

    if (sleToken == nullptr || (sleToken->getFlags() & lsfMPTAuthorized) == 0)
        return tecNO_AUTH;
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/VaultDeposit.cpp:120` (changes a sensitive control or state-update path)

Before
```cpp
MPTIssue const mptIssue(mptIssuanceID);
    if (vault->getFlags() == tfVaultPrivate)
    {
        if (auto const err = enforceMPTokenAuthorization(
```
After
```cpp
MPTIssue const mptIssue(mptIssuanceID);
    // Note, vault owner is always authorized
    if (account_ != vault->at(sfOwner) && (vault->getFlags() & tfVaultPrivate))
    {
        if (auto const err = enforceMPTokenAuthorization(
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/VaultDeposit.cpp:132` (changes a sensitive control or state-update path)

Before
```cpp
// No authorization needed, but must ensure there is MPToken
        auto sleMpt = view().read(keylet::mptoken(mptIssuanceID, account_));
        if (!sleMpt && account_ != vaultAccount)
        {
            if (auto const err = MPTokenAuthorize::authorize(
```
After
```cpp
// No authorization needed, but must ensure there is MPToken
        auto sleMpt = view().read(keylet::mptoken(mptIssuanceID, account_));
        if (!sleMpt)
        {
            if (auto const err = MPTokenAuthorize::authorize(
```

# Fix Pattern

Replace exact flag comparisons with bitwise flag checks, make the shared authorization helper enforce the authorized-token bit consistently, and ensure required MPToken state is present on related deposit paths.

## How It Was Fixed

VaultDeposit changed the private-vault gate to `(vault->getFlags() & tfVaultPrivate)` and added an explicit owner exemption. The no-authorization-needed branch now handles missing MPToken state without excluding the vault account. enforceMPTokenAuthorization now rejects both null tokens and tokens missing lsfMPTAuthorized. VaultSet now loads the vault's MPToken issuance before mutable updates and fails if it is absent.

# Why It Matters

1. Private-vault authorization should not depend on the full flags value matching exactly.

2. An existing MPToken should not imply authorization unless the authorized bit is set.

3. Related exempt paths still need required token state to remain consistent.

4. The evidence supports likely access-control relevance, but not a specific exploit outcome.

# Evidence Notes

Primary evidence is in VaultDeposit.cpp line 120, VaultDeposit.cpp line 132, and View.cpp line 2345. VaultSet.cpp line 96 is supporting evidence only because the provided excerpt does not show the permission-domain check that uses the loaded issuance. The commit subject mentions permission-domain bug fixes, but the assessment does not rely on unstated exploitability. Protocol security invariant: Vault operations that depend on private-vault or MPToken authorization state must test the relevant flag bits and must not treat a merely existing MPToken as authorized unless it carries lsfMPTAuthorized. Verification notes: The patch evidence does not prove a complete exploit chain or remote exploitability. The patch does not by itself prove asset theft, unauthorized withdrawal, or consensus failure. The visible VaultSet excerpt does not show the exact permission-domain check that uses the loaded issuance. The evidence supports an access-control fix, but not the full severity or attacker preconditions. No external advisory, issue discussion, or full exploit path is provided. Tests were changed, but their assertions are not included in the provided evidence. Keep as likely security-fix with medium confidence, not confirmed. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`

The supplied patch evidence supports retaining this as a likely security fix. The strongest evidence is in authorization-sensitive vault and MPToken paths: private vault handling changed from exact flag equality to a bitwise private-flag check, and the shared MPToken authorization helper now rejects tokens that exist but lack the authorized flag. These are concrete access-control tightening changes in transaction/ledger logic. The evidence does not prove a complete exploit chain or specific loss scenario, so the original medium-confidence framing is appropriately conservative.

## Security Evidence

1. VaultDeposit now checks the private-vault flag with a bitwise test instead of exact equality, preventing private handling from being skipped when other flags are set.
2. VaultDeposit explicitly applies the private-vault authorization path to non-owner accounts while exempting the vault owner.
3. enforceMPTokenAuthorization now rejects both missing MPToken records and records lacking lsfMPTAuthorized.
4. The changed code is in core transaction and ledger authorization paths, not only tests or cleanup.

## Missing Evidence

1. No advisory, issue discussion, or exploit report is provided.
2. Tests are mentioned but their assertions are not included in the supplied evidence.
3. The VaultSet excerpt does not show the downstream permission-domain check that uses the newly loaded issuance.
4. No concrete attacker preconditions or demonstrated asset impact are shown.

## Claim Boundaries

1. Keep the finding as an access-control authorization fix, not as confirmed asset theft or consensus failure.
2. Do not claim remote exploitability from the provided patch alone.
3. Treat VaultSet as supporting context unless additional evidence shows the permission-domain behavior it fixes.
4. Confidence should remain medium rather than high because the exploit path is inferred from code changes.
