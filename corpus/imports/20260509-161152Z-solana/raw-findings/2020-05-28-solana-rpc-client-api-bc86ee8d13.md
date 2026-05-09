---
case_id: case_20200528_bc86ee8d13
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: rpc-client-api
source_quality: high
date: 2020-05-28
source_refs:
  - git:bc86ee8d13dcd1abc63689cf5bfcd42ef07a819a
  - "core/src/serve_repair.rs:914"
  - "core/src/serve_repair.rs:867"
  - "core/src/serve_repair.rs:907"
  - "core/src/serve_repair.rs:591"
bug_class: repair-response-gating-bypass
impact_type:
  - liveness
confidence: medium
tags:
  - blockchain-core
  - repair-service
  - orphan-repair
  - nonce-gating
  - denial-of-service
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a denial-of-service or repair-gating issue in `ServeRepair::run_orphan`. The grounded change is that a failed repair response packet construction now stops the orphan walk, and tests assert that no nonce after `UNLOCK_NONCE_SLOT` yields no response.

## Observed Patch Facts

1. In `core/src/serve_repair.rs`, the patch replaces `.expect("run_orphan packets")` with `);`.

2. In `core/src/serve_repair.rs`, the patch adds `// Giving no nonce after UNLOCK_NONCE_SLOT should return empty`.

3. In `core/src/serve_repair.rs`, the patch replaces `let rv: Vec<_> = ServeRepair::run_orphan(` with `let rv = ServeRepair::run_orphan(`.

4. In `core/src/serve_repair.rs`, the patch adds `} else {`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `core/src/window_service.rs`, `core/src/verified_vote_packets.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/window_service.rs`, `core/src/cluster_info.rs`. The strongest project-level identifiers around this patch are `run_orphan`, `ServeRepair::run_orphan`, `slot`, and `packets`.

## Before/After Behavior

Before the patch, if `repair_response_packet` returned `None`, `run_orphan` skipped pushing a packet but could still continue walking to parent slots. After the patch, the `None` case breaks the loop. Tests were updated so nonce-required no-response cases are represented as `None` instead of being unwrapped as packets.

# Root Cause

`ServeRepair::run_orphan` did not treat inability to construct a repair response packet as a terminal condition. In the supplied evidence, that matters when a slot is nonce-unlocked and the request supplies no nonce: the handler could move past that slot instead of ending with no response.

## Walkthrough

1. `ServeRepair::run_orphan` walks blockstore metadata starting at the requested orphan slot.

2. For each slot, it calls `repair_response::repair_response_packet` with a nonce only when `Shred::is_nonce_unlocked(slot)` requires one.

3. Before the fix, `None` from `repair_response_packet` only meant no packet was pushed.

4. Because the loop could still take the parent-slot branch, traversal could continue after a missing-nonce response failure.

5. The patch adds `else { break; }`, making packet-construction failure terminate the walk.

6. The tests now preserve the optional result and assert `rv.is_none()` when a nonce is expected but absent.

7. A new test covers `UNLOCK_NONCE_SLOT + 1` with no nonce and expects empty behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/serve_repair.rs | 564 | orphan repair request handler walks blockstore parent slots and constructs repair response packets |
| core/src/serve_repair.rs | 591 | new guard breaks the walk when a repair response packet cannot be created, including missing nonce cases |
| core/src/serve_repair.rs | 862 | test covers no-nonce orphan request after UNLOCK_NONCE_SLOT returning empty |
| core/src/serve_repair.rs | 873 | test helper validates nonce-required orphan responses can be absent instead of unwrapped as packets |

## Code Snippets

## Snippet 1

Context: `core/src/serve_repair.rs:914` (changes signature or replay validation logic)

Before
```rust
5,
                nonce,
            )
            .expect("run_orphan packets")
            .packets
            .iter()
            .map(|b| b.clone())
            .collect();
```
After
```rust
5,
                nonce,
            );

            if Shred::is_nonce_unlocked(slot + num_slots - 1) && nonce.is_none() {
                // If a nonce is expected but not provided, there should be no
                // response
                assert!(rv.is_none());
```

## Snippet 2

Context: `core/src/serve_repair.rs:867` (changes a sensitive control or state-update path)

Before
```rust
run_orphan(UNLOCK_NONCE_SLOT, 3, None);
        run_orphan(UNLOCK_NONCE_SLOT, 3, Some(9));
    }
```
After
```rust
run_orphan(UNLOCK_NONCE_SLOT, 3, None);
        run_orphan(UNLOCK_NONCE_SLOT, 3, Some(9));
        // Giving no nonce after UNLOCK_NONCE_SLOT should return empty
        run_orphan(UNLOCK_NONCE_SLOT + 1, 3, None);
    }
```

## Snippet 3

Context: `core/src/serve_repair.rs:907` (changes a sensitive control or state-update path)

Before
```rust
// For a orphan request for `slot + num_slots - 1`, we should return the highest shreds
            // from slots in the range [slot, slot + num_slots - 1]
            let rv: Vec<_> = ServeRepair::run_orphan(
                &recycler,
                &socketaddr_any!(),
```
After
```rust
// For a orphan request for `slot + num_slots - 1`, we should return the highest shreds
            // from slots in the range [slot, slot + num_slots - 1]
            let rv = ServeRepair::run_orphan(
                &recycler,
                &socketaddr_any!(),
```

## Snippet 4

Context: `core/src/serve_repair.rs:591` (changes a sensitive control or state-update path)

Before
```rust
if let Some(packet) = packet {
                    res.packets.push(packet);
                }
                if meta.is_parent_set() && res.packets.len() <= max_responses {
```
After
```rust
if let Some(packet) = packet {
                    res.packets.push(packet);
                } else {
                    break;
                }
                if meta.is_parent_set() && res.packets.len() <= max_responses {
```

# Fix Pattern

Terminate traversal when a gated response cannot be constructed, instead of treating the failed response as a skipped slot.

## How It Was Fixed

The implementation added a `break` when `repair_response_packet` returns `None`. The tests were changed to check the optional return value and add coverage for no-nonce requests after `UNLOCK_NONCE_SLOT`.

# Why It Matters

1. Prevents orphan repair traversal from continuing after a missing nonce condition.

2. Preserves the intended no-response behavior for nonce-unlocked repair requests.

3. The commit labels the issue as DoS, but the supplied evidence does not quantify exploitability or impact magnitude.

# Evidence Notes

Supported claims are limited to `core/src/serve_repair.rs`, specifically `ServeRepair::run_orphan`, the new `else { break; }`, and tests around nonce-unlocked no-response behavior. The evidence does not support RPC-client API, transaction decoding, signature validation, panic handling, cryptographic nonce compromise, or a measured amplification factor. Protocol security invariant: An orphan repair request that reaches a nonce-unlocked slot without the required nonce must terminate without producing a response, rather than continuing parent-slot traversal and returning older repair packets. Verification notes: Does not prove remote crash or panic; the changed behavior is response suppression, not exception handling. Does not prove transaction, RPC client API, or signature decoding involvement. Does not prove cryptographic break of the nonce itself. Does not quantify amplification factor or demonstrate an end-to-end denial-of-service exploit. Does not show behavior outside orphan repair responses in `ServeRepair::run_orphan`. Implementation evidence shows the new terminal break on `None`. Test evidence shows expected `None` response when nonce is required but absent. Security classification relies partly on the commit subject `Fix run_orphan DOS (#10290)` plus the runtime repair-path behavior. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `repair-response-gating-bypass`
Final impact type: `liveness`
Final confidence: `medium`
Final tags: `blockchain-core, repair-service, orphan-repair, nonce-gating, denial-of-service`

The supplied evidence supports a security-hardening classification rather than a confirmed security-fix. The commit subject explicitly names a run_orphan DoS, and the code change makes `ServeRepair::run_orphan` stop walking parent slots when `repair_response_packet` cannot construct a packet, with tests covering missing nonce behavior after `UNLOCK_NONCE_SLOT`. However, the patch evidence does not prove a concrete exploit, remote crash, amplification factor, or measured denial-of-service impact, so the phase-3 `security-fix` label is too strong.

## Security Evidence

1. Commit subject is `Fix run_orphan DOS (#10290)`.
2. Runtime code now breaks out of the orphan repair walk when packet construction returns `None`.
3. Tests assert no response when a nonce is expected but not supplied.
4. The changed path handles repair response packets in validator core code.

## Missing Evidence

1. No end-to-end exploit scenario is shown.
2. No evidence quantifies resource exhaustion, amplification, or network impact.
3. No proof that the issue causes validator crash, consensus failure, or cryptographic nonce compromise.
4. No broader call-path evidence proves exact exposure or attacker prerequisites.

## Claim Boundaries

1. Validate only as repair-service nonce/response gating hardening.
2. Do not claim RPC client API, snapshot, transaction decoding, or signature validation involvement.
3. Do not claim a confirmed exploitable DoS beyond the commit subject and local behavior change.
4. Do not claim cryptographic compromise of the nonce mechanism.
