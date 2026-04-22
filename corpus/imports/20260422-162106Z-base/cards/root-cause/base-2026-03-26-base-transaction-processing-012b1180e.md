# Root-Cause Card

## Metadata

- ID: `base-2026-03-26-base-transaction-processing-012b1180e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proof-claim-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `claim-validation`

## Violated Invariant

- Invariant: A disputed L2 claim must be validated against the safe-head block height, and a zero-step claim at the safe head is only valid when its claimed output root equals the agreed output root.

## Trust Boundary

- Boundary: `transaction, batch, or proof input->execution or derivation pipeline`

## Attack Surface

- Entrypoint type: `transaction-or-batch-validation`
- Sensitive sink: `acceptance of a proof, signature, or derived state transition`

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `none`

## Short Reusable Lesson

- A disputed L2 claim must be validated against the safe-head block height, and a zero-step claim at the safe head is only valid when its claimed output root equals the agreed output root. The proof client relied on a weaker proxy invariant, output-root equality, instead of validating the claim against the canonical protocol state: the claimed L2 block number relative to the safe head. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
