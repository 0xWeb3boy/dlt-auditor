---
case_id: case_20250414_d6d07e6fc
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
confidence: medium
source_quality: high
date: 2025-04-14
source_refs:
  - git:d6d07e6fcf969de0af02e45c90e244ed6ed546c0
  - "src/xrpld/app/tx/detail/VaultDeposit.cpp:175"
  - "src/xrpld/app/tx/detail/VaultDeposit.cpp:86"
  - "src/xrpld/ledger/detail/View.cpp:2276"
  - "src/xrpld/app/tx/detail/VaultDeposit.cpp:67"
bug_class: authorization-correctness
impact_type:
  - authorization-enforcement
tags:
  - blockchain-core
  - vault
  - authorization
  - private-vault
  - mptoken
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely access-control fix in rippled vault deposit authorization. The patch changes VaultDeposit private-vault handling to read the share MPTokenIssuance, use its DomainID metadata for authorization decisions, and add an apply-time MPTokenAuthorize call for private vault shares. The evidence supports an authorization correctness fix, but does not show a complete exploit path or exact before-patch transaction outcome.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/VaultDeposit.cpp`, the patch adds `// If the vault is private, set the authorized flag for the vault owner`.

2. In `src/xrpld/app/tx/detail/VaultDeposit.cpp`, the patch replaces `// The authorization check below is based on DomainID stored in` with `auto const maybeDomainID = sleIssuance->at(~sfDomainID);`.

3. In `src/xrpld/ledger/detail/View.cpp`, the patch replaces `return std::visit(` with `if (auto const err = std::visit(`.

4. In `src/xrpld/app/tx/detail/VaultDeposit.cpp`, the patch replaces `auto const share = MPTIssue(vault->at(sfShareMPTID));` with `auto const mptIssuanceID = vault->at(sfShareMPTID);`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, `src/xrpld/ledger/detail`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, `src/xrpld/app/tx/detail/VaultSet.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/applySteps.cpp`, `src/xrpld/app/tx/detail/VaultWithdraw.cpp`. The strongest project-level identifiers around this patch are `const`, `vault`, `auto`, and `account`.

## Before/After Behavior

Before the patch, VaultDeposit::preclaim constructed the share directly from sfShareMPTID and the private-vault non-owner path visibly called requireAuth(ctx.view, share, account). After the patch, preclaim stores the share issuance ID, reads the corresponding MPTokenIssuance ledger entry, and reads DomainID from that issuance in the private-vault non-owner branch. Before the patch, the supplied VaultDeposit::doApply snippet did not show private-vault owner share authorization. After the patch, doApply adds a private-vault branch calling MPTokenAuthorize::authorize for the share issuance. View.cpp also changes vault-backed asset requireAuth handling from an immediate recursive return to an intermediate error check, but the provided excerpt does not fully show the resulting control flow.

# Root Cause

The private vault deposit authorization path appears to have had incomplete or inconsistent handling of vault share MPTokenIssuance authorization metadata and authorized-holder state. The evidence indicates that using the generic share requireAuth path was not sufficient for private vault shares because vault shares use a pseudo-account issuer rather than a normal issuer that can grant authorization.

## Walkthrough

1. VaultDeposit::preclaim now extracts mptIssuanceID from sfShareMPTID and constructs the share issue from that ID.

2. The patched preclaim reads the MPTokenIssuance ledger object for the share and treats a missing issuance as an internal error.

3. For private vaults where the account is not the owner, the patched code reads DomainID from the share issuance before continuing authorization handling.

4. The surrounding comments state that vault shares cannot rely on normal issuer-granted authorization because the vault uses a pseudo-account issuer.

5. VaultDeposit::doApply adds a private-vault MPTokenAuthorize::authorize call for the share issuance holder state.

6. View.cpp changes nested vault asset requireAuth handling to inspect the recursive authorization result instead of immediately returning it, though the excerpt does not establish the full behavioral effect.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/VaultDeposit.cpp | 67 | VaultDeposit preclaim reads the vault share MPTokenIssuance so private-vault authorization can use issuance metadata such as DomainID. |
| src/xrpld/app/tx/detail/VaultDeposit.cpp | 86 | VaultDeposit preclaim applies private vault authorization logic for non-owner depositors. |
| src/xrpld/app/tx/detail/VaultDeposit.cpp | 175 | VaultDeposit doApply authorizes the vault owner to hold private vault shares during deposit processing. |
| src/xrpld/ledger/detail/View.cpp | 2276 | Shared requireAuth handling for vault-backed assets propagates authorization checks through nested vault assets. |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/VaultDeposit.cpp:175` (changes an authorization or privilege gate)

Before
```cpp
return err;
        }
    }
```
After
```cpp
return err;
        }

        // If the vault is private, set the authorized flag for the vault owner
        if (vault->getFlags() & tfVaultPrivate)
        {
            if (auto const err = MPTokenAuthorize::authorize(
                    view(),
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/VaultDeposit.cpp:86` (changes a sensitive control or state-update path)

Before
```cpp
if ((vault->getFlags() & tfVaultPrivate) && account != vault->at(sfOwner))
    {
        // The authorization check below is based on DomainID stored in
        // MPTokenIssuance. Had the vault shares been a regular MPToken, we
        // would allow authorization granted by the issuer explicitly, but Vault
        // does not have an MPT issuer (instead it uses pseudo-account, which is
        // blackholed and cannot create any transactions).
        //
```
After
```cpp
if ((vault->getFlags() & tfVaultPrivate) && account != vault->at(sfOwner))
    {
        auto const maybeDomainID = sleIssuance->at(~sfDomainID);
        // Since this is a private vault and the account is not its owner, we
        // perform authorization check based on DomainID read from sleIssuance.
        // Had the vault shares been a regular MPToken, we would allow
        // authorization granted by the Issuer explicitly, but Vault uses Issuer
        // pseudo-account, which cannot grant an authorization.
```

## Snippet 3

Context: `src/xrpld/ledger/detail/View.cpp:2276` (changes a sensitive control or state-update path)

Before
```cpp
auto const asset = sleVault->at(sfAsset);
            return std::visit(
                [&]<ValidIssueType TIss>(TIss const& issue) {
                    if constexpr (std::is_same_v<TIss, Issue>)
                        return requireAuth(view, issue, account);
                    else
                        return requireAuth(view, issue, account, depth + 1);
```
After
```cpp
auto const asset = sleVault->at(sfAsset);
            if (auto const err = std::visit(
                    [&]<ValidIssueType TIss>(TIss const& issue) {
                        if constexpr (std::is_same_v<TIss, Issue>)
                            return requireAuth(view, issue, account);
                        else
                            return requireAuth(view, issue, account, depth + 1);
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/VaultDeposit.cpp:67` (changes a sensitive control or state-update path)

Before
```cpp
return tecWRONG_ASSET;

    auto const share = MPTIssue(vault->at(sfShareMPTID));
    if (share == assets.asset())
        return tefINTERNAL;

    // Cannot deposit inside Vault an Asset frozen for the depositor
    if (isFrozen(ctx.view, account, vaultAsset))
```
After
```cpp
return tecWRONG_ASSET;

    auto const mptIssuanceID = vault->at(sfShareMPTID);
    auto const share = MPTIssue(mptIssuanceID);
    if (share == assets.asset())
        return tefINTERNAL;

    auto const sleIssuance = ctx.view.read(keylet::mptIssuance(mptIssuanceID));
```

# Fix Pattern

Anchor private-vault share authorization to the share MPTokenIssuance ledger entry and explicitly create required MPToken authorization state during deposit application.

## How It Was Fixed

The patch reads the vault share issuance ID into a named variable, loads the corresponding MPTokenIssuance object, uses issuance DomainID metadata in the private-vault authorization path, and adds an MPTokenAuthorize::authorize call in VaultDeposit::doApply for private vault share holder authorization. It also adjusts shared requireAuth handling for vault-backed assets to use an intermediate authorization result check.

# Why It Matters

1. Private vault share access depends on correct authorization checks.

2. Vault share pseudo-account issuers cannot grant authorization like normal MPToken issuers.

3. Incorrect holder authorization can break private-vault access control.

4. The evidence does not support claims of theft, fund loss, consensus failure, or code execution.

# Evidence Notes

The strongest evidence is the commit subject "Fix authorization issues" plus implementation changes in VaultDeposit.cpp that alter private-vault authorization handling and add MPTokenAuthorize::authorize. The supplied snippets do not include the full regression tests, the complete new private-vault authorization branch, or a concrete exploit scenario. The View.cpp change is plausibly related support code, but the excerpt alone does not prove the exact security impact of that hunk. Protocol security invariant: Private vault share authorization must be enforced consistently from the vault share MPTokenIssuance metadata, and private-vault share holder authorization must be established for accounts that are allowed to hold the shares. Vault share authorization cannot be treated exactly like normal issuer-granted MPToken authorization when the issuer is a pseudo-account. Verification notes: The evidence does not prove that an unauthorized deposit could be completed before the patch in all configurations. The evidence does not prove theft, fund withdrawal, consensus failure, or remote code execution. The evidence does not show the full regression tests or exact user-visible failure mode. The evidence supports an authorization correctness fix, not a broader claim about all vault operations. Confidence is downgraded from high to medium because the full authorization branch and tests are not shown. Security verdict is likely rather than confirmed because the evidence shows an authorization fix but not a demonstrated vulnerability trigger. Keep in corpus because the patch directly changes access-control behavior in a sensitive vault deposit path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `authorization-correctness`
Final impact type: `authorization-enforcement`
Final tags: `blockchain-core, vault, authorization, private-vault, mptoken`

The supplied evidence supports retaining this as security hardening: the patch directly changes private vault authorization behavior in deposit processing, reads MPTokenIssuance metadata for authorization decisions, and explicitly authorizes the vault owner to hold private vault shares. However, the excerpts do not prove a concrete exploitable bypass, unauthorized transaction outcome, or asset-loss scenario, so classifying it as a confirmed security-fix would be too strong.

## Security Evidence

1. Commit subject is "Fix authorization issues".
2. VaultDeposit private-vault path now reads share MPTokenIssuance and DomainID metadata before authorization handling.
3. VaultDeposit::doApply adds an MPTokenAuthorize::authorize call for private vault shares.
4. Comments explain that vault shares use a pseudo-account issuer and cannot rely on normal issuer-granted authorization.
5. Changes occur in core transaction and ledger authorization paths.

## Missing Evidence

1. No complete before/after authorization branch is shown.
2. No regression test details are provided in the evidence.
3. No concrete exploit path or unauthorized deposit scenario is demonstrated.
4. No proof of theft, fund loss, consensus failure, or privilege escalation beyond authorization correctness.

## Claim Boundaries

1. Treat as authorization hardening/correctness for private vault deposits, not a proven exploit fix.
2. Do not claim asset theft or direct fund loss from the supplied patch alone.
3. Do not generalize beyond vault share authorization and related requireAuth behavior.
4. The View.cpp hunk is plausibly related but its full behavioral effect is not established by the excerpt.
