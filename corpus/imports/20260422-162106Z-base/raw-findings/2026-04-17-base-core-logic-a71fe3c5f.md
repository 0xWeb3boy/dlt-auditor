---
case_id: case_20260417_a71fe3c5f
project: base
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: core-logic
impact_type:
  - state-consistency
  - client-view-divergence
confidence: low
source_quality: medium
date: 2026-04-17
source_refs:
  - git:a71fe3c5f9a60ed179d09dad88cc14c3c12d67f1
  - "crates/proof/tee/nitro-host/src/registration.rs:146"
  - "crates/consensus/service/src/actors/l1_watcher/actor.rs:495"
  - "devnet/src/smoke.rs:178"
  - "devnet/src/l2/stack.rs:49"
bug_class: policy-enforcement-bypass
tags:
  - blockchain-core
  - consensus
  - validator
  - confirmation-depth
  - policy-enforcement
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence supports a real enforcement bug in the consensus derivation path: `verifier_l1_confs` delayed a wake-up signal, but did not actually bound L1 block reads in the provider path. That means a verifier/client could still derive from newer L1 data than configured. The patch appears to move enforcement into the fetch path itself. However, the provided material does not establish a concrete exploit, consensus break, or other demonstrated security impact, so this is best classified as security-relevant but unproven.

## Observed Patch Facts

1. In `crates/proof/tee/nitro-host/src/registration.rs`, the patch replaces `match first_rpc_error {` with `first_rpc_error.map_or(Ok(false), Err)`.

2. In `crates/consensus/service/src/actors/l1_watcher/actor.rs`, the patch replaces `/// Returns the derivation client for assertion and the watch receiver for the raw head.` with `/// Returns the derivation client, the watch receiver for the raw head, and the`.

3. In `devnet/src/smoke.rs`, the patch replaces `/// Builds and starts the devnet.` with `/// Sets the number of L1 blocks to keep distance from the L1 head for the`.

4. In `devnet/src/l2/stack.rs`, the patch adds `/// Number of L1 blocks to keep distance from the L1 head for the client (validator)`.

## Project Context

The changed code sits primarily in `crates/proof/tee/nitro-host/src`, `crates/proof/tee/nitro-host`, `crates/consensus/service/src/actors/l1_watcher`, which anchors the finding in the `core-logic` area of the project. Historical context from `crates/consensus/service/src/actors/l1_watcher/query_processor.rs`, `crates/consensus/service/src/actors/l1_watcher/error.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/consensus/service/src/actors/l1_watcher/query_processor.rs`, `crates/consensus/service/src/actors/l1_watcher/error.rs`. The strongest project-level identifiers around this patch are `head`, `watch::Receiver`, `derivation`, and `watch`. Nearby tests or test-like files include `crates/consensus/service/src/actors/sequencer/tests/admin_api_impl_test.rs`, `crates/consensus/service/src/actors/sequencer/tests/actor_test.rs`.

## Before/After Behavior

Before the fix, `verifier_l1_confs` only delayed the L1 head signal sent to derivation, while the pipeline could still fetch L1 blocks directly without an upper bound. After the fix, the commit says a `ConfDepthProvider` enforces a cutoff based on the observed L1 head and configured depth, and requests beyond that cutoff fail temporarily with `BlockNotFound`.

# Root Cause

The confirmation-depth policy was applied at a signaling/scheduling boundary instead of the actual L1 block access boundary. Because the provider API remained uncapped, direct reads could bypass the intended `verifier_l1_confs` limit.

## Walkthrough

1. The commit message explicitly states the pre-fix bug: the derivation actor's wake-up signal was delayed, but `AlloyChainProvider` still fetched L1 blocks with no upper bound.

2. The same message describes the remediation: a `ConfDepthProvider` intercepts `block_info_by_number` and returns a temporary `BlockNotFound` when the requested block is beyond `l1_head - conf_depth`.

3. The supplied `l1_watcher` test helper change shows new shared `Arc<AtomicU64>` head tracking, which is consistent with the commit's description that real L1 head state now feeds enforcement.

4. The devnet configuration additions in `devnet/src/l2/stack.rs` and `devnet/src/smoke.rs` support that `verifier_l1_confs` became an explicit runtime/test configuration for this path.

5. The `crates/proof/tee/nitro-host/src/registration.rs` change is only a `match` to `map_or` rewrite and does not support the consensus claim.

6. The evidence supports an ineffective-policy-enforcement bug, but not a proven attacker-controlled exploit or concrete security failure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/consensus/providers/src/conf_depth.rs | 1 | Provider wrapper that enforces the L1 confirmation-depth cutoff and rejects over-limit block fetches |
| crates/consensus/providers/src/pipeline.rs | 1 | Derivation pipeline path that reads L1 blocks and now must respect the capped provider view |
| crates/consensus/service/src/actors/l1_watcher/actor.rs | 1 | L1 watcher path that maintains the shared real L1 head used to compute the fetch upper bound |
| crates/consensus/service/src/service/node.rs | 1 | Node/service wiring that propagates `verifier_l1_confs` into the verifier derivation setup |
| crates/consensus/service/tests/actors/verifier_conf_depth.rs | 1 | Regression test coverage for verifier lag and confirmation-depth enforcement |

## Code Snippets

## Snippet 1

Context: `crates/proof/tee/nitro-host/src/registration.rs:146` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

        match first_rpc_error {
            Some(e) => Err(e),
            None => Ok(false),
        }
    }
```
After
```rust
}

        first_rpc_error.map_or(Ok(false), Err)
    }
```

## Snippet 2

Context: `crates/consensus/service/src/actors/l1_watcher/actor.rs:495` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
/// Build and run an [`L1WatcherActor`] to completion (stream ends → `StreamEnded`).
    ///
    /// Returns the derivation client for assertion and the watch receiver for the raw head.
    async fn run_actor<F: L1BlockFetcher>(
        fetcher: F,
        head_blocks: Vec<BlockInfo>,
        verifier_l1_confs: u64,
    ) -> (RecordingDerivationClient, watch::Receiver<Option<BlockInfo>>) {
```
After
```rust
/// Build and run an [`L1WatcherActor`] to completion (stream ends → `StreamEnded`).
    ///
    /// Returns the derivation client, the watch receiver for the raw head, and the
    /// shared atomic holding the L1 head number.
    async fn run_actor<F: L1BlockFetcher>(
        fetcher: F,
        head_blocks: Vec<BlockInfo>,
        verifier_l1_confs: u64,
```

## Snippet 3

Context: `devnet/src/smoke.rs:178` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

    /// Builds and starts the devnet.
    pub async fn build(self) -> Result<Devnet> {
```
After
```rust
}

    /// Sets the number of L1 blocks to keep distance from the L1 head for the
    /// client (validator) node's derivation pipeline.
    pub const fn with_verifier_l1_confs(mut self, confs: u64) -> Self {
        self.verifier_l1_confs = confs;
        self
    }
```

## Snippet 4

Context: `devnet/src/l2/stack.rs:49` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
/// When set, the client will forward transactions to builder RPC endpoints.
    pub tx_forwarding_config: Option<TxForwardingConfig>,
}
```
After
```rust
/// When set, the client will forward transactions to builder RPC endpoints.
    pub tx_forwarding_config: Option<TxForwardingConfig>,
    /// Number of L1 blocks to keep distance from the L1 head for the client (validator)
    /// consensus node's derivation pipeline.
    pub verifier_l1_confs: u64,
}
```

# Fix Pattern

Move policy enforcement from an upstream signal to the lowest data-access boundary, using current shared state to compute an allowed range and rejecting out-of-policy reads with a temporary error.

## How It Was Fixed

According to the commit body, the fix adds a provider wrapper that checks requested L1 block numbers against `observed_l1_head - conf_depth`, and the L1 watcher now publishes the real head into shared atomic state used by the derivation pipeline. Supporting changes plumb `verifier_l1_confs` through service/devnet configuration and add or adjust regression coverage around the behavior.

# Why It Matters

1. A configured confirmation-depth delay was not actually enforced on L1 reads before this patch.

2. Verifier/client derivation could consume newer L1 data than operators likely intended.

3. Applying the check at the provider boundary closes the described bypass more directly than delaying a wake-up signal alone.

4. The supplied evidence does not show stronger impact than incorrect enforcement of the configured lag policy.

# Evidence Notes

The strongest evidence is the commit body itself, which directly describes both the bug and the fix. The provided code excerpts only partially corroborate that description: they show shared head-state plumbing in the watcher tests and config propagation in devnet, but they do not include the actual `ConfDepthProvider` or derivation pipeline diff. Because the critical enforcement code is described rather than shown in the supplied excerpts, confidence should not be higher than medium. The TEE `map_or` change is unrelated support noise and should be excluded from the finding. Protocol security invariant: When `verifier_l1_confs` is configured, the verifier/client derivation path should not read L1 blocks newer than the configured confirmation-depth cutoff derived from the observed L1 head. Verification notes: The patch shows enforcement of a confirmation-depth policy, not a proven consensus split or finalized-state corruption. The provided evidence does not prove a remote exploit, theft, or concrete economic impact. The bug is scoped to verifier/client derivation reading L1 data too close to the head; it does not show that builder or sequencer logic was equivalently broken. The `crates/proof/tee/nitro-host/src/registration.rs` change appears stylistic and does not support the security claim. The provided excerpts do not include the actual contents of `crates/consensus/providers/src/conf_depth.rs` or `crates/consensus/providers/src/pipeline.rs`. The main bug/fix narrative comes from the commit message, not a direct code snippet of the enforcement logic. No supplied evidence demonstrates exploitation, consensus divergence, finalized-state corruption, or financial impact. The devnet and test changes mainly support configuration and regression coverage, not independent proof of security impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `policy-enforcement-bypass`
Final tags: `blockchain-core, consensus, validator, confirmation-depth, policy-enforcement`

The supplied material supports that a configured confirmation-depth safeguard for verifier/client derivation was not actually enforced at the L1 block fetch boundary, and the change was intended to enforce that cutoff directly. Because this is consensus-path logic in a blockchain client, tightening that boundary is security-relevant hardening. However, the provided excerpts do not show the core enforcement diff itself, and they do not prove attacker exploitability, consensus failure, or financial impact, so this should be kept only as a security-hardening case rather than a confirmed security-fix.

## Security Evidence

1. Commit body states that `verifier_l1_confs` delayed a wake-up signal but did not bound direct L1 block fetches.
2. Commit body states that a `ConfDepthProvider` now rejects reads beyond `l1_head - conf_depth`, which is a direct enforcement change.
3. `l1_watcher` test plumbing adds shared `Arc<AtomicU64>` head tracking, consistent with runtime enforcement of a head-based cutoff.
4. Devnet/config changes add and propagate `verifier_l1_confs` specifically for the validator/client derivation pipeline.

## Missing Evidence

1. The supplied excerpts do not include the actual `crates/consensus/providers/src/conf_depth.rs` enforcement logic.
2. The patch evidence does not demonstrate an exploit, attacker influence, or concrete consensus/economic damage.
3. Most shown code is test/config plumbing rather than the decisive provider-boundary fix.

## Claim Boundaries

1. Supported: a confirmation-depth policy in a consensus-sensitive path was previously ineffective and is now enforced more directly.
2. Not supported: a proven exploitable vulnerability, theft risk, finalized-state corruption, or demonstrated consensus split.
3. Scope is limited to verifier/client derivation behavior; equivalent impact on builder or sequencer logic is not shown.
4. The TEE `registration.rs` `map_or` change is unrelated and should not be used to justify the security claim.
