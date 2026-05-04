---
case_id: case_20211221_a427c2b20a
project: moonbeam
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
impact_type:
  - state-integrity
source_quality: medium
date: 2021-12-21
source_refs:
  - git:a427c2b20a9d9411c6b02e80e5941bc832842598
  - "pallets/author-mapping/src/lib.rs:144"
  - "pallets/author-mapping/src/tests.rs:263"
bug_class: association-integrity
confidence: medium
tags:
  - blockchain-core
  - author-mapping
  - association-integrity
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes an author-mapping state-integrity flaw. `update_association` now rejects updates when `new_author_id` already exists in `MappingWithDeposit`, returning `AlreadyAssociated` before removing the old mapping. This supports the commit message claim that users should not be able to kick other author-mapping associations, but the provided evidence does not show the full insertion path or broader impact.

## Observed Patch Facts

1. In `pallets/author-mapping/src/lib.rs`, the patch adds `ensure!(`.

2. In `pallets/author-mapping/src/tests.rs`, the patch replaces `assert_ok!(AuthorMapping::update_association(` with `assert_noop!(`.

## Project Context

The changed code sits primarily in `pallets/author-mapping/src`, `pallets/author-mapping`, which anchors the finding in the `core-logic` area of the project. Historical context from `pallets/author-mapping/src/mock.rs`, `pallets/author-mapping/src/benchmarks.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `pallets/author-mapping/src/mock.rs`, `pallets/author-mapping/src/benchmarks.rs`. The strongest project-level identifiers around this patch are `AuthorMapping::update_association`, `Origin::signed`, `TestAuthor`, and `Alice`.

## Before/After Behavior

Before the patch, the provided `update_association` snippet checked that the signed caller owned `old_author_id` and then proceeded to `MappingWithDeposit::<T>::remove(&old_author_id)` without a visible check that `new_author_id` was vacant. After the patch, it checks `MappingWithDeposit::<T>::get(&new_author_id).is_none()` and aborts with `AlreadyAssociated` before any removal. The regression test now expects an update from `Alice` to `Alice` to fail as a no-op instead of succeeding.

# Root Cause

The update path validated ownership of the source association but did not enforce, in the visible pre-patch code, that the destination author ID was unassociated before state mutation.

## Walkthrough

1. A signed caller invokes `AuthorMapping::update_association` with an old author ID and a new author ID.

2. The function loads the mapping for `old_author_id` and verifies the caller owns that source association.

3. Before the fix, the visible code then removed the old mapping without first checking whether `new_author_id` was already mapped.

4. The patch adds a destination vacancy check against `MappingWithDeposit`.

5. If the target author ID already exists, the call now fails with `AlreadyAssociated`.

6. The updated test confirms same-author rotation is rejected and leaves registration intact.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| pallets/author-mapping/src/lib.rs | 132 | runtime extrinsic `update_association` validates caller ownership and now rejects target author IDs that already have a mapping |
| pallets/author-mapping/src/lib.rs | 144 | new guard enforcing target mapping vacancy before state mutation |
| pallets/author-mapping/src/tests.rs | 259 | regression test asserting update to an already-associated author ID fails with `AlreadyAssociated` |

## Code Snippets

## Snippet 1

Context: `pallets/author-mapping/src/lib.rs:144` (changes a sensitive control or state-update path)

Before
```rust
Error::<T>::NotYourAssociation
			);

			MappingWithDeposit::<T>::remove(&old_author_id);
```
After
```rust
Error::<T>::NotYourAssociation
			);
			ensure!(
				MappingWithDeposit::<T>::get(&new_author_id).is_none(),
				Error::<T>::AlreadyAssociated
			);

			MappingWithDeposit::<T>::remove(&old_author_id);
```

## Snippet 2

Context: `pallets/author-mapping/src/tests.rs:263` (changes the branch that decides whether execution stops or continues)

Before
```rust
.build()
		.execute_with(|| {
			assert_ok!(AuthorMapping::update_association(
				Origin::signed(1),
				TestAuthor::Alice.into(),
				TestAuthor::Alice.into()
			));
			assert_eq!(
```
After
```rust
.build()
		.execute_with(|| {
			assert_noop!(
				AuthorMapping::update_association(
					Origin::signed(1),
					TestAuthor::Alice.into(),
					TestAuthor::Alice.into()
				),
```

# Fix Pattern

Add a destination uniqueness guard before mutating association storage.

## How It Was Fixed

`pallets/author-mapping/src/lib.rs` adds `ensure!(MappingWithDeposit::<T>::get(&new_author_id).is_none(), Error::<T>::AlreadyAssociated)` after the source ownership check and before removing `old_author_id`. Tests were updated to assert that updating an existing author ID to itself fails with `AlreadyAssociated`.

# Why It Matters

1. Prevents updates into an already-associated author ID.

2. Preserves uniqueness of author ID mappings.

3. Avoids removing the source mapping when the requested destination is occupied.

4. Evidence supports association state-integrity impact, not fund theft or consensus takeover.

# Evidence Notes

The strongest evidence is the implementation hunk in `pallets/author-mapping/src/lib.rs` adding the `new_author_id` vacancy check, plus the test change in `pallets/author-mapping/src/tests.rs` expecting `AlreadyAssociated` for `Alice` to `Alice`. The commit message explicitly says it prevents people from kicking other authorMapping associations. The full post-removal insertion or overwrite behavior is not provided, so displacement mechanics and impact beyond association state integrity should not be stated as confirmed. Protocol security invariant: An association update must be authorized for the source author ID and must only move to an unassociated target author ID, preserving uniqueness of `MappingWithDeposit` entries for Nimbus author IDs. Verification notes: The patch does not by itself prove fund theft or deposit loss. The patch does not prove consensus control or block production takeover. The provided evidence does not show the full post-removal insertion path, so overwrite mechanics are inferred from the added vacancy guard and commit message. The finding is limited to author ID association state integrity, not broader authentication or account authorization. Implementation guard is directly shown in the provided diff evidence. Regression test confirms occupied-target rejection for the same author ID case. No provided evidence proves fund loss, deposit theft, consensus compromise, or broader authentication bypass. Confidence is medium because the full update mutation path is not included. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `association-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, author-mapping, association-integrity, state-integrity`

The evidence supports keeping this as a security-hardening case: a signed runtime extrinsic now rejects updates to an already-associated author ID before mutating storage, matching the commit message about preventing users from kicking other author-mapping associations. The patch shows a meaningful integrity guard in a security-sensitive mapping path, but the supplied snippets do not show the full overwrite or insertion behavior needed to confidently classify it as a concrete security-fix rather than hardening.

## Security Evidence

1. Adds a guard that `new_author_id` must not already exist in `MappingWithDeposit`.
2. The guard is placed after source ownership validation and before removing the old association.
3. Regression test now expects `AlreadyAssociated` instead of allowing same-author update.
4. Commit message states the change prevents people from kicking other authorMapping associations.

## Missing Evidence

1. Full post-removal insertion or overwrite path is not shown.
2. No direct demonstration that another user's association can be displaced in the provided test snippet.
3. No evidence of fund loss, consensus takeover, or broader authorization bypass impact.

## Claim Boundaries

1. Validated only as author-mapping state-integrity hardening.
2. Do not claim deposit theft or consensus compromise from this evidence.
3. Do not claim exact exploit mechanics beyond occupied-target rejection.
4. Security-fix classification is too strong from the supplied patch alone.
