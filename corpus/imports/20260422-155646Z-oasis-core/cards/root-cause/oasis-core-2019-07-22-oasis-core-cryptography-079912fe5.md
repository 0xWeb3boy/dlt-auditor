# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-07-22-oasis-core-cryptography-079912fe5`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-signer-authorization-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signer-authorization`

## Violated Invariant

- Invariant: Storage receipt signatures accepted by compute-committee code must come from members of the current storage committee for the active epoch; signatures from non-members must be rejected before batch acceptance or proposal assembly.

## Trust Boundary

- Boundary: `peer->node`

## Attack Surface

- Entrypoint type: `p2p-message-handler`
- Sensitive sink: `security-sensitive consensus or registry state`

## Impact Pattern

- Primary impact: `unauthorized-signature-acceptance`
- Secondary impact: `none`

## Short Reusable Lesson

- Storage receipt signatures accepted by compute-committee code must come from members of the current storage committee for the active epoch; signatures from non-members must be rejected before batch acceptance or proposal assembly. In this pattern, authorization of storage receipt signers was incomplete at the compute/storage boundary: the shown code treated attached signatures as acceptable without the demonstrated enforcement that the signer belonged to the current epoch's authorized storage committee. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
