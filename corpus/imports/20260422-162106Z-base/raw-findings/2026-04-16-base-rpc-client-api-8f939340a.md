---
case_id: case_20260416_8f939340a
project: base
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2026-04-16
source_refs:
  - git:8f939340a8dd7e4966b0e05ad9ba7ef265f5a320
  - "crates/consensus/service/src/actors/l1_watcher/actor.rs:372"
  - "crates/consensus/service/src/actors/l1_watcher/actor.rs:196"
  - "crates/consensus/service/src/metrics/mod.rs:45"
  - "crates/consensus/service/src/actors/l1_watcher/actor.rs:169"
bug_class: insufficient-confirmation-depth
impact_type:
  - reorg-exposure
  - consensus-safety
confidence: medium
tags:
  - blockchain-core
  - consensus
  - verifier
  - l1-confirmation-depth
  - reorg-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports that this commit adds an optional verifier-specific L1 confirmation delay in the consensus L1 watcher path. Before, the watcher forwarded the latest observed L1 head directly to derivation. After, it can still publish the real head to other consumers while separately fetching and forwarding an older block at `head - verifier_l1_confs` for derivation. That is real consensus-safety-oriented hardening, but the provided snippets do not prove a prior exploitable flaw, incident, or insecure default. This should be treated as security-relevant but unproven, not a confirmed vulnerability fix.

## Observed Patch Facts

1. In `crates/consensus/service/src/actors/l1_watcher/actor.rs`, the patch replaces `#[tokio::test]` with `// ---------------------------------------------------------------------------`.

2. In `crates/consensus/service/src/actors/l1_watcher/actor.rs`, the patch replaces `// Send the head update event to all consumers.` with `// Always broadcast the real head so the sequencer's`.

3. In `crates/consensus/service/src/metrics/mod.rs`, the patch adds `#[describe("Configured verifier L1 confirmation depth")]`.

4. In `crates/consensus/service/src/actors/l1_watcher/actor.rs`, the patch replaces `let cancel = self.cancellation.clone();` with `Metrics::l1_verifier_confs_depth().set(self.verifier_l1_confs as f64);`.

## Project Context

The changed code sits primarily in `crates/consensus/service/src/actors/l1_watcher`, `crates/consensus/service/src/actors`, `crates/consensus/service/src/metrics`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `crates/consensus/service/src/actors/l1_watcher/query_processor.rs`, `crates/consensus/service/src/actors/l1_watcher/error.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/consensus/service/src/service/node.rs`, `crates/consensus/service/src/service/follow.rs`. The strongest project-level identifiers around this patch are `verifier_l1_confs`, `verifier`, `confirmation`, and `head`. Nearby tests or test-like files include `crates/consensus/service/src/actors/sequencer/tests/admin_api_impl_test.rs`, `crates/consensus/service/src/actors/sequencer/tests/actor_test.rs`.

## Before/After Behavior

Before the change, the visible L1 watcher path broadcast `head_block_info` to consumers and sent that same head to `send_new_l1_head(...)` for derivation. After the change, the watcher still broadcasts the real head on `latest_head`, but when `verifier_l1_confs > 0` and the chain height is deep enough, it computes `target = head_block_info.number - verifier_l1_confs`, fetches that older L1 block, and uses that delayed block for derivation. The patch also adds configuration wiring, metrics, startup logging, and tests for delayed-block fetch outcomes.

# Root Cause

The pre-change design did not have a separate verifier-specific confirmation-delay path in the shown head-forwarding logic; derivation received the newest observed L1 head directly. The patch introduces an optional delayed-fetch path, but the provided evidence does not prove that the earlier behavior was a vulnerability rather than a missing hardening control.

## Walkthrough

1. The commit adds a `verifier_l1_confs` setting and describes it as a confirmation depth for the verifier derivation pipeline.

2. At watcher startup, the code now records the configured depth in metrics and logs when verifier confirmation delay is enabled.

3. In the main head-processing path, the watcher still publishes the real observed head to `latest_head`.

4. The same path now conditionally computes `head_block_info.number - verifier_l1_confs` and fetches that older L1 block when the configured depth is non-zero and the head is deep enough.

5. The metrics additions track configured confirmation depth, the delayed derivation head, and delayed fetch errors.

6. The added test helper with `Default`, `None`, and `Err` responses shows the new delayed-fetch path was explicitly exercised for success and failure cases.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/consensus/service/src/actors/l1_watcher/actor.rs | 167 | initializes verifier confirmation-depth behavior and emits startup metrics/logging for the delayed-derivation mode |
| crates/consensus/service/src/actors/l1_watcher/actor.rs | 196 | critical consensus path: broadcasts the real L1 head to sequencer consumers but forwards a confirmation-delayed head to the derivation client |
| crates/consensus/service/src/metrics/mod.rs | 45 | observability for the new safety control, including configured depth, delayed derivation head, and delayed fetch failures |

## Code Snippets

## Snippet 1

Context: `crates/consensus/service/src/actors/l1_watcher/actor.rs:372` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}

    #[tokio::test]
    async fn fetch_logs_succeeds_on_first_try() {
```
After
```rust
}

    // ---------------------------------------------------------------------------
    // Configurable fetcher for verifier L1 confs tests
    // ---------------------------------------------------------------------------

    /// Response behaviour for [`ConfigurableFetcher::get_block`].
    enum GetBlockBehavior {
```

## Snippet 2

Context: `crates/consensus/service/src/actors/l1_watcher/actor.rs:196` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}
                    Some(head_block_info) => {
                        // Send the head update event to all consumers.
                        self.latest_head.send_replace(Some(head_block_info));
                        self.derivation_client.send_new_l1_head(head_block_info).await.map_err(|e| {
                            warn!(target: "l1_watcher", error = %e, "Error sending l1 head update to derivation actor");
                            L1WatcherActorError::DerivationClientError(e)
```
After
```rust
}
                    Some(head_block_info) => {
                        // Always broadcast the real head so the sequencer's
                        // DelayedL1OriginSelectorProvider can compute its own offset.
                        self.latest_head.send_replace(Some(head_block_info));

                        // Apply verifier confirmation delay: derive from
                        // `head - verifier_l1_confs` when the chain is deep enough.
```

## Snippet 3

Context: `crates/consensus/service/src/metrics/mod.rs:45` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
#[describe("Pre-built payloads discarded because the unsafe head advanced past their parent")]
    sequencer_stale_build_discarded_total: counter,
}
```
After
```rust
#[describe("Pre-built payloads discarded because the unsafe head advanced past their parent")]
    sequencer_stale_build_discarded_total: counter,
    #[describe("Configured verifier L1 confirmation depth")]
    l1_verifier_confs_depth: gauge,
    #[describe("L1 block number forwarded to derivation after verifier confirmation delay")]
    l1_verifier_derivation_head: counter,
    #[describe("Failed attempts to fetch a delayed L1 block for verifier confirmation")]
    l1_verifier_delayed_fetch_errors: counter,
```

## Snippet 4

Context: `crates/consensus/service/src/actors/l1_watcher/actor.rs:169` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
const MAX_BACKOFF: Duration = Duration::from_millis(500);

        let cancel = self.cancellation.clone();
```
After
```rust
const MAX_BACKOFF: Duration = Duration::from_millis(500);

        Metrics::l1_verifier_confs_depth().set(self.verifier_l1_confs as f64);
        if self.verifier_l1_confs > 0 {
            info!(
                target: "l1_watcher",
                verifier_l1_confs = self.verifier_l1_confs,
                "Verifier L1 confirmation delay enabled"
```

# Fix Pattern

Add a separate confirmation-aware input path for verifier derivation while preserving immediate real-head visibility for other consumers, and instrument the new delayed-fetch behavior with metrics and tests.

## How It Was Fixed

The fix wires a configurable `verifier_l1_confs` value into the consensus service and changes the L1 watcher so derivation can receive a delayed ancestor block instead of always receiving the latest observed head. It keeps the real head broadcast for other components, adds metrics and logging for the new mode, and adds tests covering delayed block fetch behavior.

# Why It Matters

1. The change affects a consensus-sensitive path that determines which L1 block derivation consumes.

2. Using a delayed ancestor can reduce exposure to reorg-prone tip data if that is an intended verifier policy.

3. The evidence shows hardening and observability work, not proof of a concrete exploit or past breakage.

4. A configurable safety control is not by itself evidence that prior behavior was insecure in practice.

# Evidence Notes

Grounded evidence is limited to the commit message and the provided snippets. The strongest direct support is the change in `crates/consensus/service/src/actors/l1_watcher/actor.rs` from directly sending `head_block_info` to derivation toward conditionally fetching `head - verifier_l1_confs` for derivation, while still publishing the real head to `latest_head`. Additional support comes from new metrics in `crates/consensus/service/src/metrics/mod.rs`, startup logging, and tests for delayed-fetch success and failure. The draft's stronger implications about an established vulnerability, exploitable consensus failure, or unsafe default are not supported by the provided evidence alone. Protocol security invariant: If verifier derivation is meant to avoid reorg-prone L1 tip data, it should be able to consume an L1 head that is delayed by a configurable confirmation depth rather than always using the freshest observed head. The provided evidence shows that behavior being added, but does not establish that violating it previously caused a concrete vulnerability. Verification notes: The patch does not prove a previously exploitable consensus split or chain takeover. The patch does not show that the default configuration was unsafe in all deployments. The patch does not prove an attacker could force profitable or durable L2 state divergence; it mainly shows reorg-safety hardening for verifier derivation. The added metrics and tests do not by themselves establish a past incident or concrete security impact. Assessment is based only on the supplied commit metadata and excerpts. No full diff, surrounding code, deployment defaults, or incident evidence was provided. The evidence supports consensus-safety hardening; it does not establish a confirmed vulnerability fix. Confidence is low because the security thesis depends on assumptions not proven by the provided snippets. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-confirmation-depth`
Final impact type: `reorg-exposure, consensus-safety`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, verifier, l1-confirmation-depth, reorg-hardening`

The supplied patch shows a real change in a consensus-sensitive verifier path: instead of always forwarding the newest observed L1 head to derivation, the watcher can now forward an older block at `head - verifier_l1_confs` while still broadcasting the real head elsewhere. That is credible security hardening against consuming reorg-prone tip data in verifier derivation. However, the evidence does not prove a concrete exploitable vulnerability, unsafe default, or prior incident, so this should be retained only as security hardening, not as a confirmed security fix.

## Security Evidence

1. The commit adds a verifier-specific L1 confirmation depth setting for derivation.
2. The watcher now conditionally derives from `head - verifier_l1_confs` instead of always using the latest head.
3. The real head is still broadcast separately, showing a deliberate split between normal visibility and safer verifier derivation behavior.
4. New metrics track verifier confirmation depth, delayed derivation head, and delayed fetch failures.
5. Added tests exercise delayed block fetch behavior and failure cases in the new path.

## Missing Evidence

1. No proof that the previous behavior was exploitable by an attacker.
2. No evidence of a demonstrated consensus split, chain takeover, or durable state divergence.
3. No evidence that the default configuration before this change was unsafe in deployment.
4. No incident report, advisory, or bug description tying this to a concrete security vulnerability.

## Claim Boundaries

1. This supports consensus-safety hardening, not a proven vulnerability remediation.
2. The evidence does not support the original `rpc-client-api` or serialization-focused framing.
3. Do not claim confirmed attacker impact or exploitation from the provided patch alone.
4. Do not claim the new option was enabled by default or that all prior deployments were insecure.
