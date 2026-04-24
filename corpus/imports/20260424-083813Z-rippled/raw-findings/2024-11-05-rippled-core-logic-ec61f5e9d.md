---
case_id: case_20241105_ec61f5e9d
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
source_quality: high
date: 2024-11-05
source_refs:
  - git:ec61f5e9d32114eac1a2020c3b26abc7299e49e8
  - "src/xrpld/app/tx/detail/AMMWithdraw.cpp:639"
  - "src/xrpld/app/tx/detail/AMMWithdraw.cpp:592"
  - "src/xrpld/app/paths/detail/AMMLiquidity.cpp:212"
  - "src/xrpld/app/tx/detail/AMMWithdraw.cpp:710"
bug_class: missing-reserve-check
impact_type:
  - reserve-enforcement
  - protocol-invariant
confidence: medium
tags:
  - blockchain-core
  - amm
  - withdrawal
  - reserve-enforcement
  - trustline
  - amendment-gated
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is that fixAMMv1_2 adds an amendment-gated reserve check in AMMWithdraw before sending a second withdrawn non-XRP issued asset. The evidence supports a likely protocol security fix around reserve enforcement, but does not prove exploitability, consensus impact, or that downstream accountSend lacked all reserve enforcement.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/AMMWithdraw.cpp`, the patch adds `if (auto const err = sufficientReserve(amount2WithdrawActual->issue());`.

2. In `src/xrpld/app/tx/detail/AMMWithdraw.cpp`, the patch replaces `// Withdraw amountWithdraw` with `// Check the reserve in case a trustline has to be created`.

3. In `src/xrpld/app/paths/detail/AMMLiquidity.cpp`, the patch replaces `catch (std::overflow_error const& e)` with `else if (view.rules().enabled(fixAMMv1_2))`.

4. In `src/xrpld/app/tx/detail/AMMWithdraw.cpp`, the patch adds `mPriorBalance,`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, `src/xrpld/app/paths/detail`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/xrpld/app/tx/detail/XChainBridge.cpp`, `src/xrpld/app/tx/detail/Transactor.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/XChainBridge.cpp`, `src/xrpld/app/tx/detail/Transactor.cpp`. The strongest project-level identifiers around this patch are `const`, `view`, `auto`, and `issue`.

## Before/After Behavior

Before the patch, the visible `amount2WithdrawActual` branch proceeded directly to `accountSend`. After the patch, `AMMWithdraw::withdraw` defines a `sufficientReserve` helper, skips it for XRP or when fixAMMv1_2 is disabled, checks whether a trustline exists for non-XRP issues, and returns an error before `accountSend` if the reserve check fails.

# Root Cause

The evidenced AMM withdraw path lacked a visible local reserve precondition before sending a non-XRP issued asset in a branch where a trustline may need to be created. The exact downstream behavior of `accountSend` is not established by the supplied snippets, so the root cause should be limited to missing explicit reserve enforcement in this AMM withdraw path.

## Walkthrough

1. `AMMWithdraw::withdraw` reaches a second withdrawal leg guarded by `if (amount2WithdrawActual)`.

2. The pre-patch snippet shows that branch entering `accountSend` without the newly added local reserve check.

3. The patch introduces an amendment-gated `sufficientReserve(Issue const& issue)` helper.

4. The helper returns success when fixAMMv1_2 is disabled or the issue is XRP.

5. For non-XRP issues, the helper checks whether the withdrawing account already has the relevant trustline.

6. The patched second withdrawal leg calls `sufficientReserve(amount2WithdrawActual->issue())` before `accountSend`.

7. If the helper returns an error, the withdrawal exits before the send operation.

8. Other changes in AMMLiquidity and equal-withdraw calculation are related AMM fixes, but the provided evidence does not make them the root security issue.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/AMMWithdraw.cpp | 592 | adds amendment-gated sufficientReserve helper for non-XRP withdrawal issues when a trustline may need to be created |
| src/xrpld/app/tx/detail/AMMWithdraw.cpp | 639 | checks reserve before sending the second withdrawn issued asset to the withdrawing account |
| src/xrpld/app/tx/detail/AMMWithdraw.cpp | 710 | passes prior LP token balance into equal withdrawal calculation, suggesting corrected AMM withdraw accounting context |
| src/xrpld/app/paths/detail/AMMLiquidity.cpp | 212 | adds amendment-gated max AMM offer fallback when spot-price quality adjustment fails |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/AMMWithdraw.cpp:639` (updates aggregate accounting or lifecycle state)

Before
```cpp
if (amount2WithdrawActual)
    {
        res = accountSend(
            view,
```
After
```cpp
if (amount2WithdrawActual)
    {
        if (auto const err = sufficientReserve(amount2WithdrawActual->issue());
            err != tesSUCCESS)
            return {err, STAmount{}, STAmount{}, STAmount{}};

        res = accountSend(
            view,
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/AMMWithdraw.cpp:592` (updates aggregate accounting or lifecycle state)

Before
```cpp
}

    // Withdraw amountWithdraw
    auto res = accountSend(
```
After
```cpp
}

    // Check the reserve in case a trustline has to be created
    bool const enabledFixAMMv1_2 = view.rules().enabled(fixAMMv1_2);
    auto sufficientReserve = [&](Issue const& issue) -> TER {
        if (!enabledFixAMMv1_2 || isXRP(issue))
            return tesSUCCESS;
        if (!view.exists(keylet::line(account, issue)))
```

## Snippet 3

Context: `src/xrpld/app/paths/detail/AMMLiquidity.cpp:212` (updates aggregate accounting or lifecycle state)

Before
```cpp
*this, *amounts, balances, Quality{*amounts});
            }
        }
        catch (std::overflow_error const& e)
```
After
```cpp
*this, *amounts, balances, Quality{*amounts});
            }
            else if (view.rules().enabled(fixAMMv1_2))
            {
                if (auto const maxAMMOffer = maxOffer(balances, view.rules());
                    maxAMMOffer &&
                    Quality{maxAMMOffer->amount()} > *clobQuality)
                    return maxAMMOffer;
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/AMMWithdraw.cpp:710` (updates aggregate accounting or lifecycle state)

Before
```cpp
FreezeHandling::fhZERO_IF_FROZEN,
            isWithdrawAll(ctx_.tx),
            ctx_.journal);
    return {ter, newLPTokenBalance};
```
After
```cpp
FreezeHandling::fhZERO_IF_FROZEN,
            isWithdrawAll(ctx_.tx),
            mPriorBalance,
            ctx_.journal);
    return {ter, newLPTokenBalance};
```

# Fix Pattern

Add an amendment-gated precondition check before state-changing AMM withdrawal send logic so issued-asset withdrawals that may create trustlines are rejected when reserve requirements are not satisfied.

## How It Was Fixed

The patch adds a local `sufficientReserve` helper in `src/xrpld/app/tx/detail/AMMWithdraw.cpp` and calls it before sending `amount2WithdrawActual`. On failure, the function returns immediately with empty amounts and the error code instead of invoking `accountSend`.

# Why It Matters

1. Preserves reserve enforcement in AMM withdrawal.

2. Avoids proceeding with an issued-asset withdrawal when a required trustline may lack reserve.

3. Keeps the fix amendment-gated for protocol activation.

4. Exploitability and broader consensus impact are not proven by the supplied evidence.

# Evidence Notes

Primary evidence is `src/xrpld/app/tx/detail/AMMWithdraw.cpp` around lines 592 and 639, where the new helper and call are shown. The comment explicitly says the check is for cases where a trustline has to be created. The snippets do not include the full helper body, full `accountSend` semantics, tests, advisory text, or an exploit scenario. The AMMLiquidity max-offer fallback and `mPriorBalance` change are not sufficient on their own to classify a vulnerability. Protocol security invariant: AMM withdrawal of a non-XRP issued asset must preserve XRPL reserve requirements when the withdrawal may require creating a trustline for the receiving account. Verification notes: The patch does not prove remote exploitability or consensus disruption by itself. The patch does not show whether accountSend previously always created trustlines without any reserve enforcement in all cases. The AMMLiquidity max-offer fallback is not enough on its own to classify a security issue. No advisory, issue discussion, or full test assertions are provided in the input. No external advisory or issue discussion was provided. No test assertions were provided in the input. The finding is bounded to the visible AMMWithdraw reserve-check change. Confidence is downgraded from high to medium because downstream reserve behavior and exploitability are not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-reserve-check`
Final impact type: `reserve-enforcement, protocol-invariant`
Final confidence: `medium`
Final tags: `blockchain-core, amm, withdrawal, reserve-enforcement, trustline, amendment-gated`

The supplied patch evidence clearly adds an amendment-gated reserve precondition to AMM withdrawal before sending a second non-XRP issued asset when a trustline may need to be created. That is security-relevant hardening of a protocol/accounting invariant, but the snippets do not prove a concrete exploitable vulnerability, consensus failure, or that downstream accountSend previously allowed reserve violation in all relevant cases. The original security-fix classification is therefore too strong; security-hardening is better supported.

## Security Evidence

1. AMMWithdraw now defines a sufficientReserve helper with an explicit comment about checking reserve when a trustline has to be created.
2. The amount2WithdrawActual path now calls sufficientReserve before accountSend and exits early on error.
3. The check is gated by fixAMMv1_2, indicating a protocol amendment/fix path rather than ordinary refactoring.
4. The affected code is in AMM withdrawal logic, a blockchain state-transition path involving issued assets and trustlines.

## Missing Evidence

1. No full helper body is provided showing the exact reserve calculation and error behavior.
2. No accountSend implementation evidence proves the prior path always missed reserve enforcement.
3. No tests, advisory, issue discussion, or exploit scenario are supplied.
4. The AMMLiquidity fallback and mPriorBalance changes are not independently shown to be security issues.

## Claim Boundaries

1. Keep the finding limited to amendment-gated reserve enforcement in AMMWithdraw for non-XRP withdrawals that may create trustlines.
2. Do not claim confirmed exploitability or a concrete funds-loss scenario from the supplied patch alone.
3. Do not claim consensus impact beyond tightening a protocol state-transition invariant.
4. Do not treat the AMMLiquidity max-offer fallback as part of the validated security finding without more evidence.
