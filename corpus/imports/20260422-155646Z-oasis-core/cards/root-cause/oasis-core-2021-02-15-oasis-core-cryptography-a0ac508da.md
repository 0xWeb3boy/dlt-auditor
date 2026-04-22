# Root-Cause Card

## Metadata

- ID: `oasis-core-2021-02-15-oasis-core-cryptography-a0ac508da`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `insufficient-signature-domain-separation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `signature-domain-separation`

## Violated Invariant

- Invariant: Executor commitments and proposed-batch scheduler signatures must be bound to the specific runtime they belong to. A signature that verifies in one runtime context must not verify in another runtime context.

## Trust Boundary

- Boundary: `committee-member->consensus`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `security-sensitive consensus or registry state`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Executor commitments and proposed-batch scheduler signatures must be bound to the specific runtime they belong to. A signature that verifies in one runtime context must not verify in another runtime context. In this pattern, runtime ID was not incorporated into the signature context for the shown roothash commitment-verification paths, so the signature domain was not explicitly separated per runtime. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
