# Root-Cause Card

## Metadata

- ID: `zksync-2019-09-03-zksync-cryptography-136c8d4e5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-message-binding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signed-message-field-binding`

## Violated Invariant

- Invariant: The message verified by a signature inside a circuit must be constrained to the same transaction fields that drive the state transition.

## Trust Boundary

- Boundary: User transaction data and prover witness serialization cross into in-circuit signature verification.

## Attack Surface

- Entrypoint type: `zk_circuit_signature_verification`
- Sensitive sink: signature-message constraints for transfer-to-new account execution

## Impact Pattern

- Primary impact: authorization integrity risk from signing one payload while executing another
- Secondary impact: proof soundness hardening for transaction serialization

## Short Reusable Lesson

- The patch reconstructs serialized transaction bits in the circuit and verifies they match allocated signature-message data for transfer-to-new. The reusable pattern is a signature verifier constrained over witness-supplied bytes without proving those bytes equal the transaction being executed.
