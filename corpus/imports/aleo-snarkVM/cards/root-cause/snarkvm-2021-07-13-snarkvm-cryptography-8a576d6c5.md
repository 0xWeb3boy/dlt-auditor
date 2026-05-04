# Root-Cause Card

## Metadata

- ID: `snarkvm-2021-07-13-snarkvm-cryptography-8a576d6c5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-transcript-length-binding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `transcript-boundary-binding`

## Violated Invariant

- Invariant: A signature verifier, including its circuit form, must bind the exact byte message and all variable-length transcript boundaries before accepting a signature.

## Trust Boundary

- Boundary: prover-controlled message bytes -> in-circuit signature verifier

## Attack Surface

- Entrypoint type: zk-circuit-signature-verifier
- Sensitive sink: signature challenge hash used by the GroupEncryption verification gadget

## Impact Pattern

- Primary impact: cryptographic signature binding hardening
- Secondary impact: possible proof acceptance ambiguity if a downstream protocol depends on the gadget result

## Short Reusable Lesson

- When byte strings are mapped into field elements for signature verification, the circuit transcript should bind length and boundaries explicitly, not only the resulting field sequence.
