# Validation Card

## Metadata

- ID: `scroll-2025-09-25-scroll-core-logic-b63e2473`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verifier-configuration-mismatch`

## What Confirmed The Issue

- Evidence 1: In `coordinator/internal/logic/verifier/verifier.go`, the patch replaces `func newRustCircuitConfig(cfg config.AssetConfig) *rustCircuitConfig {` with `Version uint 'json:"version"'`.
- Evidence 2: In `coordinator/internal/utils/version.go`, the patch adds `// version get the version for the chain instance`.
- Evidence 3: In `crates/libzkp/src/verifier.rs`, the patch replaces `tracing::info!("load verifier config for fork {}", cfg.fork_name);` with `tracing::info!("load verifier config for fork {} (ver {})", cfg.fork_name, cfg.version);`.

## What Could Have Invalidated It

- Compensating control 1: If the verifier has a single immutable version source or always recomputes its effective config from canonical metadata, similar refactors may be lower risk.
- Compensating control 2: Version-carriage cleanup alone is not enough; the important signal is whether the verifier previously selected config from inconsistent sources.
- Compensating control 3: The evidence supports verifier hardening, not a proven false-accept bug.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the verifier has a single immutable version source or always recomputes its effective config from canonical metadata, similar refactors may be lower risk.
- Caution 2: Version-carriage cleanup alone is not enough; the important signal is whether the verifier previously selected config from inconsistent sources.
- Caution 3: The evidence supports verifier hardening, not a proven false-accept bug.
