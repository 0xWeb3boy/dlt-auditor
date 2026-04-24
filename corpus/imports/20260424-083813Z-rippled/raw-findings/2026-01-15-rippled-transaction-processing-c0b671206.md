---
case_id: case_20260115_c0b671206
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2026-01-15
source_refs:
  - git:c0b67120644d4cf7083a14efa643892407556ee4
  - "src/xrpld/app/tx/detail/LoanPay.cpp:443"
  - "src/xrpld/app/tx/detail/LoanPay.cpp:421"
  - "src/xrpld/app/tx/detail/LoanPay.cpp:572"
  - "src/xrpld/app/tx/detail/LoanPay.cpp:552"
bug_class: rounding-accounting-yield-theft
impact_type:
  - economic-value-theft
  - accounting-integrity
tags:
  - blockchain-core
  - lending
  - loanpay
  - rounding
  - economic-accounting
  - yield-theft
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

Likely security fix in rippled's lending LoanPay path. The strongest evidence is the commit message saying a new test covers "Yield Theft via Rounding Manipulation" and now verifies no yield theft occurs, together with changes around rounded vault payments, assets-available/assets-total checks, and funds-conservation checks in `LoanPay.cpp`. The exact exploit sequence and some implementation changes are not shown, so this should not be classified as confirmed with high confidence.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/LoanPay.cpp`, the patch replaces `*assetsAvailableProxy <= *assetsTotalProxy,` with `Number const assetsAvailableAfter = *assetsAvailableProxy;`.

2. In `src/xrpld/app/tx/detail/LoanPay.cpp`, the patch replaces `if (*assetsAvailableProxy > *assetsTotalProxy)` with `JLOG(j_.debug()) << "total paid to vault raw: " << totalPaidToVaultRaw`.

3. In `src/xrpld/app/tx/detail/LoanPay.cpp`, the patch replaces `: accountHolds(view, brokerPayee, asset, fhIGNORE_FREEZE, ahIGNORE_AUTH, j_, Spendabl...` with `: accountHolds(`.

4. In `src/xrpld/app/tx/detail/LoanPay.cpp`, the patch replaces `Number const assetsAvailableAfter = *assetsAvailableProxy;` with `Number const pseudoAccountBalanceAfter = accountHolds(`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/xrpld/app/tx/detail/VaultDeposit.cpp`, `src/xrpld/app/tx/detail/VaultClawback.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/VaultDeposit.cpp`, `src/xrpld/app/tx/detail/VaultClawback.cpp`. The strongest project-level identifiers around this patch are `const`, `FreezeHandling::fhIGNORE_FREEZE`, `AuthHandling::ahIGNORE_AUTH`, and `assetsAvailableProxy`.

## Before/After Behavior

Before the patch, LoanPay updated vault accounting using rounded repayment values and checked `assetsAvailable <= assetsTotal`, with additional fatal/internal-error handling when assets available exceeded assets total. After the patch, the visible code captures post-rounding values into explicit variables, duplicates invariant checks after rounding, adds handling for the case where the rounded vault payment leaves assets available unchanged, and keeps post-transfer balance checks for the payer, vault pseudo-account, and broker. The commit also adds a regression test described as preventing yield theft via rounding manipulation, but the provided evidence does not show the full test body or the exact `STAmount.h` and `LendingHelpers.cpp` changes.

# Root Cause

The supported root cause is insufficiently robust handling of rounded repayment state in the lending repayment path. The evidence supports a rounding/accounting mismatch around `assetsAvailableProxy`, `assetsTotalProxy`, and balance-conservation checks, but does not show enough detail to prove the exact attacker workflow or the precise arithmetic flaw in helper code.

## Walkthrough

1. LoanPay applies repayment calculations involving `totalPaidToVaultRounded`, broker payment, and changes to vault asset accounting.

2. The local invariant requires vault assets available to remain less than or equal to assets outstanding after rounding-sensitive updates.

3. The patch makes post-rounding values explicit with `assetsAvailableAfter` and `assetsTotalAfter`.

4. The changed comments identify an edge case where the vault payment may be zero or rounded to zero, and the code is intended to fail gracefully if that occurs.

5. Funds are moved among the payer, vault pseudo-account, and broker.

6. Debug/invariant code checks the vault pseudo-account balance against recorded vault availability and checks conservation across the affected balances.

7. The commit metadata states that a regression test for "Yield Theft via Rounding Manipulation" was added and now verifies no yield theft occurs.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/LoanPay.cpp | 415 | Updates vault assets available and total outstanding after rounded repayment amounts are computed, then checks the assets-available-not-greater-than-total invariant before funds are moved. |
| src/xrpld/app/tx/detail/LoanPay.cpp | 443 | Captures post-rounding asset totals and duplicates invariant checks after rounding, including handling for an unchanged assetsAvailable value that may indicate a zero or rounded-to-zero vault payment. |
| src/xrpld/app/tx/detail/LoanPay.cpp | 546 | After moving funds, compares vault pseudo-account holdings with recorded assets available in debug invariant coverage. |
| src/xrpld/app/tx/detail/LoanPay.cpp | 566 | Checks payer, vault, and broker balances after the repayment transfer to validate conservation of funds across affected accounts. |
| src/test/app/Loan_test.cpp | 1 | Adds regression coverage for yield theft via rounding manipulation and verifies the theft no longer occurs. |
| include/xrpl/protocol/STAmount.h | 1 | Touched amount/number handling relevant to rounded asset accounting, but the provided evidence does not show the exact change. |
| src/xrpld/app/misc/detail/LendingHelpers.cpp | 1 | Touched lending helper logic relevant to payment calculation, but the provided evidence does not show the exact change. |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/LoanPay.cpp:443` (changes a sensitive control or state-update path)

Before
```cpp
// Duplicate some checks after rounding
    XRPL_ASSERT_PARTS(
        *assetsAvailableProxy <= *assetsTotalProxy,
        "xrpl::LoanPay::doApply",
        "assets available must not be greater than assets outstanding");

#if !NDEBUG
```
After
```cpp
// Duplicate some checks after rounding
    Number const assetsAvailableAfter = *assetsAvailableProxy;
    Number const assetsTotalAfter = *assetsTotalProxy;

    XRPL_ASSERT_PARTS(
        assetsAvailableAfter <= *assetsTotalProxy,
        "xrpl::LoanPay::doApply",
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/LoanPay.cpp:421` (changes a sensitive control or state-update path)

Before
```cpp
"assets available must not be greater than assets outstanding");

    if (*assetsAvailableProxy > *assetsTotalProxy)
    {
        // LCOV_EXCL_START
        JLOG(j_.fatal()) << "Vault assets available must not be greater "
                            "than assets outstanding. Available: "
                         << *assetsAvailableProxy << ", Total: " << *assetsTotalProxy;
```
After
```cpp
"assets available must not be greater than assets outstanding");

    JLOG(j_.debug()) << "total paid to vault raw: " << totalPaidToVaultRaw
                     << ", total paid to vault rounded: " << totalPaidToVaultRounded
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/LoanPay.cpp:572` (changes persisted or aggregate state handling)

Before
```cpp
auto const brokerBalanceAfter = account_ == brokerPayee
        ? STAmount{asset, 0}
        : accountHolds(view, brokerPayee, asset, fhIGNORE_FREEZE, ahIGNORE_AUTH, j_, SpendableHandling::shFULL_BALANCE);

    XRPL_ASSERT_PARTS(
        accountBalanceBefore + vaultBalanceBefore + brokerBalanceBefore ==
            accountBalanceAfter + vaultBalanceAfter + brokerBalanceAfter,
        "xrpl::LoanPay::doApply",
```
After
```cpp
auto const brokerBalanceAfter = account_ == brokerPayee
        ? STAmount{asset, 0}
        : accountHolds(
              view,
              brokerPayee,
              asset,
              fhIGNORE_FREEZE,
              ahIGNORE_AUTH,
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/LoanPay.cpp:552` (changes aggregate state or economic accounting)

Before
```cpp
#if !NDEBUG
    Number const assetsAvailableAfter = *assetsAvailableProxy;
    Number const pseudoAccountBalanceAfter =
        accountHolds(view, vaultPseudoAccount, asset, FreezeHandling::fhIGNORE_FREEZE, AuthHandling::ahIGNORE_AUTH, j_);
    XRPL_ASSERT_PARTS(
        assetsAvailableAfter == pseudoAccountBalanceAfter,
```
After
```cpp
#if !NDEBUG
    Number const pseudoAccountBalanceAfter = accountHolds(
        view,
        vaultPseudoAccount,
        asset,
        FreezeHandling::fhIGNORE_FREEZE,
        AuthHandling::ahIGNORE_AUTH,
```

# Fix Pattern

Make post-rounding accounting state explicit, validate local vault-accounting invariants after rounding, handle zero-or-rounded-to-zero payment cases gracefully, and add regression coverage for the rounding-manipulation scenario.

## How It Was Fixed

The visible LoanPay changes capture post-rounding vault accounting values, preserve the assets-available-not-greater-than-assets-outstanding invariant, add handling for unchanged `assetsAvailableAfter`, and maintain balance-conservation checks after funds are moved. The commit also adds regression coverage for the named yield-theft scenario. The exact mechanics in `STAmount.h` and `LendingHelpers.cpp` are not provided, so their specific role cannot be stated.

# Why It Matters

1. LoanPay moves value in a lending repayment path.

2. Rounding errors in repayment accounting can affect who receives yield or principal.

3. The commit explicitly names a prior yield-theft scenario.

4. The evidence is scoped to lending/vault LoanPay behavior, not all transaction processing.

5. Exploit prerequisites and impact are not established from the supplied hunks.

# Evidence Notes

Grounded evidence includes `LoanPay.cpp` hunks around rounded vault payment accounting, post-rounding invariant checks, and balance-conservation checks, plus commit metadata saying a "Yield Theft via Rounding Manipulation" regression test was added. The mapper's broader claims about exact fix mechanics in `STAmount.h` and `LendingHelpers.cpp` are not fully supported because those diffs are not shown. The evidence supports likely security relevance, but not high-confidence confirmation of the full vulnerability mechanics. Protocol security invariant: LoanPay repayment processing must keep vault asset accounting consistent with actual balances after rounding: vault assets available must not exceed assets outstanding, repayments must conserve value across payer, vault pseudo-account, and broker, and rounding must not permit yield to be redirected or avoided. Verification notes: The patch evidence does not prove remote exploitability by itself. The exact attacker prerequisites and profitable transaction sequence are not shown beyond the named regression test. The impact is limited here to vault/lending LoanPay rounding and accounting behavior, not all XRPL transaction processing. The provided hunks do not show the exact STAmount.h or LendingHelpers.cpp changes, so their specific roles are inferred only from filenames and commit scope. No claim is made that consensus integrity or ledger-wide supply invariants were directly compromised outside this LoanPay path. Do not claim remote exploitability; it is not shown. Do not claim consensus-wide impact; it is not shown. Do not describe the exact regression test assertions beyond the commit message. Treat `STAmount.h` and `LendingHelpers.cpp` as relevant but unspecified supporting changes. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `rounding-accounting-yield-theft`
Final impact type: `economic-value-theft, accounting-integrity`
Final tags: `blockchain-core, lending, loanpay, rounding, economic-accounting, yield-theft`

The finding should stay in the security corpus, but with bounded claims. The commit metadata explicitly says a regression test for "Yield Theft via Rounding Manipulation" was added and now verifies no yield theft occurs, and the shown LoanPay changes are in a value-moving lending repayment path with rounding-sensitive vault accounting and conservation checks. The supplied hunks do not prove the complete exploit sequence or all arithmetic changes, so this is likely rather than confirmed.

## Security Evidence

1. Commit body names "Yield Theft via Rounding Manipulation" and says the new test verifies no yield theft occurs.
2. LoanPay updates lending/vault repayment accounting involving rounded payments to the vault and broker.
3. Patch adds explicit post-rounding asset values and invariant checks around assets available versus assets outstanding.
4. Patch comments identify a zero or rounded-to-zero vault payment edge case and add graceful handling.
5. Funds-conservation and pseudo-account balance checks are maintained around payer, vault, and broker balances.

## Missing Evidence

1. Full regression test body is not provided.
2. Exact STAmount.h and LendingHelpers.cpp changes are not shown.
3. No concrete attacker transaction sequence or prerequisites are shown.
4. No demonstrated magnitude of possible theft or affected deployment scope is provided.

## Claim Boundaries

1. Treat this as a likely economic security fix in the LoanPay lending path.
2. Do not claim consensus-wide compromise from the supplied evidence.
3. Do not claim remote exploitability beyond normal transaction submission unless separately shown.
4. Do not describe exact exploit mechanics beyond rounding manipulation and yield theft.
5. Do not rely on unspecified helper/header changes for detailed root-cause claims.
