# Root-Cause Card

## Metadata

- ID: `nitro-2022-11-04-nitro-storage-9eb8b5709`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `preimage-source-mixing`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `single-source-of-truth-validation`

## Violated Invariant

- Invariant: Stateless validation should resolve preimages from the canonical validation context only and should not mix in live state fallbacks from unrelated sources.

## Trust Boundary

- Boundary: `proof or preimage request->stateless validator resolver`

## Attack Surface

- Entrypoint type: `proof-preimage-resolution`
- Sensitive sink: `validating proofs or state transitions from resolved preimages`

## Impact Pattern

- Primary impact: `validation-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Stateless validation should resolve preimages from the canonical validation context only and should not mix in live state fallbacks from unrelated sources. The diff shows a consistency hardening change in validator wiring and preimage sourcing, but the provided evidence does not establish a concrete vulnerability. The strongest grounded change is that the stateless preimage resolver stops consulting live trie state via `db.Node(hash)` and the staker path is rewired to use handles owned by `statelessBlockValidator`. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
