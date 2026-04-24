# Validation Card

## Metadata

- ID: `optimism-2025-08-28-optimism-storage-676b987dc4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-state-validation`

## What Confirmed The Issue

- Resetter::reset now resolves local_safe back to its L1 source before reuse.
- The new is_canonical(chain_id, source.id()) check aborts reset on noncanonical ancestry.
- The added behavior prevents reuse of stale derived state after an L1 reorg.
- node.rs wiring adds an L1 provider specifically to enable runtime canonicality validation.

## What Could Have Invalidated It

- No proof of attacker control or externally triggerable exploitation beyond the race window.
- No evidence of confidentiality, authentication, or authorization impact.
- No demonstrated consensus split, fund loss, or permanent corruption caused by the old behavior.
- No advisory, CVE, or explicit security statement from maintainers in the supplied material.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof of attacker control or externally triggerable exploitation beyond the race window.
- No evidence of confidentiality, authentication, or authorization impact.
- No demonstrated consensus split, fund loss, or permanent corruption caused by the old behavior.
