# Validation Card

## Metadata

- ID: `optimism-2025-08-28-optimism-storage-2ba747f98b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-canonicality-validation`

## What Confirmed The Issue

- Adds a new guard that resolves local_safe back to its L1 source with derived_to_source(local_safe.id()).
- Checks is_canonical(chain_id, source.id()) before proceeding with reset.
- Fails closed with ManagedNodeError::ResetFailed when the source block is non-canonical.
- Patch comments explicitly tie the condition to L1 reorg handling and 'always reset to a valid state'.

## What Could Have Invalidated It

- No evidence of attacker control over the race or reorg timing.
- No proof of fund loss, privilege escalation, consensus break, or remote code execution.
- The patch does not show the full pre-patch exploitability or whether this was externally reachable beyond node-state inconsistency.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: low_or_informational

## False-Positive Cautions

- No evidence of attacker control over the race or reorg timing.
- No proof of fund loss, privilege escalation, consensus break, or remote code execution.
- The patch does not show the full pre-patch exploitability or whether this was externally reachable beyond node-state inconsistency.
