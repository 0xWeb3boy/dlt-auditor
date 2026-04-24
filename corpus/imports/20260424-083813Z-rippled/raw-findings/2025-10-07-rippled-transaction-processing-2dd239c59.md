---
case_id: case_20251007_2dd239c59
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2025-10-07
source_refs:
  - git:2dd239c59fc66b665667b95eae24c918a5abc7d3
  - "src/xrpld/app/tx/detail/LoanSet.cpp:318"
  - "src/xrpld/app/tx/detail/LoanPay.cpp:250"
  - "src/xrpld/app/tx/detail/LoanPay.cpp:196"
  - "src/xrpld/app/tx/detail/LoanPay.cpp:364"
bug_class: missing-freeze-validation
impact_type:
  - freeze-restriction-bypass
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - loanpay
  - deep-freeze
  - recipient-validation
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The best-supported security finding is incomplete deep-freeze validation in LoanPay::preclaim. The patch adds checks for the broker owner and vault pseudo-account before LoanPay can return success. Other changes in the commit adjust precision, management-fee, and debt accounting behavior, but the provided evidence does not establish those accounting changes as independent vulnerabilities.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/LoanSet.cpp`, the patch replaces `return tecLIMIT_EXCEEDED;` with `return tecPRECISION_LOSS;`.

2. In `src/xrpld/app/tx/detail/LoanPay.cpp`, the patch replaces `Expected<LoanPaymentParts, TER> paymentParts =` with `auto const managementFeeOutstanding = [&]() {`.

3. In `src/xrpld/app/tx/detail/LoanPay.cpp`, the patch replaces `return tesSUCCESS;` with `if (auto const ret = checkDeepFrozen(ctx.view, brokerOwner, asset))`.

4. In `src/xrpld/app/tx/detail/LoanPay.cpp`, the patch replaces `// (which might be negative). debtDecrease may be negative, increasing the` with `// (which might be negative). totalPaidToVaultForDebt may be negative,`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/xrpld/app/tx/detail/LoanManage.cpp`, `src/xrpld/app/tx/detail/LoanDelete.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/SetTrust.cpp`, `src/xrpld/app/tx/detail/InvariantCheck.cpp`. The strongest project-level identifiers around this patch are `negative`, `auto`, `const`, and `debtDecrease`.

## Before/After Behavior

Before the patch, LoanPay::preclaim could return tesSUCCESS after existing checks without the shown deep-freeze checks for brokerOwner and vaultPseudoAccount. After the patch, LoanPay::preclaim calls checkDeepFrozen for both and returns the resulting error if either cannot receive funds. Separately, LoanSet now rejects nonzero-interest loans with no measurable interest due, LoanPay clamps negative computed management-fee outstanding to zero, and LoanBroker debt adjustment uses totalPaidToVaultForDebt instead of the prior debtDecrease expression.

# Root Cause

The grounded root cause is that LoanPay::preclaim did not validate all shown fund-receiving lending participants against deep-freeze restrictions. The evidence specifically supports missing checks for brokerOwner and vaultPseudoAccount, not a broader generic authorization bypass.

## Walkthrough

1. LoanPay preclaim validation runs before the state-changing payment path.

2. The pre-patch evidence shows the function returning tesSUCCESS after earlier checks, without the newly added brokerOwner and vaultPseudoAccount deep-freeze checks.

3. The patch adds checkDeepFrozen(ctx.view, brokerOwner, asset) and rejects the transaction if that recipient is deep frozen.

4. The patch adds checkDeepFrozen(ctx.view, vaultPseudoAccount, asset) and rejects the transaction if that pseudo-account is deep frozen.

5. LoanSet and LoanPay also receive accounting and precision fixes, but those hunks are best treated as correctness changes unless tied to a clearer security invariant.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/LoanPay.cpp | 196 | Adds preclaim deep-freeze checks for loan broker owner and vault pseudo-account recipients before LoanPay succeeds. |
| src/xrpld/app/tx/detail/LoanPay.cpp | 250 | Computes management fee outstanding from total value, principal, and interest while clamping negative overpayment-derived values. |
| src/xrpld/app/tx/detail/LoanPay.cpp | 364 | Updates LoanBroker debt adjustment to use totalPaidToVaultForDebt with rounding assertions. |
| src/xrpld/app/tx/detail/LoanSet.cpp | 318 | Rejects nonzero-interest loans whose computed outstanding value leaves no measurable interest due, returning precision loss. |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/LoanSet.cpp:318` (changes a sensitive control or state-update path)

Before
```cpp
// change right away.
        JLOG(j_.warn()) << "Loan is unable to pay principal.";
        return tecLIMIT_EXCEEDED;
    }
    // Check that the other computed values are valid
```
After
```cpp
// change right away.
        JLOG(j_.warn()) << "Loan is unable to pay principal.";
        return tecPRECISION_LOSS;
    }
    if (interestRate != 0 &&
        (properties.totalValueOutstanding - principalRequested) <= 0)
    {
        // Unless this is a zero-interst loan, there must be some interest due
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/LoanPay.cpp:250` (changes a sensitive control or state-update path)

Before
```cpp
TenthBips16 managementFeeRate{brokerSle->at(sfManagementFeeRate)};

    Expected<LoanPaymentParts, TER> paymentParts =
```
After
```cpp
TenthBips16 managementFeeRate{brokerSle->at(sfManagementFeeRate)};
    auto const managementFeeOutstanding = [&]() {
        auto const m = loanSle->at(sfTotalValueOutstanding) -
            loanSle->at(sfPrincipalOutstanding) - loanSle->at(sfInterestOwed);
        // It shouldn't be possible for this to result in a negative number, but
        // with overpayments, who knows?
        if (m < 0)
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/LoanPay.cpp:196` (changes a sensitive control or state-update path)

Before
```cpp
return ret;
    }

    return tesSUCCESS;
```
After
```cpp
return ret;
    }
    if (auto const ret = checkDeepFrozen(ctx.view, brokerOwner, asset))
    {
        JLOG(ctx.j.warn())
            << "Loan Broker can not receive funds (deep frozen).";
        return ret;
    }
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/LoanPay.cpp:364` (changes a sensitive control or state-update path)

Before
```cpp
// Decrease LoanBroker Debt by the amount paid, add the Loan value change
    // (which might be negative). debtDecrease may be negative, increasing the
    // debt
    auto const debtDecrease = totalPaidToVault - paymentParts->valueChange;
    XRPL_ASSERT_PARTS(
        isRounded(asset, debtDecrease, loanScale),
        "ripple::LoanPay::doApply",
```
After
```cpp
// Decrease LoanBroker Debt by the amount paid, add the Loan value change
    // (which might be negative). totalPaidToVaultForDebt may be negative,
    // increasing the debt
    XRPL_ASSERT_PARTS(
        isRounded(asset, totalPaidToVaultForDebt, loanScale),
        "ripple::LoanPay::doApply",
        "totalPaidToVaultForDebt rounding good");
```

# Fix Pattern

Add explicit recipient-complete validation in preclaim before allowing the transaction to proceed, while keeping related accounting corrections scoped to the lending payment calculations.

## How It Was Fixed

LoanPay::preclaim was extended with checkDeepFrozen calls for brokerOwner and vaultPseudoAccount, each returning the freeze-related TER before success. LoanSet::doApply now uses tecPRECISION_LOSS for precision conditions and rejects nonzero-interest loans with no measurable interest due. LoanPay::doApply now derives managementFeeOutstanding from total value, principal, and interest with a zero clamp, and updates LoanBroker debt using totalPaidToVaultForDebt with matching rounding validation.

# Why It Matters

1. Deep-freeze restrictions are intended to prevent frozen recipients from receiving the asset.

2. LoanPay involves multiple lending-related accounts or pseudo-accounts, so checking only some participants can leave a validation gap.

3. The evidence supports a likely freeze-enforcement fix, not a proven theft, consensus failure, or generic access-control bypass.

# Evidence Notes

The strongest evidence is LoanPay.cpp preclaim line 196, where checkDeepFrozen was added for brokerOwner and vaultPseudoAccount with log messages saying those recipients cannot receive funds when deep frozen. The LoanSet precision and LoanPay accounting hunks are real behavioral changes, but the supplied evidence does not prove they are security vulnerabilities. The heuristic claim of broad access-control failure is too strong; the grounded class is missing deep-freeze recipient validation. Protocol security invariant: Loan payment validation should reject issued-asset payment flows when any account or pseudo-account that may receive funds is deep frozen for the asset. Verification notes: The patch does not prove a complete exploit path or attacker-controlled theft scenario. The evidence does not show whether prior missing freeze checks were reachable on all LoanPay transactions or only specific broker/vault configurations. Management-fee and debt-calculation changes are accounting correctness fixes unless tied to a concrete security invariant elsewhere. No claim is made that consensus safety was violated beyond the shown transaction validation and ledger-accounting paths. The heuristic access-control framing is too broad; the concrete security issue shown is incomplete deep-freeze recipient validation. No complete exploit path is shown in the provided evidence. Reachability across all LoanPay configurations is not established. Accounting changes should not be classified as security fixes without additional evidence. The finding is kept because the deep-freeze checks directly enforce a protocol restriction on recipients. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-freeze-validation`
Final impact type: `freeze-restriction-bypass`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, loanpay, deep-freeze, recipient-validation`

The supplied patch evidence supports keeping this as a security-hardening case, centered on LoanPay adding missing deep-freeze checks for additional fund-receiving participants before preclaim succeeds. The evidence does not prove theft, privilege escalation, or a complete exploit path, so the original security-fix/access-control framing is too strong. The accounting and precision changes should be treated as correctness work from the provided evidence.

## Security Evidence

1. LoanPay::preclaim previously reached tesSUCCESS without the newly added brokerOwner and vaultPseudoAccount deep-freeze checks.
2. The patch adds checkDeepFrozen(ctx.view, brokerOwner, asset) and returns the error if the broker owner cannot receive funds.
3. The patch adds checkDeepFrozen(ctx.view, vaultPseudoAccount, asset) and returns the error if the vault pseudo-account cannot receive funds.
4. Log messages explicitly describe these recipients as unable to receive funds when deep frozen.

## Missing Evidence

1. No exploit scenario or attacker-controlled transaction flow is shown.
2. No test excerpt demonstrates a prior successful payment to a deep-frozen broker owner or vault pseudo-account.
3. The evidence does not establish whether all LoanPay configurations were affected.
4. The management-fee, debt, and precision hunks are not tied to a demonstrated security invariant.

## Claim Boundaries

1. Validate only the missing deep-freeze recipient checks as security-relevant.
2. Do not claim broader access-control failure or privilege misuse beyond freeze-rule enforcement.
3. Do not classify the accounting and rounding changes as security fixes from this evidence alone.
4. Treat this as hardening or enforcement tightening, not a proven concrete vulnerability.
