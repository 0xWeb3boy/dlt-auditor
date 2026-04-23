# Validation Card

## Metadata

- ID: `nitro-2022-01-26-nitro-transaction-processing-b5048b881`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-payment-validation`

## What Confirmed The Issue

- Evidence 1: The supplied diff supports a likely security-relevant admission-control fix in the sequencer: before, the shown publish path serialized submitted transactions without an evident check that the sender's pricing configuration pointed at this sequencer; after, `preTxFilter` rejects senders whose `PreferredAggregator` is not `SequencerAddress`.
- Evidence 2: Add an explicit authorization/payment-routing check at the service ingress point, then propagate rejection state through downstream encoding and consumption paths instead of assuming all submitted inputs are valid.

## What Could Have Invalidated It

- Compensating control 1: If a later authoritative validator rejects the same input before it can affect persistent state, similar cases may reduce to wasted work rather than a security bug.
- Compensating control 2: If the feature is disabled or only reachable in tests, classify similar cases as hardening or correctness only.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: If a later authoritative validator rejects the same input before it can affect persistent state, similar cases may reduce to wasted work rather than a security bug.
- Caution 2: Do not claim fund loss or consensus breakage without evidence that the unchecked input reaches a state-changing sink.
