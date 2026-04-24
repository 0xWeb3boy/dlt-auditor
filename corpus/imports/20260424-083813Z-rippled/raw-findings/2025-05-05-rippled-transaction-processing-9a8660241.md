---
case_id: case_20250505_9a8660241
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2025-05-05
source_refs:
  - git:9a866024175b813d9033b061b28fb4324647b61d
  - "src/xrpld/app/tx/detail/LoanSet.cpp:340"
  - "src/xrpld/app/tx/detail/LoanManage.cpp:304"
  - "src/xrpld/app/tx/detail/LoanManage.cpp:226"
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:1999"
bug_class: ledger-accounting-invariant-hardening
impact_type:
  - ledger-integrity
  - state-consistency
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - loan-vault-accounting
  - invariant-check
  - underflow-guard
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports an accounting correctness and invariant-hardening change in rippled's lending loan/vault transaction path. The patch replaces inline interest allocation math with a shared helper, adds checks before reducing vault accounting fields, and adds invariant checks for negative loan balances. The evidence does not prove an external trigger, exploit path, fund loss, authorization bypass, consensus failure, or crash, so this should not be kept as a confirmed security fix.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/LoanSet.cpp`, the patch replaces `// The total amount if interest the loan is expected to generate` with `auto const loanInterestToVault = LoanInterestOutstanding(`.

2. In `src/xrpld/app/tx/detail/LoanManage.cpp`, the patch replaces `vaultSle->at(sfLossUnrealized) -=` with `auto vaultLossUnrealizedProxy = vaultSle->at(sfLossUnrealized);`.

3. In `src/xrpld/app/tx/detail/LoanManage.cpp`, the patch replaces `// Move the First-Loss Capital from the LoanBroker pseudo-account to the` with `// Update the Vault object:`.

4. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `return true;` with `if (after->at(sfAssetsAvailable) < 0)`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, `src/xrpld/app/tx/detail/VaultSet.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/LoanDelete.cpp`, `src/xrpld/app/tx/detail/VaultWithdraw.cpp`. The strongest project-level identifiers around this patch are `auto`, `const`, `Vault`, and `vaultSle`.

## Before/After Behavior

Before the patch, `LoanSet::doApply()` computed vault interest allocation inline from total interest minus the management fee. After the patch, it calls `LoanInterestOutstanding(vaultAsset, principalRequested, interestRate, managementFeeRate)`. Before the patch, `unimpairLoan()` directly subtracted `principalOutstanding + interestOutstanding` from `sfLossUnrealized`; after the patch, it checks for insufficient current loss and returns `tefBAD_LEDGER`. Before the patch, the shown `defaultLoan()` path did not show a guard before reducing vault assets; after the patch, it checks `sfAssetsTotal < vaultDefaultAmount` and returns `tefBAD_LEDGER`. `ValidLoan::finalize()` also adds checks that `sfAssetsAvailable` and `sfPrincipalOutstanding` are not negative.

# Root Cause

The snippets indicate loan/vault accounting code used inline calculations and direct ledger-field decrements without the newly added shared calculation and sufficient-value checks. However, the provided evidence does not prove that these states were externally reachable or security exploitable.

## Walkthrough

1. `LoanSet::doApply()` previously derived the vault interest share with local arithmetic.

2. The patched code uses `LoanInterestOutstanding(...)`, passing the vault asset and fee parameters to a shared helper.

3. `defaultLoan()` now checks whether `sfAssetsTotal` is smaller than `vaultDefaultAmount` before subtracting.

4. `unimpairLoan()` now checks whether `sfLossUnrealized` is smaller than `principalOutstanding + interestOutstanding` before subtracting.

5. `ValidLoan::finalize()` now fails if `sfAssetsAvailable` or `sfPrincipalOutstanding` is negative.

6. These changes strengthen accounting invariants, but the supplied evidence does not establish a vulnerability thesis.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/LoanSet.cpp | 340 | computes loan interest allocated to the vault using the shared LoanInterestOutstanding helper instead of local math |
| src/xrpld/app/tx/detail/LoanManage.cpp | 226 | handles loan default accounting and now rejects vault asset-total underflow with tefBAD_LEDGER |
| src/xrpld/app/tx/detail/LoanManage.cpp | 304 | handles loan unimpair accounting and now rejects vault unrealized-loss underflow with tefBAD_LEDGER |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 1999 | adds ValidLoan invariant checks that loan assets available and principal outstanding are non-negative |
| src/xrpld/app/tx/detail/LoanDelete.cpp | 42 | new LoanDelete transaction implementation in the same lending protocol path |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/LoanSet.cpp:340` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
TenthBips32 const managementFeeRate{brokerSle->at(sfManagementFeeRate)};
    // The total amount if interest the loan is expected to generate
    auto const loanInterest =
        tenthBipsOfValue(principalRequested, interestRate);
    // The portion of the loan interest that will go to the vault (total
    // interest minus the management fee)
    auto const loanInterestToVault =
```
After
```cpp
TenthBips32 const managementFeeRate{brokerSle->at(sfManagementFeeRate)};
    // The portion of the loan interest that will go to the vault (total
    // interest minus the management fee)
    auto const loanInterestToVault = LoanInterestOutstanding(
        vaultAsset, principalRequested, interestRate, managementFeeRate);
    auto const startDate = tx[sfStartDate];
    auto const paymentInterval =
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/LoanManage.cpp:304` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
{
    // Update the Vault object(clear "paper loss")
    vaultSle->at(sfLossUnrealized) -=
        principalOutstanding + interestOutstanding;
    view.update(vaultSle);
```
After
```cpp
{
    // Update the Vault object(clear "paper loss")
    auto vaultLossUnrealizedProxy = vaultSle->at(sfLossUnrealized);
    auto const lossReversed = principalOutstanding + interestOutstanding;
    if (vaultLossUnrealizedProxy < lossReversed)
    {
        JLOG(j.warn())
            << "Vault unrealized loss is less than the amount to be cleared";
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/LoanManage.cpp:226` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
view.update(loanSle);

    // Move the First-Loss Capital from the LoanBroker pseudo-account to the
    // Vault pseudo-account:
    return accountSend(
```
After
```cpp
view.update(loanSle);

    // Update the Vault object:

    // Decrease the Total Value of the Vault:
    auto vaultAssetsTotalProxy = vaultSle->at(sfAssetsTotal);
    if (vaultAssetsTotalProxy < vaultDefaultAmount)
    {
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:1999` (changes how canonical state is encoded, returned, or reconstructed)

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
        if (after->at(sfAssetsAvailable) < 0)
        {
            JLOG(j.fatal())
                << "Invariant failed: Loan assets available is negative";
            return false;
        }
```

# Fix Pattern

Centralize domain accounting calculations, add explicit sufficient-balance checks before ledger-field decrements, and add final invariant checks for negative loan accounting fields.

## How It Was Fixed

`LoanSet.cpp` now uses `LoanInterestOutstanding(...)` for vault interest allocation. `LoanManage.cpp` now guards reductions of `sfAssetsTotal` and `sfLossUnrealized`, returning `tefBAD_LEDGER` on inconsistent ledger state. `InvariantCheck.cpp` now rejects negative `sfAssetsAvailable` and `sfPrincipalOutstanding` values during loan invariant validation.

# Why It Matters

1. Avoids applying shown vault decrements when the current accounting value is too small.

2. Adds checks for negative loan accounting fields.

3. Makes vault interest allocation use a shared helper instead of duplicated arithmetic.

4. May be security relevant in a ledger system, but exploitability is not shown.

# Evidence Notes

The strongest evidence is in `LoanSet.cpp`, `LoanManage.cpp`, and `InvariantCheck.cpp`. The provided snippets support accounting hardening and math-correctness changes. They do not show a concrete attacker-controlled path, malformed transaction trigger, privilege bypass, consensus divergence, node crash, or demonstrated asset loss. The commit also includes feature implementation work such as `LoanDelete`, which should not be treated as the root cause based on the supplied snippets. Protocol security invariant: Loan and vault accounting should preserve non-negative ledger fields and compute interest/management-fee allocations consistently, but the provided evidence does not establish that the old behavior created an exploitable security vulnerability. Verification notes: No concrete exploit path is shown by the patch evidence. No authorization bypass is demonstrated in the provided snippets. No proof is provided that malformed external input can force the underflow states. No consensus split or node crash is proven. The commit includes feature implementation work, so not every changed file should be treated as a security fix. Downgraded from likely security-hardening to unclear because exploitability is not established. Removed unsupported serialization/API-boundary claims from the heuristic baseline. Kept the subsystem as lending loan/vault accounting because that is directly supported by the changed files. Set `keep_in_security_corpus` to false under the unclear-verdict rule. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `ledger-accounting-invariant-hardening`
Final impact type: `ledger-integrity, state-consistency`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, loan-vault-accounting, invariant-check, underflow-guard`

The evidence does not prove a concrete exploit, but it does show security-relevant hardening in a blockchain transaction path: loan/vault ledger accounting now rejects insufficient balances before subtracting, uses a shared interest calculation, and adds invariant failures for negative loan fields. In a ledger system, preventing negative accounting state and guarded value reductions is strong enough to retain as security-hardening, while avoiding stronger claims of a confirmed vulnerability or asset-theft exploit.

## Security Evidence

1. LoanManage now checks sfLossUnrealized before subtracting principal plus interest and returns tefBAD_LEDGER on insufficient value.
2. LoanManage now checks sfAssetsTotal before reducing it by the default amount and returns tefBAD_LEDGER on insufficient value.
3. InvariantCheck now rejects negative sfAssetsAvailable and sfPrincipalOutstanding for Loan objects.
4. Changed code is in transaction-processing loan/vault ledger accounting, a security-sensitive blockchain subsystem.

## Missing Evidence

1. No demonstrated attacker-controlled transaction sequence is provided.
2. No proof of asset loss, unauthorized transfer, consensus failure, or node crash is shown.
3. Commit also includes feature implementation work, so not every touched file is security-relevant.
4. The exact prior behavior of numeric underflow or negative STNumber handling is not established from the supplied snippets.

## Claim Boundaries

1. Validate only as security-hardening, not as a confirmed security-fix.
2. Do not claim authorization bypass, serialization bug, client-view divergence, or consensus split from this evidence.
3. Do not claim exploitability or fund theft without additional proof.
4. The supported claim is conservative: ledger accounting invariant hardening in the loan/vault transaction path.
