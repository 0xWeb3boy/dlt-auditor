---
case_id: case_20250424_d16aa9e0d
project: movement
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2025-04-24
source_refs:
  - git:d16aa9e0d10a02fb6de74e9e2ed2be1afbc64ff6
  - "protocol-units/da/movement/protocol/light-node/src/sequencer.rs:413"
  - "protocol-units/da/movement/protocol/light-node/src/sequencer.rs:106"
  - "protocol-units/da/movement/protocol/prevalidator/src/lib.rs:12"
  - "protocol-units/da/movement/protocol/prevalidator/src/aptos.rs:1"
bug_class: transaction-validation-bypass
impact_type:
  - integrity
  - validation-bypass
confidence: medium
tags:
  - validator-ops
  - sequencer
  - transaction-validation
  - signature-validation
  - validation-bypass
  - whitelist-configuration
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes a no-whitelist configuration path where the DA light-node sequencer did not install or invoke the Aptos transaction prevalidator before accepting submitted transactions. The fix makes the prevalidator unconditional and treats the signer whitelist as an optional validator mode.

## Observed Patch Facts

1. In `protocol-units/da/movement/protocol/light-node/src/sequencer.rs`, the patch replaces `match &self.prevalidator {` with `match self.prevalidator.prevalidate(transaction) {`.

2. In `protocol-units/da/movement/protocol/light-node/src/sequencer.rs`, the patch replaces `let prevalidator = match whitelisted_accounts {` with `let prevalidator = Arc::new(match whitelisted_accounts {`.

3. In `protocol-units/da/movement/protocol/prevalidator/src/lib.rs`, the patch replaces `/// thiserror for validation and internal errors` with `#[derive(Debug)]`.

4. In `protocol-units/da/movement/protocol/prevalidator/src/aptos.rs`, the patch adds `//! Prevalidation of Aptos transactions.`.

## Project Context

The changed code sits primarily in `protocol-units/da/movement/protocol/light-node/src`, `protocol-units/da/movement/protocol/light-node`, `protocol-units/da/movement/protocol/prevalidator/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `protocol-units/da/movement/protocol/light-node/src/passthrough.rs`, `protocol-units/da/movement/protocol/light-node/src/manager.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `protocol-units/da/movement/protocol/light-node/src/passthrough.rs`. The strongest project-level identifiers around this patch are `whitelisted_accounts`, `prevalidator`, `match`, and `Arc::new`.

## Before/After Behavior

Before the patch, `try_from_config` created `Some(prevalidator)` only when `whitelisted_accounts` was present and used `None` otherwise; `batch_write` then branched on that optional prevalidator. After the patch, `try_from_config` always creates a `Validator`, using `with_whitelist` when configured and `new` otherwise, and `batch_write` always calls `self.prevalidator.prevalidate(transaction)` before pushing accepted transactions.

# Root Cause

Baseline transaction validation was incorrectly coupled to whitelist configuration. When no signer whitelist was configured, the sequencer also omitted the prevalidator, so the ingestion path could skip the validation step entirely in that deployment mode.

## Walkthrough

1. The sequencer reads `whitelisted_accounts` during runtime initialization.

2. Before the change, it only constructed a prevalidator for `Some(whitelisted_accounts)` and used `None` when no whitelist was configured.

3. The `batch_write` path deserialized submitted blob data into `Transaction` values.

4. Before the change, `batch_write` matched on the optional prevalidator, so no-whitelist deployments could avoid calling `prevalidate`.

5. The patch always stores an `Arc<Validator>` in the sequencer runtime.

6. The patch chooses `Validator::with_whitelist(...)` for configured whitelists and `Validator::new()` when no whitelist exists.

7. The patched `batch_write` path always calls `prevalidate(transaction)` and only accepts `Ok(Prevalidated(transaction))`.

8. Validation errors are discarded, while internal errors remain separate.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| protocol-units/da/movement/protocol/light-node/src/sequencer.rs | 89 | constructs the sequencer runtime prevalidator; changed from optional only-when-whitelist to always-present baseline validator |
| protocol-units/da/movement/protocol/light-node/src/sequencer.rs | 401 | batch_write transaction ingestion path; changed to always invoke prevalidate and discard validation failures |
| protocol-units/da/movement/protocol/prevalidator/src/aptos.rs | 1 | Aptos transaction validator that checks encoding/signature validity and optionally applies sender whitelist |
| protocol-units/da/movement/protocol/prevalidator/src/lib.rs | 6 | prevalidation result/error API used by sequencer to separate accepted transactions from validation/internal errors |

## Code Snippets

## Snippet 1

Context: `protocol-units/da/movement/protocol/light-node/src/sequencer.rs:413` (changes a sensitive control or state-update path)

Before
```rust
.map_err(|e| tonic::Status::internal(e.to_string()))?;

			match &self.prevalidator {
				Some(prevalidator) => {
					// match the prevalidated status, if validation error discard if internal error raise internal error
					match prevalidator.prevalidate(transaction).await {
						Ok(prevalidated) => {
							transactions.push(prevalidated.into_inner());
```
After
```rust
.map_err(|e| tonic::Status::internal(e.to_string()))?;

			// match the prevalidated status, if validation error discard if internal error raise internal error
			match self.prevalidator.prevalidate(transaction) {
				Ok(Prevalidated(transaction)) => {
					transactions.push(transaction);
				}
				Err(Error::Validation(e)) => {
```

## Snippet 2

Context: `protocol-units/da/movement/protocol/light-node/src/sequencer.rs:106` (changes a consensus- or validator-sensitive branch)

Before
```rust
// prevalidator
		let whitelisted_accounts = config.whitelisted_accounts()?;
		let prevalidator = match whitelisted_accounts {
			Some(whitelisted_accounts) => Some(Arc::new(Validator::new(whitelisted_accounts))),
			None => None,
		};

		Ok(Self { pass_through, memseq, prevalidator })
```
After
```rust
// prevalidator
		let whitelisted_accounts = config.whitelisted_accounts()?;
		let prevalidator = Arc::new(match whitelisted_accounts {
			Some(whitelisted_accounts) => Validator::with_whitelist(whitelisted_accounts),
			None => Validator::new(),
		});

		Ok(Self { pass_through, memseq, prevalidator })
```

## Snippet 3

Context: `protocol-units/da/movement/protocol/prevalidator/src/lib.rs:12` (changes a sensitive control or state-update path)

Before
```rust
}

/// thiserror for validation and internal errors
#[derive(thiserror::Error, Debug)]

/// A prevalidated outcome. Indicates that input of A (from the trait [PrevalidatorOperations]) is prevalidated as an instance of B, or else invalid instance.
pub struct Prevalidated<B>(B);
```
After
```rust
}

#[derive(Debug)]
/// A prevalidated outcome. Indicates that input of A (from the trait [PrevalidatorOperations]) is prevalidated as an instance of B, or else invalid instance.
pub struct Prevalidated<B>(pub B);

impl<B> Prevalidated<B> {
```

## Snippet 4

Context: `protocol-units/da/movement/protocol/prevalidator/src/aptos.rs:1` (changes signature or replay validation logic)

Before
```rust
(no before snippet captured)
```
After
```rust
//! Prevalidation of Aptos transactions.

use crate::{Error, Prevalidated};

use aptos_types::account_address::AccountAddress;
use aptos_types::transaction::SignedTransaction as AptosTransaction;
use movement_types::transaction::Transaction;
```

# Fix Pattern

Decouple mandatory baseline validation from optional policy checks. Always instantiate and invoke the validator, and place whitelist enforcement inside the validator as an optional mode.

## How It Was Fixed

`sequencer.rs` now constructs a validator in both configuration branches and calls `self.prevalidator.prevalidate(transaction)` unconditionally in `batch_write`. The prevalidation result wrapper was adjusted so the accepted transaction can be destructured as `Prevalidated(transaction)`.

# Why It Matters

1. No-whitelist deployments still need baseline transaction checks.

2. Whitelist absence should not disable the transaction validation path.

3. The evidence supports a validation bypass in one configuration mode.

4. The evidence does not establish replay, signature forgery, panic, or a proven consensus failure.

# Evidence Notes

The strongest evidence is the before/after change in `sequencer.rs`: optional prevalidator construction became unconditional validator construction, and `batch_write` now always invokes `prevalidate`. The Aptos validator context says it prevalidates transactions as correctly encoded and signed Aptos transactions with an optional whitelist, but the provided evidence does not include the full validator implementation. Claims about exact cryptographic checks should therefore remain bounded to the stated prevalidation role. Protocol security invariant: Transactions submitted through the DA light-node sequencer batch_write path should pass baseline transaction prevalidation regardless of whether an optional signer whitelist is configured. The whitelist should add sender policy, not decide whether validation runs at all. Verification notes: The provided patch does not prove an end-to-end exploit or consensus break. The evidence does not show a panic-on-malformed-input fix. The evidence does not show that whitelist enforcement itself was incorrect when a whitelist was configured. The impact is limited to configurations with no signer whitelist, based on the provided diff. The patch supports a validation bypass classification, but not a stronger claim about signature forgery or replay. Supported: no-whitelist configuration previously resulted in no installed prevalidator. Supported: patched batch_write always invokes prevalidation before accepting transactions. Supported: whitelist enforcement was optionalized inside validator construction. Not supported: end-to-end exploit, replay vulnerability, panic/DoS root cause, or consensus break. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `transaction-validation-bypass`
Final impact type: `integrity, validation-bypass`
Final confidence: `medium`
Final tags: `validator-ops, sequencer, transaction-validation, signature-validation, validation-bypass, whitelist-configuration`

The supplied patch evidence supports a security-relevant validation bypass: when no signer whitelist was configured, the sequencer previously constructed no prevalidator and the batch ingestion path could avoid prevalidation entirely. The fix makes the Aptos transaction validator unconditional and treats the whitelist as an optional policy layer. The original liveness-focused classification is too narrow and misleading; the supported issue is baseline transaction validation being skipped in one configuration mode.

## Security Evidence

1. Before the patch, `whitelisted_accounts: None` resulted in `prevalidator: None`.
2. The batch write path previously matched on `self.prevalidator`, so the no-whitelist branch could accept transactions without calling `prevalidate`.
3. After the patch, `try_from_config` always creates a `Validator`, using `Validator::new()` when no whitelist is present.
4. After the patch, `batch_write` always calls `self.prevalidator.prevalidate(transaction)` and only pushes `Ok(Prevalidated(transaction))`.
5. Provided project context describes the Aptos validator as checking correctly encoded and signed transactions, with whitelist enforcement optional.

## Missing Evidence

1. No full prevalidator implementation is provided to independently verify every validation check it performs.
2. No exploit, test case, or production incident evidence is provided.
3. No evidence proves replay, consensus failure, or signature forgery beyond the skipped validation path.

## Claim Boundaries

1. Applies to deployments with no signer whitelist configured.
2. Supports a baseline transaction validation bypass, not a proven end-to-end exploit.
3. Does not show that whitelist enforcement was broken when a whitelist was configured.
4. Does not support classifying the impact primarily as liveness failure.
