# Root-Cause Card

## Metadata

- ID: `base-2026-03-29-base-transaction-processing-6c11aa61d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: EIP-8130 AA transactions should bind validation-time state lookups to the authenticated sender identity and should satisfy explicit structural and encoded-size limits before deeper processing.

## Trust Boundary

- Boundary: `transaction, batch, or proof input->execution or derivation pipeline`

## Attack Surface

- Entrypoint type: `transaction-or-batch-validation`
- Sensitive sink: `admission of work into shared network, RPC, or challenger resources`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `availability`

## Short Reusable Lesson

- EIP-8130 AA transactions should bind validation-time state lookups to the authenticated sender identity and should satisfy explicit structural and encoded-size limits before deeper processing. Validation logic in this AA transaction path relied on an implicit sender-derived lookup in at least one place and did not yet enforce all of the structural and encoded-size limits that the patched code now requires. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
