---
case_id: case_20251209_e7bd4fb988
project: avalanchego
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2025-12-09
source_refs:
  - git:e7bd4fb988f2c04749458298c1f6b4a5b7161d5d
  - "firewood/src/merkle/mod.rs:396"
  - "firewood/src/merkle/merge.rs:40"
  - "firewood/src/iter.rs:970"
  - "firewood/src/merkle/merge.rs:168"
bug_class: range-proof-boundary-hardening
impact_type:
  - proof-verification-integrity
  - absence-proof-correctness
confidence: medium
tags:
  - blockchain-core
  - storage
  - merkle-trie
  - range-proof
  - absence-proof
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch corrects Firewood range proof generation so proof boundaries are tied to requested range bounds rather than only to the first and last yielded keys. The evidence supports an authenticated data structure correctness issue, but it does not establish that clients accepted forged or incomplete state, that an attacker could exploit the behavior, or that consensus/security impact occurred.

## Observed Patch Facts

1. In `firewood/src/merkle/mod.rs`, the patch replaces `let mut iter = match start_key {` with `// if there is a requested lower bound, the start proof must always be`.

2. In `firewood/src/merkle/merge.rs`, the patch replaces `let base_iter = match first_key {` with `let base_iter = merkle`.

3. In `firewood/src/iter.rs`, the patch replaces `let mut iter = match start {` with `let mut iter = merkle.key_value_iter_from_key(start.unwrap_or_default());`.

4. In `firewood/src/merkle/merge.rs`, the patch replaces `enum KeyRangeIter<I, K> {` with `#[derive(Debug)]`.

## Project Context

The changed code sits primarily in `firewood/src/merkle`, `firewood/src`, which anchors the finding in the `storage` area of the project. Historical context from `firewood/src/merkle/parallel.rs`, `firewood/src/manager.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `firewood/src/merkle/parallel.rs`, `firewood/src/manager.rs`. The strongest project-level identifiers around this patch are `ReturnableIterator::new`, `iter`, `None`, and `merkle`. Nearby tests or test-like files include `firewood/src/merkle/tests/range.rs`, `firewood/src/merkle/tests/proof.rs`.

## Before/After Behavior

Before the change, range proof generation used the first and last keys found during iteration as proof anchors, which could leave a requested-but-absent lower or upper bound unproven. After the change, the lower-bound proof is generated from the requested start key when present, upper-bound behavior is described as similarly corrected, and merge iteration is explicitly bounded with `stop_after_key(last_key)`. Tests were adjusted to exercise unified from-key iteration behavior.

# Root Cause

The range proof code conflated yielded trie keys with requested range boundary keys. When a requested boundary key was absent, proving only the nearest yielded key did not provide proof material for the gap between the requested bound and the returned data.

## Walkthrough

1. A caller requests a range proof with optional lower and upper bounds.

2. The pre-fix code started iteration from the lower bound but, according to the commit message, generated proofs for the first key found rather than necessarily for the requested start key.

3. If the requested start key was absent, the first yielded key could be greater than the requested lower bound.

4. That proof could authenticate returned key-values but would not prove absence for the gap between the requested start and first yielded key.

5. The commit states the upper-bound side had a similar issue when an upper bound was requested and the result set was not truncated.

6. The fix generates a start proof directly from the requested start key when present.

7. The merge iterator now starts from the requested first key or default lower bound and applies an explicit stop after the requested last key.

8. The provided evidence supports proof correctness and verification completeness, but not a demonstrated exploit path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| firewood/src/merkle/mod.rs | 390 | validates requested range and generates start/end proofs for requested bounds |
| firewood/src/merkle/merge.rs | 36 | constructs bounded merge iterator between trie data and provided key-value proof data |
| firewood/src/merkle/merge.rs | 168 | range filtering helper area changed as part of bounded iterator behavior |
| firewood/src/iter.rs | 964 | iterator behavior coverage for starting from an optional lower bound |

## Code Snippets

## Snippet 1

Context: `firewood/src/merkle/mod.rs:396` (changes bounds, limits, or capacity handling)

Before
```rust
}

        let mut iter = match start_key {
            // TODO: fix the call-site to force the caller to do the allocation
            Some(key) => self.key_value_iter_from_key(key.to_vec().into_boxed_slice()),
            None => self.key_value_iter(),
        };
```
After
```rust
}

        // if there is a requested lower bound, the start proof must always be
        // for that key even if (especially if) the key is not present in the
        // trie so that the requestor can assert no keys exist between the
        // requested key and the first provided key.
        let start_proof = start_key
            .map(|key| self.prove(key))
```

## Snippet 2

Context: `firewood/src/merkle/merge.rs:40` (changes persisted or aggregate state handling)

Before
```rust
kvp_iter: impl IntoIterator<IntoIter = I>,
    ) -> Self {
        let base_iter = match first_key {
            Some(k) => merkle.key_value_iter_from_key(k),
            None => merkle.key_value_iter(),
        };

        Self {
```
After
```rust
kvp_iter: impl IntoIterator<IntoIter = I>,
    ) -> Self {
        let base_iter = merkle
            .key_value_iter_from_key(first_key.as_ref().map(AsRef::as_ref).unwrap_or_default())
            .stop_after_key(last_key);
        Self {
            trie: ReturnableIterator::new(base_iter),
            kvp: ReturnableIterator::new(FilteredKeyRangeIter::new(kvp_iter.into_iter(), None)),
```

## Snippet 3

Context: `firewood/src/iter.rs:970` (changes persisted or aggregate state handling)

Before
```rust
}

        let mut iter = match start {
            Some(start) => merkle.key_value_iter_from_key(start.to_vec().into_boxed_slice()),
            None => merkle.key_value_iter(),
        };

        // we iterate twice because we should get a None then start over
```
After
```rust
}

        let mut iter = merkle.key_value_iter_from_key(start.unwrap_or_default());

        // we iterate twice because we should get a None then start over
```

## Snippet 4

Context: `firewood/src/merkle/merge.rs:168` (changes a sensitive control or state-update path)

Before
```rust
}

enum KeyRangeIter<I, K> {
    Unfiltered { iter: I },
    Filtered { iter: I, last_key: K },
    Exhausted,
}
```
After
```rust
}

#[derive(Debug)]
pub(super) enum EitherKey<L, R> {
```

# Fix Pattern

Bind range proof boundary proofs to caller-requested bounds, and use bounded iteration/filtering so returned key-values stay within the requested range.

## How It Was Fixed

`firewood/src/merkle/mod.rs` now computes `start_proof = start_key.map(|key| self.prove(key))`, with comments explaining that absent requested lower-bound keys still need proofs. The commit message states requested end keys are handled similarly except when truncation requires a different proof key. `firewood/src/merkle/merge.rs` now builds the trie iterator with `key_value_iter_from_key(...unwrap_or_default())` and applies `.stop_after_key(last_key)`, replacing the prior optional branch that could use an unbounded iterator.

# Why It Matters

1. Range proof verifiers need absence evidence for requested boundary gaps.

2. Absent keys at requested bounds matter for authenticated trie queries.

3. Returned key-values should be constrained to the requested range.

4. The evidence does not show client acceptance of invalid state or a concrete attack path.

# Evidence Notes

The strongest evidence is the commit message and the `firewood/src/merkle/mod.rs` change adding `start_proof = start_key.map(|key| self.prove(key))` with explanatory comments. `firewood/src/merkle/merge.rs` supports the bounded-iteration aspect through `stop_after_key(last_key)`. Claims of remote exploitability, consensus failure, or invalid state acceptance are unsupported by the provided input. Protocol security invariant: A Merkle range proof for requested bounds should provide proof material for the requested lower and upper keys, including absent boundary keys, and should only yield keys within those bounds, so a verifier can reason about absence between the requested boundary and the first or last returned key. Verification notes: The patch does not prove that invalid state could be accepted by all clients. The patch does not show a remote attack path or attacker-controlled call surface. The patch does not establish consensus impact from the provided evidence alone. The change may also be described as authenticated data structure correctness, not memory safety or access control. No commands or file inspection were performed, per instruction. Classification is based only on the supplied commit message, mapper output, draft, and excerpts. Security relevance is plausible, but vulnerability impact is not established by the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `range-proof-boundary-hardening`
Final impact type: `proof-verification-integrity, absence-proof-correctness`
Final confidence: `medium`
Final tags: `blockchain-core, storage, merkle-trie, range-proof, absence-proof, security-hardening`

The supplied evidence supports retaining this as security hardening rather than a proven vulnerability fix. The patch changes Merkle range proof generation so proofs are anchored to requested lower and upper bounds, including absent boundary keys, and bounds yielded keys to the requested range. That is security-sensitive authenticated data structure behavior, but the evidence does not prove clients accepted forged state, that an attacker could exploit the gap, or that consensus impact occurred.

## Security Evidence

1. Commit message states clients previously could not prove absence between requested bounds and yielded keys.
2. Patch generates a start proof from the requested start key even when that key is absent from the trie.
3. Patch adds bounded iteration with stop_after_key(last_key), supporting enforcement of requested range limits.
4. Changed subsystem is Merkle/range proof logic for blockchain state storage, a security-sensitive verification primitive.

## Missing Evidence

1. No proof that malformed or incomplete proofs were accepted by verifiers.
2. No demonstrated attacker-controlled call path or exploit scenario.
3. No evidence of consensus failure, state forgery, or remote impact.
4. No full verifier-side patch evidence showing changed acceptance or rejection behavior.

## Claim Boundaries

1. Classify as security hardening for proof completeness, not as a confirmed exploitable security fix.
2. Do not claim forged blockchain state acceptance from the supplied evidence.
3. Do not claim memory safety, access control, denial of service, or consensus impact.
4. The supported claim is limited to tightening Merkle range proof boundary and absence-proof correctness.
