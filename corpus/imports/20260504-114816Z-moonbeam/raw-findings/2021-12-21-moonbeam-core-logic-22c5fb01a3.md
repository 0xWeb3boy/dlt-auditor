---
case_id: case_20211221_22c5fb01a3
project: moonbeam
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
bug_class: state-corruption
impact_type:
  - state-integrity
confidence: high
source_quality: medium
tags:
  - blockchain-core
  - core-logic
  - state-corruption
  - state-integrity
date: 2021-12-21
source_refs:
  - git:22c5fb01a357b007be05a5647814e3ec5f5a1ce3
  - "pallets/author-mapping/src/lib.rs:146"
  - "pallets/author-mapping/src/tests.rs:232"
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes an authorization/state-integrity flaw in the author-mapping pallet. `update_association` already checked that the signer owned `old_author_id`, but it did not check whether caller-supplied `new_author_id` was already present in `MappingWithDeposit` before inserting. The added guard rejects occupied targets with `AlreadyAssociated`, preventing a valid owner of one association from replacing another existing author mapping.

## Observed Patch Facts

1. In `pallets/author-mapping/src/lib.rs`, the patch adds `ensure!(`.

2. In `pallets/author-mapping/src/tests.rs`, the patch replaces `//TODO Test ideas in case we bring back the narc extrinsic` with `#[test]`.

## Project Context

The changed code sits primarily in `pallets/author-mapping/src`, `pallets/author-mapping`, which anchors the finding in the `core-logic` area of the project. Historical context from `pallets/author-mapping/src/mock.rs`, `pallets/author-mapping/src/migrations.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `pallets/author-mapping/src/mock.rs`, `pallets/author-mapping/src/migrations.rs`. The strongest project-level identifiers around this patch are `account`, `narced`, `period`, and `ExtBuilder::default`.

## Before/After Behavior

Before the patch, `update_association` loaded `stored_info` for `old_author_id`, verified the signer matched `stored_info.account`, and then inserted that info under `new_author_id` without a visible occupied-target check. After the patch, it first ensures `MappingWithDeposit::<T>::get(&new_author_id).is_none()` and fails with `Error::<T>::AlreadyAssociated` if the target author ID is already registered.

# Root Cause

The source ownership check was necessary but incomplete. The extrinsic authorized the caller based on ownership of the old association, then allowed mutation of an arbitrary destination key without verifying that the destination key was free.

## Walkthrough

1. A signed caller invokes `update_association` with an owned `old_author_id` and a chosen `new_author_id`.

2. The function retrieves the stored registration for `old_author_id`.

3. The existing check confirms the signer owns that source registration.

4. Before the fix, the function then inserted the source registration under `new_author_id` directly.

5. If `new_author_id` was already present, that insert could replace or disrupt the existing target association.

6. The patch adds a pre-insert check requiring the target key to be absent.

7. Occupied targets now fail with `AlreadyAssociated` before storage is mutated.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| pallets/author-mapping/src/lib.rs | 134 | update_association extrinsic validates signer ownership of old_author_id and mutates MappingWithDeposit for the requested new_author_id |
| pallets/author-mapping/src/lib.rs | 146 | new guard rejects rotation when new_author_id is already associated |
| pallets/author-mapping/src/tests.rs | 232 | regression coverage for rotation behavior around existing author registration |

## Code Snippets

## Snippet 1

Context: `pallets/author-mapping/src/lib.rs:146` (changes a sensitive control or state-update path)

Before
```rust
Error::<T>::NotYourAssociation
			);

			MappingWithDeposit::<T>::insert(&new_author_id, &stored_info);
```
After
```rust
Error::<T>::NotYourAssociation
			);
			ensure!(
				MappingWithDeposit::<T>::get(&new_author_id).is_none(),
				Error::<T>::AlreadyAssociated
			);

			MappingWithDeposit::<T>::insert(&new_author_id, &stored_info);
```

## Snippet 2

Context: `pallets/author-mapping/src/tests.rs:232` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

//TODO Test ideas in case we bring back the narc extrinsic
// unstaked account can be narced after period
// unstaked account cannot be narced before period
// staked account can be narced after period
// staked account cannot be narced before period
```
After
```rust
}

#[test]
fn rotating_to_the_same_author_id_leaves_registration_in_tact() {
	ExtBuilder::default()
		.with_balances(vec![(1, 1000)])
		.with_mappings(vec![(TestAuthor::Alice.into(), 1)])
		.build()
```

# Fix Pattern

Check destination-key availability before writing caller-controlled state into a shared mapping. Ownership of the source object does not authorize overwriting an already-owned destination object.

## How It Was Fixed

The implementation adds an `ensure!` in `pallets/author-mapping/src/lib.rs` inside `update_association`, immediately before `MappingWithDeposit::<T>::insert(&new_author_id, &stored_info)`. The guard requires `MappingWithDeposit::<T>::get(&new_author_id).is_none()` and returns `Error::<T>::AlreadyAssociated` otherwise. Rust tests were also updated around rotation behavior, though the supplied evidence does not include the full test assertions.

# Why It Matters

1. Prevents one association owner from overwriting another occupied author ID.

2. Preserves integrity of `MappingWithDeposit` entries during rotation.

3. Enforces authorization on both the source association and the requested destination.

4. Evidence does not support stronger claims such as fund theft, balance manipulation, or consensus failure.

# Evidence Notes

The strongest evidence is the added guard in `pallets/author-mapping/src/lib.rs` within `update_association`: before the patch, the shown code inserted into `MappingWithDeposit` after only the source ownership check; after the patch, it rejects an already-associated `new_author_id`. The commit message says it prevents people from kicking other authorMapping associations. The provided test hunk supports regression coverage but does not show enough detail to rely on exact assertions. No specific TypeScript test hunk is provided. Protocol security invariant: A caller who owns one author mapping may update that mapping only to an unoccupied author ID; the operation must not overwrite an author ID that is already associated with another registration. Verification notes: The patch does not prove funds can be stolen or balances directly manipulated. The patch does not show consensus failure or chain-wide safety violation by itself. The patch does not prove exploitability beyond the ability to overwrite or disrupt an occupied author-mapping entry through update_association. The TypeScript test changes are listed in the commit files but no specific hunk evidence is provided here. Confirmed from supplied diff context that the new guard is in the mutation path before insertion. Confirmed from supplied context that the pre-existing authorization check covered `old_author_id` ownership, not target occupancy. Did not rely on unprovided TypeScript test details. Kept impact limited to mapping overwrite/disruption; no broader chain or financial impact is established by the evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`

The supplied patch evidence supports a concrete authorization/state-integrity fix. `update_association` already verified ownership of the source author ID, but before this patch it inserted caller-controlled `stored_info` at `new_author_id` without checking whether that destination mapping was already occupied. The added `AlreadyAssociated` guard directly prevents overwriting or displacing another author-mapping association, matching the commit subject. Broader claims such as fund theft or consensus failure are not supported, but the core security claim is supported.

## Security Evidence

1. Signed update path checks caller owns `old_author_id` but previously did not check destination occupancy.
2. Patch adds `MappingWithDeposit::<T>::get(&new_author_id).is_none()` before insertion.
3. Failure mode uses `Error::<T>::AlreadyAssociated`, indicating occupied destination IDs are now rejected.
4. Commit message explicitly says it prevents people from kicking other authorMapping associations.

## Missing Evidence

1. Full regression test assertions are not included in the supplied evidence.
2. No evidence shows financial loss, balance theft, or chain-wide consensus failure.
3. No TypeScript test hunk is provided despite the file being listed in the commit.

## Claim Boundaries

1. Supported impact is limited to unauthorized overwrite or disruption of author-mapping state.
2. Do not claim direct fund theft or balance manipulation from this evidence.
3. Do not claim consensus failure unless additional project-specific evidence shows author mapping disruption has that effect.
