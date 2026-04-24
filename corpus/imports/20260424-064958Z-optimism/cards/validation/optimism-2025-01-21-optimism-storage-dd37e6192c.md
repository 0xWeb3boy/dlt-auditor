# Validation Card

## Metadata

- ID: `optimism-2025-01-21-optimism-storage-dd37e6192c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-state-transition-validation`

## What Confirmed The Issue

- Rewind now requires eth.BlockID and verifies the stored sealed block hash before truncation.
- Derived-link insertion now carries an explicit invalidated hash and rejects mismatched same-height replacement.
- The DB refuses to build new state on top of an already invalidated entry.
- Traversal can now return ErrAwaitReplacementBlock, making unresolved invalidated state explicit and fail-closed.

## What Could Have Invalidated It

- No proof of external attacker reachability or control over the invalidation/rewind inputs.
- No demonstrated exploit, incident, or concrete consensus failure caused by the old behavior.
- No explicit security advisory, vulnerability reference, or attacker impact statement in the commit metadata.
- No evidence that the pre-patch behavior was exploitable beyond correctness or operator-integrity failure.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof of external attacker reachability or control over the invalidation/rewind inputs.
- No demonstrated exploit, incident, or concrete consensus failure caused by the old behavior.
- No explicit security advisory, vulnerability reference, or attacker impact statement in the commit metadata.
