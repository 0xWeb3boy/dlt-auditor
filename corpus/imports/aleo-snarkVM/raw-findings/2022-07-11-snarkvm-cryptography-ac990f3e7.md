---
case_id: case_20220711_ac990f3e7
project: snarkvm
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: medium
date: 2022-07-11
source_refs:
  - git:ac990f3e7b98ee330a6e2b57cd465ccb2f9eddb3
  - "console/program/src/request/verify.rs:206"
  - "console/program/src/data_types/value_type/serialize.rs:111"
  - "console/program/src/data_types/value_type/serialize.rs:123"
  - "vm/compiler/src/process/stack/mod.rs:691"
bug_class: missing-balance-nonnegativity-constraint
impact_type:
  - value-conservation-bypass
confidence: medium
tags:
  - blockchain-core
  - vm
  - circuit-constraints
  - balance-accounting
  - value-conservation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported security-relevant change is in VM transition record-balance accounting. After summing record inputs and subtracting record outputs, the patch now asserts that `i64_balance` is not negative via `!i64_balance.msb()` before retaining the field consistency check. The external `ValueType` changes are test syntax corrections for `.record` parsing and are not the root cause.

## Observed Patch Facts

1. In `console/program/src/request/verify.rs`, the patch replaces `ValueType::from_str("token.aleo/token").unwrap(),` with `ValueType::from_str("token.aleo/token.record").unwrap(),`.

2. In `console/program/src/data_types/value_type/serialize.rs`, the patch replaces `check_serde_json(ValueType::<CurrentNetwork>::from_str("hello_world.aleo/new").unwrap...` with `check_serde_json(ValueType::<CurrentNetwork>::from_str("hello_world.aleo/new.record")...`.

3. In `console/program/src/data_types/value_type/serialize.rs`, the patch replaces `check_bincode(ValueType::<CurrentNetwork>::from_str("hello_world.aleo/new").unwrap());` with `check_bincode(ValueType::<CurrentNetwork>::from_str("hello_world.aleo/new.record").un...`.

4. In `vm/compiler/src/process/stack/mod.rs`, the patch replaces `A::assert_eq(i64_balance.to_field(), field_balance);` with `// Ensure the i64 balance MSB is false.`.

## Project Context

The changed code sits primarily in `console/program/src/request`, `console/program/src`, `console/program/src/data_types/value_type`, which anchors the finding in the `cryptography` area of the project. Historical context from `console/program/src/data_types/value_type/parse.rs`, `vm/compiler/src/process/stack/sample.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `console/program/src/data_types/value_type/parse.rs`, `vm/compiler/src/process/transition/output/serialize.rs`. The strongest project-level identifiers around this patch are `ValueType::from_str`, `ValueType`, `from_str`, and `unwrap`.

## Before/After Behavior

Before the patch, non-`stake.aleo/initialize` transitions only checked that `i64_balance.to_field()` matched `field_balance` after record input/output balance accounting. After the patch, those transitions also assert `!i64_balance.msb()`, requiring the signed balance to be non-negative, then keep the field equality check and add a public field-balance injection equality check. Separate tests changed external record strings from locator-only forms to locator-plus-`.record` forms.

# Root Cause

The transition balance check constrained consistency between the signed accumulator and field accumulator, but did not explicitly constrain the signed accumulator to be non-negative for ordinary transitions.

## Walkthrough

1. The stack transition logic initializes signed `i64_balance` and field `field_balance` accumulators.

2. Record input balances are added to both accumulators.

3. Record output balances are subtracted from both accumulators.

4. Before the patch, the final non-special-function check only required the signed accumulator converted to a field to equal the field accumulator.

5. The patch adds `A::assert(!i64_balance.msb())`, rejecting negative signed net balances.

6. The existing field consistency assertion remains, with a reference-form comparison change.

7. The patch also injects the computed field balance as public and asserts equality with the in-circuit field balance.

8. The `ValueType` test edits align external record examples with parser behavior requiring a `.record` suffix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| vm/compiler/src/process/stack/mod.rs | 691 | enforces non-negative net record balance and field/i64 consistency during transition processing |
| console/program/src/data_types/value_type/parse.rs | 19 | parses local and external record value types; contextual support for corrected `.record` suffix |
| console/program/src/request/verify.rs | 206 | test coverage for signing/verifying requests with external record input types |
| console/program/src/data_types/value_type/serialize.rs | 111 | serialization test baseline for external record value type syntax |

## Code Snippets

## Snippet 1

Context: `console/program/src/request/verify.rs:206` (changes the branch that decides whether execution stops or continues)

Before
```rust
ValueType::from_str("amount.private").unwrap(),
                ValueType::from_str("token.record").unwrap(),
                ValueType::from_str("token.aleo/token").unwrap(),
            ];
```
After
```rust
ValueType::from_str("amount.private").unwrap(),
                ValueType::from_str("token.record").unwrap(),
                ValueType::from_str("token.aleo/token.record").unwrap(),
            ];
```

## Snippet 2

Context: `console/program/src/data_types/value_type/serialize.rs:111` (changes the branch that decides whether execution stops or continues)

Before
```rust
check_serde_json(ValueType::<CurrentNetwork>::from_str("token.record").unwrap());
        check_serde_json(ValueType::<CurrentNetwork>::from_str("hello_world.record").unwrap());
        check_serde_json(ValueType::<CurrentNetwork>::from_str("hello_world.aleo/new").unwrap());
    }
```
After
```rust
check_serde_json(ValueType::<CurrentNetwork>::from_str("token.record").unwrap());
        check_serde_json(ValueType::<CurrentNetwork>::from_str("hello_world.record").unwrap());
        check_serde_json(ValueType::<CurrentNetwork>::from_str("hello_world.aleo/new.record").unwrap());
    }
```

## Snippet 3

Context: `console/program/src/data_types/value_type/serialize.rs:123` (changes the branch that decides whether execution stops or continues)

Before
```rust
check_bincode(ValueType::<CurrentNetwork>::from_str("token.record").unwrap());
        check_bincode(ValueType::<CurrentNetwork>::from_str("hello_world.record").unwrap());
        check_bincode(ValueType::<CurrentNetwork>::from_str("hello_world.aleo/new").unwrap());
    }
}
```
After
```rust
check_bincode(ValueType::<CurrentNetwork>::from_str("token.record").unwrap());
        check_bincode(ValueType::<CurrentNetwork>::from_str("hello_world.record").unwrap());
        check_bincode(ValueType::<CurrentNetwork>::from_str("hello_world.aleo/new.record").unwrap());
    }
}
```

## Snippet 4

Context: `vm/compiler/src/process/stack/mod.rs:691` (changes the branch that decides whether execution stops or continues)

Before
```rust
// If the program and function is not a special function, then ensure the i64 balance is positive.
        if !(program_id.to_string() == "stake.aleo" && function.name().to_string() == "initialize") {
            // Ensure the i64 balance matches the field balance.
            A::assert_eq(i64_balance.to_field(), field_balance);
        }
```
After
```rust
// If the program and function is not a special function, then ensure the i64 balance is positive.
        if !(program_id.to_string() == "stake.aleo" && function.name().to_string() == "initialize") {
            use circuit::{Eject, MSB};

            // Ensure the i64 balance MSB is false.
            A::assert(!i64_balance.msb());
            // Ensure the i64 balance matches the field balance.
            A::assert_eq(i64_balance.to_field(), &field_balance);
```

# Fix Pattern

Add an explicit signed-domain non-negativity circuit constraint alongside the existing field-domain consistency check.

## How It Was Fixed

In `vm/compiler/src/process/stack/mod.rs`, the patch imports `MSB` and asserts `!i64_balance.msb()` in the non-special transition branch. It preserves the `i64_balance.to_field()` versus `field_balance` equality check and adds a public `Field` injection of `field_balance.eject_value()` with an equality assertion. Test fixtures were updated to use external record type strings ending in `.record`.

# Why It Matters

1. Prevents ordinary transitions from accepting a negative net record balance.

2. Strengthens record value conservation checks in VM transition processing.

3. Keeps the claim scoped to balance accounting, not request replay or signature validation.

4. Treats `.record` fixture updates as supporting cleanup, not the security root cause.

# Evidence Notes

The strongest evidence is the added `A::assert(!i64_balance.msb())` in `vm/compiler/src/process/stack/mod.rs` after record input/output balance accumulation. Parser evidence supports that external records parse as `Locator::parse` followed by `.record`, making the related `ValueType` changes test syntax corrections. The evidence does not establish a replay, signature-validation, or parser vulnerability, and does not evaluate the preserved `stake.aleo/initialize` exception. Protocol security invariant: For non-special transitions, record balance accounting must prove that total record inputs minus total record outputs is non-negative, and that the signed integer accumulator and field accumulator represent the same balance. A transition must not be accepted merely because a negative signed balance has a matching field representation. Verification notes: The patch does not prove a request signature or replay-validation flaw. The provided evidence does not show an end-to-end exploit or accepted malicious transaction. The ValueType string changes look test-oriented and do not independently establish a security fix. The special-case behavior for `stake.aleo/initialize` is preserved and not evaluated here. No claim is made about other balance paths outside the shown stack transition logic. Supported by the added MSB assertion in the VM stack transition path. Supported by surrounding code showing record input balances are added and record output balances are subtracted before the check. External record string edits are test-only evidence and should not drive the security classification. No end-to-end exploit is shown, but the missing non-negative balance constraint is directly security-relevant in transition accounting. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-balance-nonnegativity-constraint`
Final impact type: `value-conservation-bypass`
Final confidence: `medium`
Final tags: `blockchain-core, vm, circuit-constraints, balance-accounting, value-conservation`

The supplied evidence supports retaining this as security hardening, not the original replay/signature-validation finding. The strongest patch adds an explicit circuit assertion that the signed net record balance is non-negative after record inputs are added and record outputs are subtracted, which tightens a security-sensitive value-conservation invariant in a blockchain VM. The evidence does not prove an exploitable transaction or request forgery bug, and the ValueType changes appear to be test syntax corrections.

## Security Evidence

1. Adds `A::assert(!i64_balance.msb())` in the VM stack transition balance check.
2. The assertion applies after record input balances are added and record output balances are subtracted.
3. The code already compares signed and field balance representations, and the patch strengthens that check with signed-domain non-negativity.
4. The changed path is transition processing for record balances, a security-sensitive blockchain accounting invariant.

## Missing Evidence

1. No end-to-end exploit or malicious accepted transition is shown.
2. No commit message or patch text explicitly states a security vulnerability.
3. No evidence supports replay, request forgery, or signature-validation impact.
4. The preserved `stake.aleo/initialize` exception is not evaluated.
5. The public field-balance injection change is not fully explained by the supplied evidence.

## Claim Boundaries

1. Classify as balance-accounting constraint hardening, not replay or signature validation.
2. Do not claim proven asset inflation without evidence of exploitability.
3. Do not treat the `.record` parser/test fixture edits as independent security fixes.
4. Scope the finding to non-special VM transition record-balance checks shown in the patch.
