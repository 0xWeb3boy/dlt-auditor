# Root-Cause Card

## Metadata

- ID: `oasis-core-2020-01-23-oasis-core-cryptography-d5cc58f88`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `insufficient-signature-verification`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-verification`

## Violated Invariant

- Invariant: Node registration must not accept a descriptor unless the authorized registration principal submits it and the descriptor carries signatures from the required keys it embeds. In the provided evidence, that is directly shown for the node identity key and the consensus key, with rejection of unexpected extra signers.

## Trust Boundary

- Boundary: `operator->registry`

## Attack Surface

- Entrypoint type: `registration-path`
- Sensitive sink: `node registry admission`

## Impact Pattern

- Primary impact: `unauthorized-registration`
- Secondary impact: `none`

## Short Reusable Lesson

- Node registration must not accept a descriptor unless the authorized registration principal submits it and the descriptor carries signatures from the required keys it embeds. In the provided evidence, that is directly shown for the node identity key and the consensus key, with rejection of unexpected extra signers. In this pattern, node registration validation was centered on a single accepted descriptor signer instead of requiring proof that specific security-relevant keys embedded in the descriptor had actually signed it, and the transaction authorization check was tied to the descriptor signer rather than directly to the authorized node/entity principal. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
