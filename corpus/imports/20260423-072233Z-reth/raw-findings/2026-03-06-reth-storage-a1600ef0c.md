---
case_id: case_20260306_a1600ef0c
project: reth
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2026-03-06
source_refs:
  - git:a1600ef0c6b12944853dd48b68a4eaa53520859a
  - "crates/trie/trie/src/trie_cursor/masked.rs:614"
  - "crates/trie/trie/src/trie_cursor/masked.rs:124"
  - "crates/trie/trie/src/trie_cursor/masked.rs:414"
  - "crates/trie/trie/src/trie_cursor/masked.rs:589"
bug_class: proof-integrity
impact_type:
  - proof-integrity
confidence: medium
tags:
  - blockchain-core
  - trie
  - proof-generation
  - integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes `MaskedTrieCursor::mask_node` so the last surviving hashed child is cleared whenever masking removes other hashed children, even if `state_mask` still contains unhashed children. The provided code and tests support a trie-structure correctness bug that previously left a stale single hashed child in place. The commit message says this caused debug panics and invalid proofs in release builds, but the supplied evidence does not establish a concrete security vulnerability beyond that correctness/integrity claim.

## Observed Patch Facts

1. In `crates/trie/trie/src/trie_cursor/masked.rs`, the patch replaces `assert!(!node.hash_mask.is_bit_set(0));` with `assert!(node.hash_mask.is_empty(), "expected empty hash_mask, got {:?}", node.hash_ma...`.

2. In `crates/trie/trie/src/trie_cursor/masked.rs`, the patch replaces `// If all children were originally hashed (state_mask == hash_mask) and only one` with `// If only one hashed bit survived masking, clear it too. Being inside this block`.

3. In `crates/trie/trie/src/trie_cursor/masked.rs`, the patch replaces `fn test_no_match_returns_unchanged() {` with `fn test_last_hash_cleared_when_state_mask_wider_than_hash_mask() {`.

4. In `crates/trie/trie/src/trie_cursor/masked.rs`, the patch replaces `fn test_partial_mask_preserves_last_hash_when_state_mask_wider() {` with `fn test_last_hash_cleared_when_state_mask_wider() {`.

## Project Context

The changed code sits primarily in `crates/trie/trie/src/trie_cursor`, `crates/trie/trie/src`, which anchors the finding in the `storage` area of the project. Historical context from `crates/trie/trie/src/trie_cursor/subnode.rs`, `crates/trie/trie/src/trie_cursor/in_memory.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/trie/trie/src/verify.rs`, `crates/trie/trie/src/proof_v2/mod.rs`. The strongest project-level identifiers around this patch are `hashed`, `child`, `hash_mask`, and `only`.

## Before/After Behavior

Before the patch, masking could preserve a single remaining bit in `hash_mask` when `state_mask` was wider than `hash_mask`; the old test expected that surviving hash to remain. After the patch, any case where masking leaves only one hashed bit clears that last bit too, and the updated tests now require `hash_mask` and `hashes` to be empty in those scenarios.

# Root Cause

An overly narrow condition tied cleanup of the final surviving hashed child to the old `state_mask == hash_mask` case instead of the actual invariant: once masking leaves only one hashed child, that cached hash is no longer valid because the branch should collapse.

## Walkthrough

1. `mask_node` starts from `node.hash_mask` and unsets hashed child bits whose child paths are marked changed in the prefix set.

2. The changed comment and condition show the old logic only applied final-bit cleanup under a narrower `state_mask == hash_mask` assumption.

3. That left a stale single hashed child when unhashed children still existed in `state_mask` but only one hashed bit survived masking.

4. The new regression test with `state_mask` bits `0,1,5` and `hash_mask` bits `0,5` documents the missed case and now expects an empty `hash_mask` and empty `hashes`.

5. The renamed test for the wider `state_mask` case similarly changed from preserving `hash(3)` to requiring all hashes to be cleared.

6. The commit message states the resulting stale single-child branch could panic in debug builds and generate invalid proofs in release builds.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/trie/trie/src/trie_cursor/masked.rs | 99 | core branch-masking logic that updates `hash_mask`/`hashes` before branch collapse |
| crates/trie/trie/src/verify.rs | 1 | downstream state-root verification path that depends on structurally valid trie cursor output |
| crates/trie/trie/src/proof_v2/mod.rs | 1 | downstream proof-construction path whose correctness depends on valid masked branch encoding |
| crates/trie/trie/src/trie_cursor/masked.rs | 414 | regression test covering wider `state_mask` than `hash_mask` during masking |
| crates/trie/trie/src/trie_cursor/masked.rs | 591 | regression test showing the last surviving hash must be cleared to allow branch collapse |

## Code Snippets

## Snippet 1

Context: `crates/trie/trie/src/trie_cursor/masked.rs:614` (changes signature or replay validation logic)

Before
```rust
let (key, node) = cursor.seek(Nibbles::default()).unwrap().unwrap();
        assert_eq!(key, Nibbles::from_nibbles([0x1]));
        assert!(!node.hash_mask.is_bit_set(0));
        assert!(node.hash_mask.is_bit_set(3));
        assert!(!node.hash_mask.is_bit_set(7));
        assert_eq!(&*node.hashes, &[hash(3)]);
    }
```
After
```rust
let (key, node) = cursor.seek(Nibbles::default()).unwrap().unwrap();
        assert_eq!(key, Nibbles::from_nibbles([0x1]));
        assert!(node.hash_mask.is_empty(), "expected empty hash_mask, got {:?}", node.hash_mask);
        assert!(node.hashes.is_empty());
    }
```

## Snippet 2

Context: `crates/trie/trie/src/trie_cursor/masked.rs:124` (changes a sensitive control or state-update path)

Before
```rust
if new_hash_mask != original_hash_mask {
            // If all children were originally hashed (state_mask == hash_mask) and only one
            // hashed bit survived masking, clear it too. Being inside this block guarantees
            // bits were unset, so a single remaining bit means the original had more than one.
            // This handles the case where all but one child of a branch have been deleted —
            // the remaining child must be revealed to collapse the branch, so its cached hash
            // cannot be used.
```
After
```rust
if new_hash_mask != original_hash_mask {
            // If only one hashed bit survived masking, clear it too. Being inside this block
            // guarantees bits were unset, so a single remaining bit means the original had
            // more than one. This handles the case where all but one child of a branch have
            // been deleted — the remaining child must be revealed to collapse the branch, so
            // its cached hash cannot be used.
            if (new_hash_mask & TrieMask::new(new_hash_mask.get().wrapping_sub(1))).is_empty() {
```

## Snippet 3

Context: `crates/trie/trie/src/trie_cursor/masked.rs:414` (changes signature or replay validation logic)

Before
```rust
}

    #[test]
    fn test_no_match_returns_unchanged() {
```
After
```rust
}

    #[test]
    fn test_last_hash_cleared_when_state_mask_wider_than_hash_mask() {
        // Branch at [0x1] with children 0 (hashed), 1 (unhashed, state_mask only), 5 (hashed).
        // state_mask has bits 0,1,5; hash_mask has only bits 0,5.
        // Prefix set marks child 0 as changed → new_hash_mask has only bit 5.
        // Since only one hashed bit remains, it must be cleared so the branch can collapse.
```

## Snippet 4

Context: `crates/trie/trie/src/trie_cursor/masked.rs:589` (changes aggregate state or economic accounting)

Before
```rust
#[test]
    fn test_partial_mask_preserves_last_hash_when_state_mask_wider() {
        // Node at [0x1] with state_mask bits 0, 3, 7, 9 but only 0, 3, 7 hashed.
        // Prefix set marks children 0 and 7 as changed.
        // Only child 3's hash remains, but since state_mask != original_hash_mask
        // (child 9 is a non-hashed child), this is not an all-children-deleted scenario
        // and the last hash is preserved.
```
After
```rust
#[test]
    fn test_last_hash_cleared_when_state_mask_wider() {
        // Node at [0x1] with state_mask bits 0, 3, 7, 9 but only 0, 3, 7 hashed.
        // Prefix set marks children 0 and 7 as changed.
        // Only child 3's hash would remain, but since it's the last hashed bit it must
        // also be cleared — the remaining child needs to be revealed to allow branch
        // collapse.
```

# Fix Pattern

Remove a special-case guard and enforce the structural post-update invariant directly in the masking logic.

## How It Was Fixed

The code now checks only whether masking changed the hash mask and whether exactly one hashed bit remains; if so, it clears that final bit as well. Tests were updated and added to assert that `hash_mask` and `hashes` become empty in the previously missed `state_mask wider than hash_mask` cases.

# Why It Matters

1. It prevents masked trie nodes from staying in an internally inconsistent single-child branch form.

2. The commit message ties the old behavior to invalid proof generation in release builds.

3. The evidence supports a correctness and integrity issue in trie/proof-related code, but not stronger claims like memory corruption or code execution.

# Evidence Notes

Direct code evidence is limited to `crates/trie/trie/src/trie_cursor/masked.rs`. The diff shows a narrower guard was removed and tests were changed from preserving the last hash to clearing it. The strongest impact statement comes from the commit message, which says the old state produced debug panics and invalid proofs. The provided mapper context references proof and verification modules, but those modules were not changed here, so downstream impact should be treated as contextual rather than directly demonstrated by the diff. Protocol security invariant: When masking trie branches for downstream proof or state-root work, a branch must not retain a cached child hash if masking leaves only one hashed child; the remaining child must be revealed so the branch can collapse into a structurally valid form. Verification notes: The patch proves invalid proof generation and debug-only panics, not memory corruption or code execution. The evidence does not prove attacker-controlled reachability or a practical exploit path in deployed nodes. The patch alone does not prove consensus divergence or acceptance of an incorrect chain state. No confidentiality impact is shown by the changed code or tests. The diff directly supports the behavioral change in `mask_node` and the new expected test outcomes. The tests demonstrate the previously missed `state_mask wider than hash_mask` scenario. Security impact is not established beyond the commit message's claim about invalid proofs and debug panics. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `proof-integrity`
Final impact type: `proof-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, trie, proof-generation, integrity`

The patch is in trie masking logic used for proof-related state representation, and it removes a condition that previously left an invalid single-child hashed branch in place. The supplied evidence supports that this change hardens a security-sensitive integrity path by preventing structurally invalid proof material from being produced. However, the patch does not by itself prove an exploitable vulnerability, attacker reachability, or broader state corruption, so this is better retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. Commit message states the old behavior generated invalid proofs in release builds.
2. The code change removes a special-case guard and always clears the final surviving hashed bit when masking leaves only one hashed child.
3. Updated and added tests specifically change expected behavior from preserving a remaining hash to requiring empty hash state.
4. The affected subsystem is trie/proof masking logic, which is security-sensitive because proof correctness depends on structural validity.

## Missing Evidence

1. No evidence shows untrusted input or attacker-controlled reachability to this path.
2. No downstream verification or consensus failure is demonstrated in the patch itself.
3. No concrete exploit scenario, privilege impact, or acceptance of forged state is shown.

## Claim Boundaries

1. Supported claim: this hardens trie/proof integrity by preventing invalid masked branch encodings.
2. Not supported: direct state corruption, consensus compromise, or chain acceptance of false proofs.
3. Not supported: memory safety, code execution, confidentiality impact, or a proven exploitable vulnerability.
