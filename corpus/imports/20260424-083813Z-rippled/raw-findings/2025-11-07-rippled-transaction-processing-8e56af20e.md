---
case_id: case_20251107_8e56af20e
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2025-11-07
source_refs:
  - git:8e56af20ee9e9e35b50c66d9ab10e63ef841955d
  - "src/libxrpl/basics/Number.cpp:220"
  - "src/libxrpl/basics/Number.cpp:245"
  - "include/xrpl/basics/Number.h:29"
  - "src/xrpld/app/tx/detail/InvariantCheck.cpp:2421"
bug_class: numeric-representability-hardening
impact_type:
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - vault-accounting
  - numeric-bounds
  - representability-check
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch separates Number validity from representability and adds explicit representability checks for vault aggregate fields. The supplied evidence supports a conservative security-hardening classification: unrepresentable Number values are described as subject to rounding or truncation, and ValidVault::finalize now rejects vault state whose tracked aggregate amounts are not representable. The evidence does not establish a concrete exploit, crash path, or funds-loss scenario.

## Observed Patch Facts

1. In `src/libxrpl/basics/Number.cpp`, the patch replaces `if (enforceInteger_ != none)` with `return valid(enforceInteger_);`.

2. In `src/libxrpl/basics/Number.cpp`, the patch replaces `Number&` with `bool`.

3. In `include/xrpl/basics/Number.h`, the patch replaces `* - weak: If the absolute value is greater than maxIntValue, valid() will` with `* - compatible: If the absolute value is greater than maxIntValue, valid()`.

4. In `src/xrpld/app/tx/detail/InvariantCheck.cpp`, the patch replaces `auto const updatedShares = [&]() -> std::optional<Shares> {` with `if (!afterVault.assetsTotal.representable() ||`.

## Project Context

The changed code sits primarily in `src/libxrpl/basics`, `src/libxrpl`, `include/xrpl/basics`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/xrpld/app/tx/detail/apply.cpp`, `src/xrpld/app/tx/detail/XChainBridge.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/libxrpl/protocol/STNumber.cpp`, `src/libxrpl/json/json_reader.cpp`. The strongest project-level identifiers around this patch are `Number`, `Number::valid`, `value`, and `valid`. Nearby tests or test-like files include `include/xrpl/beast/unit_test/suite.h`, `include/xrpl/beast/unit_test/detail/const_container.h`.

## Before/After Behavior

Before the patch, the documented Number enforcement model did not separately expose representability, and the supplied ValidVault::finalize hunk shows no explicit check that assetsTotal, assetsAvailable, assetsMaximum, or lossUnrealized were within the Number mantissa range. After the patch, Number has separate compatible, weak, and strong enforcement semantics, representable() checks +/- maxMantissa, weak enforcement is documented as throwing for unrepresentable values, and ValidVault::finalize fails the invariant when any tracked vault aggregate field is not representable.

# Root Cause

The pre-patch model conflated policy validity with exact numeric representability for Number-backed integer amounts. This left at least the shown vault aggregate invariant without an explicit guard against values beyond Number::maxMantissa, even though the commit states such values may be rounded or truncated.

## Walkthrough

1. Number.h updates the integer enforcement model to distinguish compatible, weak, and strong behavior around validity and representability.

2. Number.cpp changes Number::valid() to route through enforcement-specific validity logic.

3. Number.cpp adds Number::representable(), which checks enforced integer values against maxMantissa and -maxMantissa.

4. The commit text states that representable means <= Number::maxMantissa and that unrepresentable numbers will be rounded or truncated.

5. ValidVault::finalize now checks assetsTotal, assetsAvailable, assetsMaximum, and lossUnrealized with representable().

6. If any of those fields is not representable, the vault invariant fails.

7. The evidence supports numeric state-integrity hardening in vault invariant handling, not a proven remotely exploitable vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| include/xrpl/basics/Number.h | 29 | Defines integer enforcement levels, including compatible, weak, and strong semantics for valid versus representable Number values. |
| src/libxrpl/basics/Number.cpp | 220 | Routes Number::valid() through enforcement-specific validity semantics rather than treating all non-none enforcement identically. |
| src/libxrpl/basics/Number.cpp | 245 | Adds Number::representable() to check maxMantissa bounds before values can be rounded or truncated. |
| src/xrpld/app/tx/detail/InvariantCheck.cpp | 2421 | Extends the ValidVault invariant to fail when vault aggregate amount fields are not representable. |
| src/xrpld/app/tx/detail/VaultDeposit.cpp | 0 | Vault transaction path touched by the commit; likely uses the revised Number bounds for deposit accounting. |
| src/xrpld/app/tx/detail/VaultWithdraw.cpp | 0 | Vault transaction path touched by the commit; likely uses the revised Number bounds for withdrawal accounting. |

## Code Snippets

## Snippet 1

Context: `src/libxrpl/basics/Number.cpp:220` (changes a sensitive control or state-update path)

Before
```cpp
Number::valid() const noexcept
{
    if (enforceInteger_ != none)
    {
        static Number const max = maxIntValue;
```
After
```cpp
Number::valid() const noexcept
{
    return valid(enforceInteger_);
}

bool
Number::valid(EnforceInteger enforce)
{
```

## Snippet 2

Context: `src/libxrpl/basics/Number.cpp:245` (changes a sensitive control or state-update path)

Before
```cpp
}

Number&
Number::operator+=(Number const& y)
```
After
```cpp
}

bool
Number::representable() const noexcept
{
    if (enforceInteger_ != none)
    {
        static Number const max = maxMantissa;
```

## Snippet 3

Context: `include/xrpl/basics/Number.h:29` (changes a sensitive control or state-update path)

Before
```c
*
     * - none: No enforcement. The value may vary freely. This is the default.
     * - weak: If the absolute value is greater than maxIntValue, valid() will
     *   return false.
     * - strong: Assignment operations will throw if the absolute value is above
     *   maxIntValue.
     */
    enum EnforceInteger { none, weak, strong };
```
After
```c
*
     * - none: No enforcement. The value may vary freely. This is the default.
     * - compatible: If the absolute value is greater than maxIntValue, valid()
     *   will return false. Needed for backward compatibility with XRP used in
     *   AMMs, and available for functions that will do their own checking. This
     *   is the default for automatic conversions from XRPAmount to Number.
     * - weak: Like compatible, plus, if the value is unrepresentable (larger
     *   than maxMantissa), assignment and other operations will throw.
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/InvariantCheck.cpp:2421` (changes bounds, limits, or capacity handling)

Before
```cpp
"ripple::ValidVault::finalize : single vault operation");

    auto const updatedShares = [&]() -> std::optional<Shares> {
        // At this moment we only know that a vault is being updated and there
```
After
```cpp
"ripple::ValidVault::finalize : single vault operation");

    if (!afterVault.assetsTotal.representable() ||
        !afterVault.assetsAvailable.representable() ||
        !afterVault.assetsMaximum.representable() ||
        !afterVault.lossUnrealized.representable())
    {
        JLOG(j.fatal()) << "Invariant failed: vault overflowed maximum current "
```

# Fix Pattern

Separate validity from representability, add an explicit representability predicate, and enforce it at the vault invariant boundary for aggregate ledger amounts.

## How It Was Fixed

The patch introduced a compatible enforcement mode for legacy validity behavior, documented stricter weak and strong enforcement, added Number::representable() using maxMantissa bounds, and extended ValidVault::finalize to reject non-representable vault aggregate fields.

# Why It Matters

1. Unrepresentable Number values may be rounded or truncated according to the commit text.

2. Vault aggregate fields now have an explicit representability guard in invariant checking.

3. The change reduces ambiguity between policy-valid values and exactly representable values.

4. The provided evidence does not prove exploitability, node crash, or theft.

# Evidence Notes

Grounded evidence comes from include/xrpl/basics/Number.h line 29, src/libxrpl/basics/Number.cpp lines 220 and 245, the commit message, and src/xrpld/app/tx/detail/InvariantCheck.cpp line 2421. Claims about malformed transaction inputs, panics, mempool behavior, funds theft, or a specific exploit path are not supported by the supplied hunks and are excluded. Protocol security invariant: Consensus-relevant ledger amount handling must distinguish values that satisfy policy validity from values that are exactly representable by Number, and vault aggregate fields must not pass invariant checks when they exceed Number::maxMantissa and may be rounded or truncated. Verification notes: The patch does not by itself prove remote exploitability. The patch does not prove malformed transactions can crash a node. The patch does not prove funds can be stolen or unauthorized balances created. The evidence does not show a specific pre-patch transaction sequence that reaches an unrepresentable vault value. AMM compatibility changes are shown, but the concrete AMM security impact is not proven by the provided hunks. No concrete pre-patch transaction sequence is shown. No externally triggerable exploit path is demonstrated. No node crash or panic path is established by the supplied evidence. AMM-related compatibility is mentioned in the commit text, but the provided hunks do not establish a concrete AMM security impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `numeric-representability-hardening`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, vault-accounting, numeric-bounds, representability-check, state-integrity`

The supplied patch evidence supports retaining this as security hardening, not a proven security fix. It separates Number validity from representability, documents that unrepresentable values can be rounded or truncated, and adds an invariant check rejecting vault aggregate fields that exceed the representable mantissa range. Because this occurs in consensus-relevant ledger/vault accounting, the change tightens security-sensitive state handling. However, the evidence does not prove exploitability, funds loss, node crash, or liveness failure, so the original liveness framing is too specific.

## Security Evidence

1. Number gains explicit representable() logic bounded by maxMantissa and -maxMantissa.
2. The commit message states unrepresentable numbers will be rounded or truncated.
3. Weak enforcement is changed to throw when integer values are unrepresentable.
4. ValidVault::finalize now fails the vault invariant if assetsTotal, assetsAvailable, assetsMaximum, or lossUnrealized are not representable.
5. The changed code is in blockchain transaction/vault accounting and invariant checking paths.

## Missing Evidence

1. No concrete pre-patch transaction sequence reaches an unrepresentable vault value.
2. No demonstrated exploit path, theft, unauthorized balance creation, or consensus split is shown.
3. No evidence establishes a node crash or liveness failure.
4. No test excerpt proves a specific security regression was fixed.

## Claim Boundaries

1. Classify as security-hardening rather than security-fix.
2. Do not claim confirmed exploitability or funds loss from the supplied evidence.
3. Do not preserve the liveness-failure impact because the patch evidence only supports numeric state-integrity hardening.
4. AMM compatibility is mentioned, but the supplied hunks do not establish a concrete AMM security impact.
