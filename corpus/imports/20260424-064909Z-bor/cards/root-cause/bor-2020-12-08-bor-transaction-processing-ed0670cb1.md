# Root-Cause Card

## Metadata

- ID: `bor-2020-12-08-bor-transaction-processing-ed0670cb1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `replay-protection and signature domain binding`

## Violated Invariant

- Invariant: Signed messages and transactions must be bound to the intended chain, domain, nonce, and execution context before they are accepted or relayed.

## Trust Boundary

- Boundary: untrusted signed payload to verifier or signer boundary

## Attack Surface

- Entrypoint type: transaction/message signature verification path
- Sensitive sink: signer recovery, authorization, or replay-protection decision

## Impact Pattern

- Primary impact: transaction-replay
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The helper layer for contract transaction creation was centered on a legacy Homestead-based signer, so convenience-generated signing options did not carry an explicit chain-specific replay-protection domain through those APIs.
