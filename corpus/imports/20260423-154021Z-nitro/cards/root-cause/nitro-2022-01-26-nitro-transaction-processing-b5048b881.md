# Root-Cause Card

## Metadata

- ID: `nitro-2022-01-26-nitro-transaction-processing-b5048b881`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-payment-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `payment-recipient-binding`

## Violated Invariant

- Invariant: A paid submission service should accept a transaction only when the sender's configured payment routing or pricing state authorizes this specific sequencer or ingress path.

## Trust Boundary

- Boundary: `external transaction submission->paid sequencer admission path`

## Attack Surface

- Entrypoint type: `transaction-or-message-admission`
- Sensitive sink: `accepting or serializing a transaction into a paid service queue`

## Impact Pattern

- Primary impact: `unauthorized-service-use`
- Secondary impact: `fee-bypass`

## Short Reusable Lesson

- A paid submission service should accept a transaction only when the sender's configured payment routing or pricing state authorizes this specific sequencer or ingress path. The supplied diff supports a likely security-relevant admission-control fix in the sequencer: before, the shown publish path serialized submitted transactions without an evident check that the sender's pricing configuration pointed at this sequencer; after, `preTxFilter` rejects senders whose `PreferredAggregator` is not `SequencerAddress`. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
