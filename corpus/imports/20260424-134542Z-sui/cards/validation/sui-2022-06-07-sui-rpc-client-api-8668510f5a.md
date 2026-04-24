# Validation Card

## Metadata

- ID: `sui-2022-06-07-sui-rpc-client-api-8668510f5a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-integrity-hardening`

## What Confirmed The Issue

- CheckpointSummary and SignedCheckpointProposal construction now include the previous checkpoint digest.
- A helper retrieves the digest of the previous authenticated checkpoint, creating explicit checkpoint hash-linking after genesis.
- Remote checkpoint contents returned by another authority are now compared to checkpoint.checkpoint.content_digest instead of the whole checkpoint digest.
- The affected code is in checkpoint reconstruction, proposal creation, and authority checkpoint synchronization paths.

## What Could Have Invalidated It

- No demonstrated exploit path or attacker capability is provided.
- No evidence shows prior checkpoints could be forged, rewritten, or accepted despite consensus signatures.
- No test assertions are supplied showing a security regression case.
- No direct asset loss, authorization bypass, confidentiality impact, or signature bypass is shown.

## Severity Guidance

- Expected impact band: state-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Classify as security-hardening, not security-fix.
- Do not claim proven checkpoint forgery or history rewrite vulnerability.
- Do not claim RPC-client API impact; the evidence is checkpoint/consensus focused.
- Impact should be limited to state/checkpoint integrity hardening.
