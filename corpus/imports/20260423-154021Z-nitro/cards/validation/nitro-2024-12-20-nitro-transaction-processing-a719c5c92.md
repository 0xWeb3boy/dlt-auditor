# Validation Card

## Metadata

- ID: `nitro-2024-12-20-nitro-transaction-processing-a719c5c92`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-machine-hardening`

## What Confirmed The Issue

- Evidence 1: This patch tightens express-lane transaction sequencing by binding processing to the current round and adding an explicit notifier before advancing to the next queued transaction.
- Evidence 2: Constrain a sequencing loop to the valid protocol scope and require explicit downstream acknowledgement before advancing state.

## What Could Have Invalidated It

- Compensating control 1: If a later authoritative validator rejects the same input before it can affect persistent state, similar cases may reduce to wasted work rather than a security bug.
- Compensating control 2: If the feature is disabled or only reachable in tests, classify similar cases as hardening or correctness only.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If a later authoritative validator rejects the same input before it can affect persistent state, similar cases may reduce to wasted work rather than a security bug.
- Caution 2: Do not claim fund loss or consensus breakage without evidence that the unchecked input reaches a state-changing sink.
