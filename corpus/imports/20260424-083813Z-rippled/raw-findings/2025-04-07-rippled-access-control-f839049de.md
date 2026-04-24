---
case_id: case_20250407_f839049de
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: access-control
source_quality: high
date: 2025-04-07
source_refs:
  - git:f839049de76b940a0d7b71f90cecc87ed8a35e47
  - "src/xrpld/ledger/detail/View.cpp:2272"
  - "src/xrpld/app/tx/detail/VaultCreate.cpp:111"
  - "src/xrpld/app/tx/detail/VaultDeposit.cpp:67"
  - "src/xrpld/app/tx/detail/VaultDeposit.cpp:94"
bug_class: authorization-recursion-boundary
impact_type:
  - authorization-hardening
  - availability-hardening
confidence: medium
tags:
  - blockchain-core
  - authorization
  - recursion-depth
  - vaults
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a correctness and possible hardening change in rippled vault asset handling: `requireAuth` changes its recursion guard from `depth > maxFreezeCheckDepth` to `depth >= maxFreezeCheckDepth`, `VaultCreate` checks MPT assets for excessive recursive vault-share authorization chains, and `VaultDeposit` adds or reorders asset identity, freeze, and authorization checks. The provided evidence does not establish a concrete vulnerability, exploit path, denial-of-service impact, or incorrect ledger-state impact, so this should not be treated as a confirmed security fix.

## Observed Patch Facts

1. In `src/xrpld/ledger/detail/View.cpp`, the patch replaces `if (depth > maxFreezeCheckDepth)` with `if (depth >= maxFreezeCheckDepth)`.

2. In `src/xrpld/app/tx/detail/VaultCreate.cpp`, the patch replaces `// Cannot create Vault for an Asset frozen for the vault owner` with `// Check for excessive vault shares recursion, which is reported by`.

3. In `src/xrpld/app/tx/detail/VaultDeposit.cpp`, the patch replaces `return tecFROZEN;` with `if (share == assets.asset())`.

4. In `src/xrpld/app/tx/detail/VaultDeposit.cpp`, the patch replaces `if (assets.holds<MPTIssue>())` with `if (auto const ter = std::visit(`.

## Project Context

The changed code sits primarily in `src/xrpld/ledger/detail`, `src/xrpld/ledger`, `src/xrpld/app/tx/detail`, which anchors the finding in the `access-control` area of the project. Historical context from `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, `src/xrpld/app/tx/detail/VaultClawback.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, `src/xrpld/app/tx/detail/VaultClawback.cpp`. The strongest project-level identifiers around this patch are `const`, `vault`, `asset`, and `auto`.

## Before/After Behavior

Before the patch, `requireAuth` allowed processing when `depth` was exactly `maxFreezeCheckDepth`; after the patch, that boundary returns `tecKILLED`. `VaultCreate::preclaim` changed from an owner frozen check to an MPT-specific `requireAuth(..., 1)` check that only returns on `tecKILLED`, based on the provided hunk. `VaultDeposit::preclaim` now derives the vault share earlier, rejects a defensive share/deposit asset identity case, preserves freeze handling, and applies `requireAuth` to `vaultAsset` through `std::visit`.

# Root Cause

The grounded root cause is an off-by-one recursion boundary in `requireAuth`, plus validation behavior in VaultCreate and VaultDeposit that was adjusted around vault asset authorization. The evidence does not prove that the prior behavior created an exploitable authorization bypass or other concrete security impact.

## Walkthrough

1. `requireAuth` follows vault-linked issuer state and can recurse into authorization checks for the vault asset.

2. The old guard used `depth > maxFreezeCheckDepth`, allowing one additional level at exactly the configured maximum.

3. The patch changes the guard to `depth >= maxFreezeCheckDepth` and returns `tecKILLED` at that boundary.

4. `VaultCreate::preclaim` now calls `requireAuth(ctx.view, mptIssue, account, 1)` for MPT assets and only propagates `tecKILLED`, matching the comment that this path is for excessive recursion detection.

5. `VaultDeposit::preclaim` now computes the vault share MPT ID earlier and rejects a defensive case where the share equals the deposited asset.

6. `VaultDeposit::preclaim` applies freeze checking and then routes the actual `vaultAsset` through `requireAuth`, returning non-success results.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/ledger/detail/View.cpp | 2272 | enforces recursive requireAuth depth limit for vault-linked MPT issuers |
| src/xrpld/app/tx/detail/VaultCreate.cpp | 111 | checks MPT vault asset creation path for excessive recursive vault-share authorization chains |
| src/xrpld/app/tx/detail/VaultDeposit.cpp | 67 | validates deposited asset identity and prevents vault share asset self-reference |
| src/xrpld/app/tx/detail/VaultDeposit.cpp | 94 | applies requireAuth to the vault asset before deposit acceptance |

## Code Snippets

## Snippet 1

Context: `src/xrpld/ledger/detail/View.cpp:2272` (changes a sensitive control or state-update path)

Before
```cpp
return tefINTERNAL;  // LCOV_EXCL_LINE

            if (depth > maxFreezeCheckDepth)
                return tecKILLED;  // TODO: consider different code

            auto const asset = sleVault->at(sfAsset);
```
After
```cpp
return tefINTERNAL;  // LCOV_EXCL_LINE

            if (depth >= maxFreezeCheckDepth)
                return tecKILLED;  // VaultCreate looks for this error code

            auto const asset = sleVault->at(sfAsset);
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/VaultCreate.cpp:111` (changes a sensitive control or state-update path)

Before
```cpp
}

    // Cannot create Vault for an Asset frozen for the vault owner
    if (isFrozen(ctx.view, account, asset))
```
After
```cpp
}

    // Check for excessive vault shares recursion, which is reported by
    // requireAuth as tecKILLED. The vault owner might not be permissioned to
    // hold assets but that's OK, it only means that the owner won't be able to
    // withdraw from or deposit into the vault (but other users would be fine).
    if (asset.holds<MPTIssue>())
    {
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/VaultDeposit.cpp:67` (changes a sensitive control or state-update path)

Before
```cpp
return tecWRONG_ASSET;

    // Cannot deposit inside Vault an Asset frozen for the depositor
    if (isFrozen(ctx.view, account, vaultAsset))
        return tecFROZEN;

    auto const share = MPTIssue(vault->at(sfShareMPTID));
    // Cannot deposit if the shares of the vault are frozen
```
After
```cpp
return tecWRONG_ASSET;

    auto const share = MPTIssue(vault->at(sfShareMPTID));
    if (share == assets.asset())
        return tefINTERNAL;

    // Cannot deposit inside Vault an Asset frozen for the depositor
    if (isFrozen(ctx.view, account, vaultAsset))
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/VaultDeposit.cpp:94` (changes a sensitive control or state-update path)

Before
```cpp
}

    if (assets.holds<MPTIssue>())
    {
```
After
```cpp
}

    if (auto const ter = std::visit(
            [&]<ValidIssueType TIss>(TIss const& issue) -> TER {
                return requireAuth(ctx.view, issue, account);
            },
            vaultAsset.value());
        !isTesSuccess(ter))
```

# Fix Pattern

Tighten a recursive boundary check and align vault create/deposit validation with existing authorization helpers, while keeping documented business-rule exceptions narrow.

## How It Was Fixed

`View.cpp` changed the recursion-depth comparison from `>` to `>=`. `VaultCreate.cpp` added an MPT-only `requireAuth` recursion check that returns `tecKILLED` for excessive recursion. `VaultDeposit.cpp` reordered share derivation, added a defensive identity check, and added `std::visit`-based `requireAuth` validation for the vault asset.

# Why It Matters

1. Prevents one extra recursive authorization step at the configured depth boundary.

2. Makes excessive recursive vault-share chains explicitly detectable by VaultCreate.

3. Applies authorization handling to the vault asset in VaultDeposit.

4. Security relevance is plausible, but concrete vulnerability impact is not shown.

# Evidence Notes

The strongest evidence is the direct `requireAuth` off-by-one change and the added VaultCreate/VaultDeposit validation hunks. Claims of an externally exploitable bypass, denial of service, privilege escalation, or incorrect ledger state are not supported by the provided input. Related VaultWithdraw and VaultClawback files are only contextual and should not be treated as affected root-cause paths. Protocol security invariant: Vault create and deposit validation should avoid unbounded recursive authorization traversal through vault-backed MPT assets and should apply the relevant freeze/authorization checks to the vault asset being used. Verification notes: The patch does not prove an externally exploitable bypass. The evidence does not show whether exceeding the old recursion boundary caused denial of service, incorrect ledger state, or only incorrect return codes. The VaultCreate change is not simply a stricter freeze check; it intentionally allows owner non-permissioning except for excessive recursion detection. No claim is made about VaultWithdraw or VaultClawback behavior beyond surrounding subsystem context. No exploit scenario is provided. No failing regression test details are provided in the input. The commit message says this fixes an off-by-one error, but does not establish security impact. Classify as unclear rather than confirmed or likely security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `authorization-recursion-boundary`
Final impact type: `authorization-hardening, availability-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, authorization, recursion-depth, vaults, hardening`

The evidence does not prove a concrete exploitable vulnerability, so this should not be retained as a confirmed security fix. However, the patch clearly tightens security-sensitive vault authorization and freeze-related behavior: it corrects a recursion-depth boundary in requireAuth, adds explicit excessive-recursion detection in VaultCreate, and applies requireAuth to VaultDeposit's vault asset. That is enough to classify conservatively as security-hardening rather than not-security.

## Security Evidence

1. requireAuth recursion guard changed from depth > maxFreezeCheckDepth to depth >= maxFreezeCheckDepth.
2. VaultCreate now checks MPT assets through requireAuth specifically to detect excessive vault-share recursion returning tecKILLED.
3. VaultDeposit now runs requireAuth over the vault asset and returns non-success authorization results.
4. Changed paths are transaction preclaim and ledger authorization/freeze helpers in blockchain core vault handling.

## Missing Evidence

1. No exploit scenario is shown.
2. No proof that the old off-by-one caused denial of service, authorization bypass, or incorrect ledger acceptance.
3. No regression test details are supplied showing a security invariant violation.
4. VaultCreate behavior also relaxes owner permissioning in one respect, so the exact user-visible security impact is not fully established.

## Claim Boundaries

1. Do not claim a confirmed privilege escalation or authorization bypass.
2. Do not claim a concrete denial-of-service vulnerability from the patch alone.
3. Treat this as hardening of recursive authorization/freeze validation, not a proven vulnerability fix.
4. Limit affected paths to VaultCreate, VaultDeposit, and requireAuth recursion behavior shown in the evidence.
