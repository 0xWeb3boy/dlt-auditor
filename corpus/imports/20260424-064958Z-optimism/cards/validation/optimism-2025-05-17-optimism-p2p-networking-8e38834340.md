# Validation Card

## Metadata

- ID: `optimism-2025-05-17-optimism-p2p-networking-8e38834340`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `forkchoice-sync-state`

## What Confirmed The Issue

- The commit message explicitly says safe and finalized hashes are set to B256::ZERO while the execution layer syncs.
- The patch changes forkchoice construction so unsafe payloads are no longer always reused as stronger safe/finalized markers during sync.
- The patch limits when the unsafe ref is finalized, indicating stricter handling of finality state.
- The touched code is in engine/derivation paths that control forkchoice, sync gating, and local canonical-state tracking.

## What Could Have Invalidated It

- No proof of attacker influence over the bad state transition is provided.
- No test, incident, or advisory shows consensus failure, funds risk, or privilege impact.
- No evidence shows remote exploitability or a demonstrated safety violation across nodes.
- The logging change in attributes.rs is observability only and does not itself support a security claim.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: low_or_informational

## False-Positive Cautions

- No proof of attacker influence over the bad state transition is provided.
- No test, incident, or advisory shows consensus failure, funds risk, or privilege impact.
- No evidence shows remote exploitability or a demonstrated safety violation across nodes.
