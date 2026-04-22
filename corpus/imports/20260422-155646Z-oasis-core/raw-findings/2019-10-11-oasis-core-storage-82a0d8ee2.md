---
case_id: case_20191011_82a0d8ee2
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: medium
date: 2019-10-11
source_refs:
  - git:82a0d8ee2fca74d6b478a5f7b6257b16c18b7e34
  - "runtime/src/storage/mkvs/urkel/cache/lru_cache.rs:204"
  - "runtime/src/storage/mkvs/urkel/cache/lru_cache.rs:510"
  - "runtime/src/storage/mkvs/urkel/cache/lru_cache.rs:408"
  - "runtime/src/storage/mkvs/urkel/cache/lru_cache.rs:138"
bug_class: state-integrity-hardening
impact_type:
  - integrity
confidence: medium
tags:
  - storage
  - cache
  - remote-sync
  - merkle-tree
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes a cache-management bug in the MKVS remote-sync path. The evidence shows added protection against evicting the active dereference pointer during merge, plus error handling when that protection blocks admission. The code supports a correctness/integrity fix for in-memory tree state under cache pressure, but the provided evidence does not establish a concrete security vulnerability or attacker-controlled exploit path.

## Observed Patch Facts

1. In `runtime/src/storage/mkvs/urkel/cache/lru_cache.rs`, the patch replaces `fn use_node(&mut self, ptr: NodePtrRef) -> bool {` with `fn try_commit_node(`.

2. In `runtime/src/storage/mkvs/urkel/cache/lru_cache.rs`, the patch replaces `fn commit_node(&mut self, ptr: NodePtrRef) {` with `fn use_node(&mut self, ptr: NodePtrRef) -> bool {`.

3. In `runtime/src/storage/mkvs/urkel/cache/lru_cache.rs`, the patch replaces `let mut stack: Vec<NodePtrRef> = Vec::new();` with `self.try_remove_node(ptr, None)`.

4. In `runtime/src/storage/mkvs/urkel/cache/lru_cache.rs`, the patch replaces `evicted.push(back);` with `if let Some(locked_val) = locked_val {`.

## Project Context

The changed code sits primarily in `runtime/src/storage/mkvs/urkel/cache`, `runtime/src/storage/mkvs/urkel`, which anchors the finding in the `storage` area of the project. Historical context from `runtime/src/storage/mkvs/urkel/cache/cache.rs`, `runtime/src/storage/mkvs/urkel/tree/remove.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/storage/mkvs/urkel/tree/remove.rs`, `runtime/src/storage/mkvs/urkel/tree/node.rs`. The strongest project-level identifiers around this patch are `NodePtrRef`, `borrow`, `NodeKind::Internal`, and `stack`.

## Before/After Behavior

Before the patch, the commit message says a too-small cache could evict the node being dereferenced during merge of remote results and silently corrupt the tree. After the patch, the eviction path rejects removing a locked active pointer, merged-node commit carries that locked pointer, and `remote_sync` stops keeping later merged nodes once that condition is hit; the commit message further says dereference now returns an error instead of silently corrupting the tree.

# Root Cause

Eviction and commit logic in the remote merge path did not account for the pointer currently being dereferenced, so cache pressure could remove that active node during merge.

## Walkthrough

1. `remote_sync` verifies a proof, merges a subtree, then commits merged nodes into the cache.

2. The patched call path passes the active dereference pointer into merged-node commit via `commit_merged_node(node_ref, &ptr)`.

3. `evict_for_val` now checks an optional locked value and returns `RemoveLockedError` instead of evicting that exact pointer.

4. The commit helper was changed to `try_commit_node(ptr, locked_ptr)`, showing the lock is carried through cache admission.

5. When `RemoveLockedError` occurs in `remote_sync`, later merged nodes are discarded from memory rather than forced into the cache.

6. The commit message states the remaining failure mode is now an error instead of silent tree corruption.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/storage/mkvs/urkel/tree/lookup.rs | 23 | lookup read-sync entrypoint that fetches remote proofs for a target pointer |
| runtime/src/storage/mkvs/urkel/tree/iterator.rs | 21 | iterator read-sync entrypoint that exercises the same remote proof/dereference flow |
| runtime/src/storage/mkvs/urkel/cache/lru_cache.rs | 461 | remote proof verification and subtree merge path that commits merged nodes while protecting the dereferenced pointer |
| runtime/src/storage/mkvs/urkel/cache/lru_cache.rs | 130 | LRU eviction loop updated to reject eviction of the locked active node during cache admission |
| runtime/src/storage/mkvs/urkel/cache/lru_cache.rs | 199 | node commit path changed to carry the locked pointer and stop merging instead of evicting the active dereference target |
| runtime/src/storage/mkvs/urkel/cache/lru_cache.rs | 400 | node removal/dereference path now surfaces failure rather than continuing after an unsafe eviction |

## Code Snippets

## Snippet 1

Context: `runtime/src/storage/mkvs/urkel/cache/lru_cache.rs:204` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

    fn use_node(&mut self, ptr: NodePtrRef) -> bool {
        match classify_noderef!(? ptr.borrow().node) {
            NodeKind::Internal => self.lru_internal.move_to_front(ptr),
            NodeKind::Leaf => self.lru_leaf.move_to_front(ptr),
            NodeKind::None => false,
        }
```
After
```rust
}

    fn try_commit_node(
        &mut self,
        ptr: NodePtrRef,
        locked_ptr: Option<&NodePtrRef>,
    ) -> Result<(), RemoveLockedError> {
        if !ptr.borrow().clean {
```

## Snippet 2

Context: `runtime/src/storage/mkvs/urkel/cache/lru_cache.rs:510` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

    fn commit_node(&mut self, ptr: NodePtrRef) {
        if !ptr.borrow().clean {
            panic!("urkel: commit_node called on dirty node");
        }
        if ptr.borrow().node.is_none() {
            return;
```
After
```rust
}

    fn use_node(&mut self, ptr: NodePtrRef) -> bool {
        match classify_noderef!(? ptr.borrow().node) {
            NodeKind::Internal => self.lru_internal.use_val(ptr),
            NodeKind::Leaf => self.lru_leaf.use_val(ptr),
            NodeKind::None => false,
        }
```

## Snippet 3

Context: `runtime/src/storage/mkvs/urkel/cache/lru_cache.rs:408` (changes the branch that decides whether execution stops or continues)

Before
```rust
fn remove_node(&mut self, ptr: NodePtrRef) {
        let mut stack: Vec<NodePtrRef> = Vec::new();
        stack.push(ptr);
        while !stack.is_empty() {
            let top = stack[stack.len() - 1].clone();

            if top.borrow().get_cache_extra().is_none() {
```
After
```rust
fn remove_node(&mut self, ptr: NodePtrRef) {
        self.try_remove_node(ptr, None)
            .expect("no locked pointer passed, cannot fail");
    }
```

## Snippet 4

Context: `runtime/src/storage/mkvs/urkel/cache/lru_cache.rs:138` (changes a sensitive control or state-update path)

Before
```rust
while !self.list.is_empty() && self.size + target_size > self.capacity {
                let back = (*self.list.back().get().unwrap()).item.clone();
                if self.remove(back.clone()) {
                    evicted.push(back);
```
After
```rust
while !self.list.is_empty() && self.size + target_size > self.capacity {
                let back = (*self.list.back().get().unwrap()).item.clone();
                if let Some(locked_val) = locked_val {
                    if back.as_ptr() == locked_val.as_ptr() {
                        return Err(RemoveLockedError);
                    }
                }
                if self.remove(back.clone()) {
```

# Fix Pattern

Carry the active pointer through cache admission, block eviction of that pointer, and stop or fail when capacity makes safe admission impossible.

## How It Was Fixed

The patch adds a locked-pointer check to the LRU eviction loop, refactors commit into a fallible `try_commit_node(..., locked_ptr)` path, and passes the dereferenced pointer through remote merge commit. On lock conflict, the merge stops retaining additional nodes. The commit message also states item ordering was adjusted to reduce eviction pressure on the active path and that dereference now errors instead of silently proceeding.

# Why It Matters

1. Pre-patch behavior was described as silent tree corruption under cache pressure.

2. The visible change protects consistency of the in-memory dereference path during remote merge.

3. The evidence supports a correctness/integrity hardening in a sensitive storage path, not a proven exploit.

# Evidence Notes

Direct code evidence is in `runtime/src/storage/mkvs/urkel/cache/lru_cache.rs`: `evict_for_val` returns `RemoveLockedError` when the eviction candidate matches `locked_val`; commit is refactored to `try_commit_node(ptr, locked_ptr)`; `remote_sync` calls `commit_merged_node(node_ref, &ptr)` and stops retaining later merged nodes after `RemoveLockedError`; `remove_node` now delegates to `try_remove_node(ptr, None)`. The stronger claims about silent corruption before the fix, item ordering, and dereference returning an error come from the commit message, not from the shown hunks alone. The provided evidence does not show proof-verification bypass, persistent corruption, consensus impact, or a demonstrated attacker trigger. Protocol security invariant: During remote subtree merge and dereference, cache admission must not evict the node currently being dereferenced; if capacity prevents preserving that pointer, the operation should stop or fail rather than continue with inconsistent in-memory tree state. Verification notes: The patch does not show a proof-verification bypass; proofs are still verified before merge. The patch does not prove persistent storage corruption or consensus divergence. The patch does not establish that a remote peer can reliably trigger the condition beyond inducing cache pressure in read-sync. The patch does not show confidentiality impact, privilege escalation, or code execution. Code changes clearly add a locked-pointer eviction guard. The commit message is the main evidence for the exact pre-patch failure mode. Security impact is not established beyond possible integrity relevance in this path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `state-integrity-hardening`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `storage, cache, remote-sync, merkle-tree`

The patch does not clearly prove an exploitable security vulnerability, but it does tighten behavior in a security-sensitive remote proof/merge path by preventing eviction of the actively dereferenced node and failing safely when cache pressure would otherwise cause inconsistent tree state. Given the authenticated-tree and remote-sync context, this is better treated as security hardening for integrity-sensitive state handling than as a confirmed security bug fix.

## Security Evidence

1. `remote_sync` merges a verified remote subtree and now passes the active dereference pointer into commit logic as a locked value.
2. `evict_for_val` refuses to evict the locked pointer and returns `RemoveLockedError` instead of proceeding.
3. The merge path stops retaining later merged nodes after `RemoveLockedError`, avoiding continuation after an unsafe cache-admission condition.
4. The commit message describes the prior outcome as silent tree corruption and the new behavior as returning an error instead.

## Missing Evidence

1. No patch evidence shows a concrete attacker-controlled trigger beyond cache pressure during read sync.
2. No evidence demonstrates consensus failure, persistent corruption, or proof-verification bypass.
3. No evidence shows confidentiality, privilege, or code-execution impact.
4. The strongest claim about pre-patch silent corruption comes from the commit message rather than a fully shown failing code path or test.

## Claim Boundaries

1. Supported: hardening of integrity-sensitive cache behavior during remote proof merge and dereference.
2. Supported: the fix prevents eviction of the currently dereferenced node and introduces fail-safe handling.
3. Not supported: a confirmed exploitable vulnerability with demonstrated attacker impact.
4. Not supported: broader claims such as consensus compromise or persistent state corruption.
