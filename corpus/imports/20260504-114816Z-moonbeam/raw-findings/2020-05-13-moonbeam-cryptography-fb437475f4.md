---
case_id: case_20200513_fb437475f4
project: moonbeam
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2020-05-13
source_refs:
  - git:fb437475f4d77d48dae2b7c544e215d4fa8da2cb
  - "pallets/mb-session/src/lib.rs:238"
  - "pallets/mb-session/src/lib.rs:310"
  - "pallets/mb-session/src/lib.rs:227"
  - "runtime/src/lib.rs:288"
bug_class: improper-authorization
impact_type:
  - unauthorized-state-mutation
  - validator-state-tampering
confidence: medium
tags:
  - blockchain-core
  - access-control
  - authorization
  - validator
  - snapshot
  - offchain-worker
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a likely authorization fix in `mb-session`: session validator and snapshot persistence changed from signed-origin calls accepting raw vectors to unsigned-origin calls carrying structured payloads and a signature parameter. The stronger replay/signature-validation thesis is not proven because the provided snippets do not show the unsigned validation or signature-checking implementation.

## Observed Patch Facts

1. In `pallets/mb-session/src/lib.rs`, the patch replaces `origin,snapshots: Vec<(T::AccountId,T::AccountId,BalanceOf<T>)>` with `origin,`.

2. In `pallets/mb-session/src/lib.rs`, the patch replaces `let selected_validators = <Module<T>>::select_validators();` with `let validators = <Module<T>>::select_validators();`.

3. In `pallets/mb-session/src/lib.rs`, the patch replaces `origin,selected_validators: Vec<T::AccountId>` with `origin,`.

4. In `runtime/src/lib.rs`, the patch replaces `type Call = Call;` with `// type Call = Call;`.

## Project Context

The changed code sits primarily in `pallets/mb-session/src`, `pallets/mb-session`, `runtime/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `runtime/src/impls.rs`, `runtime/src/constants.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/impls.rs`. The strongest project-level identifiers around this patch are `T::AccountId`, `type`, `origin`, and `T::Public`.

## Before/After Behavior

Before the patch, `persist_selected_validators` required only `ensure_signed(origin)?` and wrote the supplied `Vec<T::AccountId>` directly into `SessionValidators<T>`. `persist_snapshots` similarly required only `ensure_signed(origin)?` and persisted caller-supplied snapshot tuples. The offchain validator-selection path submitted the selected validators through a signed transaction. After the patch, both persistence calls require `ensure_none(origin)?`, accept structured payloads plus `_signature: T::Signature`, and the old signed validator submission code is commented out. Runtime wiring also removes the shown signed call/submit transaction associated types for `pallet_im_online` and adds `UnsignedPriority`.

# Root Cause

The supported root cause is an insufficient authorization boundary around session/offchain persistence dispatchables: the shown pre-patch bodies accepted any signed origin and then mutated session-related storage from caller-supplied values. The evidence does not prove a missing cryptographic verification or replay-protection bug specifically.

## Walkthrough

1. Pre-patch `persist_selected_validators` accepted a signed origin and a raw validator vector.

2. The shown body then cloned that vector directly into `SessionValidators<T>` without any additional authorization check in the provided evidence.

3. Pre-patch `persist_snapshots` also accepted a signed origin and raw snapshot tuples.

4. The shown snapshot body iterated over caller-supplied tuples and persisted them through `Self::set_snapshot`.

5. The offchain validator-selection path previously submitted a signed transaction to the same validator persistence dispatchable.

6. The patch changes both persistence calls to unsigned-origin entry points with structured payloads and a signature argument.

7. The old signed offchain validator submission path is commented out.

8. The provided evidence does not show the validation path that checks the payload or `_signature`, so claims about replay protection or signature enforcement must remain bounded.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| pallets/mb-session/src/lib.rs | 227 | dispatchable that persists selected session validators into `SessionValidators` storage |
| pallets/mb-session/src/lib.rs | 238 | dispatchable that persists account snapshot data used by the session/offchain logic |
| pallets/mb-session/src/lib.rs | 302 | offchain validator-selection path that previously submitted a signed state-changing transaction |
| runtime/src/lib.rs | 287 | runtime wiring for offchain/unsigned transaction behavior related to liveness/session components |

## Code Snippets

## Snippet 1

Context: `pallets/mb-session/src/lib.rs:238` (changes signature or replay validation logic)

Before
```rust
#[weight = 0]
		fn persist_snapshots(
			origin,snapshots: Vec<(T::AccountId,T::AccountId,BalanceOf<T>)>
		) -> DispatchResult {
			ensure_signed(origin)?;
			for s in &snapshots {
				Self::set_snapshot(&s.0,&s.1,s.2)?;
			}
```
After
```rust
#[weight = 0]
		fn persist_snapshots(
			origin,
			snapshots_payload: SnapshotsPayload<T::AccountId, T::Public, T::BlockNumber, BalanceOf<T>>,
			_signature: T::Signature
		) -> DispatchResult {
			ensure_none(origin)?;
			for s in &snapshots_payload.snapshots {
```

## Snippet 2

Context: `pallets/mb-session/src/lib.rs:310` (changes signature or replay validation logic)

Before
```rust
if (last_block_of_era - current_block_number) == validator_selection_delta {
			// Perform the validator selection
			let selected_validators = <Module<T>>::select_validators();
			// Send signed transaction to persist the new validators to the on-chain storage
			let call = Call::persist_selected_validators(selected_validators);
			let res = T::SubmitTransaction::submit_signed(call);
			if res.is_empty() {
				debug::native::info!("No local accounts found.");
```
After
```rust
if (last_block_of_era - current_block_number) == validator_selection_delta {
			// Perform the validator selection
			let validators = <Module<T>>::select_validators();
			// Send signed transaction to persist the new validators to the on-chain storage
			// let call = Call::persist_selected_validators(selected_validators);
			// let res = T::SubmitTransaction::submit_signed(call);
			// if res.is_empty() {
			// 	debug::native::info!("No local accounts found.");
```

## Snippet 3

Context: `pallets/mb-session/src/lib.rs:227` (changes signature or replay validation logic)

Before
```rust
#[weight = 0]
		fn persist_selected_validators(
			origin,selected_validators: Vec<T::AccountId>
		) -> DispatchResult {
			ensure_signed(origin)?;
			<SessionValidators<T>>::put(selected_validators.clone());
			Ok(())
		}
```
After
```rust
#[weight = 0]
		fn persist_selected_validators(
			origin,
			validators_payload: ValidatorsPayload<T::AccountId, T::Public, T::BlockNumber>,
			_signature: T::Signature
		) -> DispatchResult {
			ensure_none(origin)?;
			<SessionValidators<T>>::put(validators_payload.validators.clone());
```

## Snippet 4

Context: `runtime/src/lib.rs:288` (changes signature or replay validation logic)

Before
```rust
type AuthorityId = ImOnlineId;
	type Event = Event;
	type Call = Call;
	type SubmitTransaction = SubmitTransaction;
	type SessionDuration = SessionDuration;
	type ReportUnresponsiveness = Offences;
}
```
After
```rust
type AuthorityId = ImOnlineId;
	type Event = Event;
	// type Call = Call;
	// type SubmitTransaction = SubmitTransaction;
	type SessionDuration = SessionDuration;
	type ReportUnresponsiveness = Offences;
	type UnsignedPriority = ();
}
```

# Fix Pattern

Replace raw signed-origin state update calls with unsigned offchain payload calls that are expected to be validated before dispatch, while removing the old signed submission path.

## How It Was Fixed

`persist_selected_validators` and `persist_snapshots` were changed from `ensure_signed(origin)?` plus raw vectors to `ensure_none(origin)?` plus structured payloads and a `T::Signature` argument. State writes now use fields from those payloads. The signed offchain submission code shown for validator selection was disabled, and related runtime wiring was adjusted for unsigned behavior.

# Why It Matters

1. Session validator storage should not be writable through arbitrary signed inputs.

2. Snapshot persistence affects session/offchain state and should be restricted to validated data.

3. The patch shape is consistent with tightening access control around consensus-adjacent state.

4. Concrete exploit impact is not established by the provided evidence.

# Evidence Notes

Grounded evidence comes from `pallets/mb-session/src/lib.rs` lines 227, 238, and 302, and `runtime/src/lib.rs` line 287. Supported facts: signed-origin gates were replaced with unsigned-origin gates, raw vectors were replaced with structured payloads plus `_signature`, direct storage writes remained based on supplied payload data, and the previous signed offchain validator submission was commented out. Unsupported claims: direct signature verification, replay protection, malformed unsigned transaction rejection, production exposure, theft, slashing, or consensus takeover. Protocol security invariant: Session validator and snapshot persistence should only accept data from the intended offchain/session authority path, not arbitrary caller-supplied state updates. Verification notes: The provided patch does not show `ValidateUnsigned` or equivalent signature/replay validation logic. The `_signature` argument is unused in the shown dispatch bodies, so signature enforcement is inferred from the API shape, not directly proven. The evidence does not prove that malformed unsigned transactions are accepted by the runtime or transaction pool after the patch. The evidence does not show whether these dispatchables were exposed in production or only alpha/offchain workflows. No concrete theft, slashing, or consensus takeover impact is proven by the patch alone. No `ValidateUnsigned` or equivalent validation implementation is included in the provided evidence. The `_signature` parameter is unused in the shown dispatch bodies. Security classification depends on the shown pre-patch signed dispatchables being externally callable, which the mapper labels as dispatchables. No tests or exploit trace are provided. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-authorization`
Final impact type: `unauthorized-state-mutation, validator-state-tampering`
Final confidence: `medium`
Final tags: `blockchain-core, access-control, authorization, validator, snapshot, offchain-worker`

The evidence supports keeping this as security hardening, but not as a proven replay/signature-validation security fix. The pre-patch dispatchables accepted any signed origin and directly wrote caller-supplied validator and snapshot data into session-related storage, which is a security-sensitive authorization boundary. The patch removes that signed-origin path and changes the API toward unsigned offchain payloads with signature-bearing structures, but the provided evidence does not show the validation logic that would prove signature checking, replay prevention, or a complete fix.

## Security Evidence

1. Pre-patch persist_selected_validators used ensure_signed(origin)? and wrote the supplied validator vector to SessionValidators<T>.
2. Pre-patch persist_snapshots used ensure_signed(origin)? and persisted caller-supplied snapshot tuples.
3. The changed code affects validator/session and snapshot persistence paths, which are consensus-adjacent state.
4. The patch changes these calls to ensure_none(origin)? and structured payloads with signature parameters, removing the shown arbitrary signed-origin write path.
5. The old signed offchain submission path for selected validators was commented out.

## Missing Evidence

1. No ValidateUnsigned or equivalent transaction validation implementation is shown.
2. The provided dispatch bodies do not use the _signature parameter directly.
3. No replay-protection mechanism, nonce, block-bound check, or signature verification is shown in the supplied snippets.
4. No tests, exploit trace, advisory, or production exposure evidence is provided.

## Claim Boundaries

1. Do not claim a confirmed replay or signature-validation vulnerability from this evidence alone.
2. Do not claim concrete consensus takeover, slashing, theft, or chain halt impact.
3. Supported claim is limited to tightening authorization around session validator and snapshot persistence.
4. Classification should be security-hardening rather than confirmed security-fix.
