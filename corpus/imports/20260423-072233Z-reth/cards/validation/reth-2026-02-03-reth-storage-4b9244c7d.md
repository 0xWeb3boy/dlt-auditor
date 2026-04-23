# Validation Card

## Metadata

- ID: `reth-2026-02-03-reth-storage-4b9244c7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-trie-proof-generation`

## What Confirmed The Issue

- Evidence 1: The patch adds or restores a fail-closed check, state update, or accounting reconstruction in a security-sensitive path.
- Evidence 2: The changed path sits on a trust boundary: State/proof request inputs crossing into authenticated trie proof material returned to a verifier or caller.

## What Could Have Invalidated It

- Compensating control 1: Another mandatory validation layer already enforces the same invariant before this code can affect security-sensitive state.
- Compensating control 2: The changed branch is reachable only from trusted tests, offline tooling, or non-production maintenance flows.

## Severity Guidance

- Expected impact band: proof_integrity
- Expected severity band: medium

## False-Positive Cautions

- A proof-generation bug is not automatically a verifier acceptance bug.
- Local debug proof APIs may not cross a security boundary.
- Need evidence that ambiguous proofs are consumed by trust decisions before claiming exploitability.
