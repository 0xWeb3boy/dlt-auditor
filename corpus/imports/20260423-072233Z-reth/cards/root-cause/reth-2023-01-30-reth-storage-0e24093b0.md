# Root-Cause Card

## Metadata

- ID: `reth-2023-01-30-reth-storage-0e24093b0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-state-invariant`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The provided evidence supports a likely security-relevant protocol/state-integrity fix rather than a mere cleanup. The main demonstrated issue is that newly created empty accounts could still be recorded or persisted after Spurious Dragon state clearing should treat them as empty. The patch adds an explicit emptiness predicate, applies it only after the fork activates, and skips inserting such accounts. The storage-unwind hunk appears supportive, but the excerpts do not establish it as the primary bug on their own.
