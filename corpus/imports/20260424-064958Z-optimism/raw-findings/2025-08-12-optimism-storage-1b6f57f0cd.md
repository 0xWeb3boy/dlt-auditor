---
case_id: case_20250812_1b6f57f0cd
project: optimism
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
impact_type:
  - state-integrity
confidence: low
source_quality: high
date: 2025-08-12
source_refs:
  - git:1b6f57f0cd2954541c97f3d9db8f8c7cd762045a
  - "kona/crates/supervisor/core/src/reorg/task.rs:26"
  - "kona/crates/supervisor/core/src/reorg/metrics.rs:67"
  - "kona/crates/supervisor/core/src/reorg/task.rs:181"
  - "kona/crates/supervisor/core/src/reorg/task.rs:760"
bug_class: reorg-state-validation
tags:
  - blockchain
  - reorg
  - finalization
  - state-integrity
  - supervisor
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a bug fix in supervisor reorg handling for activation-block edge cases, specifically how the rewind target is chosen. It does not, by itself, establish an exploitable vulnerability or a concrete security impact.

## Observed Patch Facts

1. In `kona/crates/supervisor/core/src/reorg/task.rs`, the patch replaces `/// Sets up metrics for the reorg task` with `/// Processes reorg for a single chain`.

2. In `kona/crates/supervisor/core/src/reorg/metrics.rs`, the patch replaces `/// Records metrics for a L1 reorg processing operation.` with `pub(crate) fn record_block_depth(chain_id: ChainId, l1_depth: u64, l2_depth: u64) {`.

3. In `kona/crates/supervisor/core/src/reorg/task.rs`, the patch replaces `/// Checks if a block is canonical on L1` with `async fn find_common_ancestor(&self) -> Result<BlockInfo, ReorgHandlerError> {`.

4. In `kona/crates/supervisor/core/src/reorg/task.rs`, the patch replaces `assert_eq!(rewind_target.unwrap(), Some(finalized_state.source.id()));` with `assert_eq!(rewind_target.unwrap(), Some(finalized_state.source));`.

## Project Context

The changed code sits primarily in `kona/crates/supervisor/core/src/reorg`, `kona/crates/supervisor/core/src`, which anchors the finding in the `storage` area of the project. Historical context from `kona/crates/supervisor/core/src/reorg/handler.rs`, `kona/crates/supervisor/core/src/reorg/error.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `kona/crates/supervisor/core/src/syncnode/node.rs`, `kona/crates/supervisor/core/src/l1_watcher/watcher.rs`. The strongest project-level identifiers around this patch are `chain_id`, `B256::from`, `async`, and `reorg`.

## Before/After Behavior

Before the patch, the provided evidence does not show this path deriving a rewind bound from the finalized safety head. After the patch, `find_common_ancestor()` reads the finalized safety head, maps it back to a source block, and `find_rewind_target()` uses that ancestor while scanning backward for a canonical source block. The tests also add a finalized/future-activation canonical case.

# Root Cause

The patch suggests that rewind-target selection in activation-block reorg cases was not explicitly bounded by a finalized-derived common ancestor, making edge-case handling around canonical source selection less robust.

## Walkthrough

1. `process_chain_reorg` now loads the latest derivation state and drives per-chain reorg processing through `find_rewind_target()`.

2. `find_rewind_target()` first checks whether the latest source block is still canonical and returns without rewinding if so.

3. If the latest source is not canonical, the code now calls `find_common_ancestor()`.

4. `find_common_ancestor()` reads the finalized safety head and converts it to a source block with `derived_to_source(finalized_block.id())`.

5. The rewind search then walks backward through stored source blocks until it finds a canonical block, without going below that ancestor bound.

6. Tests add a `finalized_future_activation_canonical` scenario, indicating the fix targets activation-boundary reorg behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| kona/crates/supervisor/core/src/reorg/task.rs | 23 | per-chain reorg entrypoint that triggers rewind processing against stored derivation state |
| kona/crates/supervisor/core/src/reorg/task.rs | 130 | rewind-target selection loop that walks back source blocks until a canonical block is found |
| kona/crates/supervisor/core/src/reorg/task.rs | 181 | common-ancestor selection anchored from finalized state to bound reorg handling |

## Code Snippets

## Snippet 1

Context: `kona/crates/supervisor/core/src/reorg/task.rs:26` (changes persisted or aggregate state handling)

Before
```rust
DB: DbReader + StorageRewinder + Send + Sync + 'static,
{
    /// Sets up metrics for the reorg task
    pub(crate) fn with_metrics(self) -> Self {
        Metrics::init(self.chain_id);
        self
    }
```
After
```rust
DB: DbReader + StorageRewinder + Send + Sync + 'static,
{
    /// Processes reorg for a single chain
    pub(crate) async fn process_chain_reorg(&self) -> Result<(), ReorgHandlerError> {
        let latest_state = self.db.latest_derivation_state()?;

        // Find last valid source block for this chain
        let rewound_state = match self.find_rewind_target(latest_state).await {
```

## Snippet 2

Context: `kona/crates/supervisor/core/src/reorg/metrics.rs:67` (changes a sensitive control or state-update path)

Before
```rust
}

    /// Records metrics for a L1 reorg processing operation.
    /// Takes the result of the processing and extracts the reorg depth if successful.
    pub(crate) fn record_l1_reorg_processing(
        chain_id: ChainId,
        start_time: Instant,
        result: &Result<ReorgDepth, SupervisorError>,
```
After
```rust
}

    pub(crate) fn record_block_depth(chain_id: ChainId, l1_depth: u64, l2_depth: u64) {
        metrics::histogram!(
            Self::SUPERVISOR_REORG_L1_DEPTH,
            "chain_id" => chain_id.to_string(),
        )
        .record(l1_depth as f64);
```

## Snippet 3

Context: `kona/crates/supervisor/core/src/reorg/task.rs:181` (changes signature or replay validation logic)

Before
```rust
}

    /// Checks if a block is canonical on L1
    async fn is_block_canonical(
```
After
```rust
}

    async fn find_common_ancestor(&self) -> Result<BlockInfo, ReorgHandlerError> {
        trace!(
            target: "supervisor::reorg_handler",
            chain_id = %self.chain_id,
            "Finding common ancestor."
        );
```

## Snippet 4

Context: `kona/crates/supervisor/core/src/reorg/task.rs:760` (changes signature or replay validation logic)

Before
```rust
// Should succeed since the latest source block is still canonical
        assert!(rewind_target.is_ok());
        assert_eq!(rewind_target.unwrap(), Some(finalized_state.source.id()));
    }

    #[tokio::test]
    async fn test_is_block_canonical() {
        let canonical_hash = B256::from([1u8; 32]);
```
After
```rust
// Should succeed since the latest source block is still canonical
        assert!(rewind_target.is_ok());
        assert_eq!(rewind_target.unwrap(), Some(finalized_state.source));
    }

    #[tokio::test]
    async fn test_find_rewind_target_with_finalized_future_activation_canonical() {
        let mut mock_db = MockDb::new();
```

# Fix Pattern

Anchor recovery logic to finalized state, then perform a bounded backward search for the last canonical source block before rewinding.

## How It Was Fixed

The fix adds explicit finalized-anchored ancestor selection and uses that bound during rewind-target discovery, along with tests covering finalized and future-activation canonical cases.

# Why It Matters

1. Reorg handling decides how persisted derivation state is rewound.

2. A wrong rewind target can leave supervisor state misaligned with canonical L1 history.

3. Finalized state is a natural lower bound for safe rewind decisions.

4. The evidence shows correctness hardening, but not a proven security exploit.

# Evidence Notes

Grounded evidence is limited to the new `find_common_ancestor()` helper, the updated `find_rewind_target()` loop, the changed per-chain reorg entrypoint, and added tests in `reorg/task.rs`. The metrics changes appear supportive rather than the root fix. The supplied hunks do not demonstrate the full pre-patch failure mode end to end, and they do not prove attacker-triggerable impact, forged block acceptance, funds loss, or consensus failure. Protocol security invariant: When handling an L1 reorg, the supervisor should rewind only to a source block that is still canonical, and its search should not cross below the finalized-derived ancestor. Verification notes: The patch does not prove a remotely triggerable exploit. The patch does not prove acceptance of arbitrary forged blocks; it shows mishandling of canonical/reorg edge cases. The patch does not establish funds loss or a full consensus split from the evidence alone. The exact pre-patch failure mode at activation boundaries is inferred from the changed logic and tests, not fully demonstrated end to end. The code clearly adds finalized-based ancestor lookup in the reorg path. The tests show activation/finalized edge cases were the intended target. No direct exploit scenario or externally triggerable security impact is shown in the provided evidence. Security relevance is plausible, but not established strongly enough to keep as a confirmed or likely security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `reorg-state-validation`
Final tags: `blockchain, reorg, finalization, state-integrity, supervisor`

The patch materially tightens a security-sensitive reorg path in a blockchain supervisor by anchoring rewind decisions to the finalized safety head and bounding the backward search for a canonical source block. That is stronger than a generic reliability tweak because finalized ancestry is a trust boundary for state/canonicality decisions. The evidence still does not prove a concrete exploitable vulnerability, attacker-controlled trigger, or demonstrated corruption event, so this is best retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. `find_common_ancestor()` now derives a lower bound from the finalized safety head before rewinding.
2. `find_rewind_target()` walks backward only above that ancestor bound and stops on a canonical source block.
3. The changed logic sits in reorg/canonicality handling, which is security-sensitive for blockchain state integrity.
4. New tests target finalized and future-activation reorg edge cases, showing intentional hardening of finalization-bound behavior.

## Missing Evidence

1. No end-to-end pre-patch failure is shown causing an actual invalid state transition or consensus break.
2. No evidence shows an external attacker could reliably trigger or exploit the condition.
3. No proof of forged block acceptance, funds impact, or cross-node divergence is included in the supplied patch evidence.

## Claim Boundaries

1. Supported claim: the commit hardens finalized-bound reorg handling and reduces risk of incorrect rewind decisions.
2. Not supported: a proven exploitable vulnerability or concrete state-corruption incident.
3. Not supported: claims of arbitrary block acceptance, remote compromise, or direct financial loss from this patch alone.
