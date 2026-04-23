# Validation Card

## Metadata

- ID: `nitro-2023-02-24-nitro-transaction-processing-e853315fb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-version-gating`

## What Confirmed The Issue

- Evidence 1: The patch makes L2 transaction parsing version-aware across block production and reorg replay, and adds an explicit rejection of `ArbitrumExtendedTxType` when `arbOSVersion < 11`.
- Evidence 2: Thread protocol-version context from canonical state into transaction parsing and fail closed on transaction types that are not yet enabled.

## What Could Have Invalidated It

- Compensating control 1: If a later authoritative validator rejects the same input before it can affect persistent state, similar cases may reduce to wasted work rather than a security bug.
- Compensating control 2: If the feature is disabled or only reachable in tests, classify similar cases as hardening or correctness only.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If a later authoritative validator rejects the same input before it can affect persistent state, similar cases may reduce to wasted work rather than a security bug.
- Caution 2: Do not claim fund loss or consensus breakage without evidence that the unchecked input reaches a state-changing sink.
