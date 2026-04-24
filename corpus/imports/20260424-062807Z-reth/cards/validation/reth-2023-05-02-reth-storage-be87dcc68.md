# Validation Card

## Metadata

- ID: `reth-2023-05-02-reth-storage-be87dcc68`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-target-mismatch`

## What Confirmed The Issue

- Resume logic changed from accepting any saved checkpoint to accepting only one whose target_block == to_block.
- Fresh rebuild path now clears the persisted execution checkpoint before clearing trie tables, removing stale checkpoint/trie combinations.

## What Could Have Invalidated It

- No proof that a remote peer or attacker could intentionally trigger the stale-checkpoint condition
- No test, incident report, or reproduction showing invalid state roots, bad block acceptance, or consensus divergence before the fix

## Severity Guidance

- Expected impact band: state_or_proof_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that a remote peer or attacker could intentionally trigger the stale-checkpoint condition
- No test, incident report, or reproduction showing invalid state roots, bad block acceptance, or consensus divergence before the fix
