# Root-Cause Card

## Metadata

- ID: `zksync-2019-07-09-zksync-cryptography-3833fee9c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-circuit-constraint`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `witness-account-key-binding`

## Violated Invariant

- Invariant: A proof circuit must constrain witness-supplied signer identity to the committed source account key before accepting a transfer state transition.

## Trust Boundary

- Boundary: Untrusted prover witness data crosses into the zk circuit constraints that define valid transfer execution.

## Attack Surface

- Entrypoint type: `zk_proof_witness_and_transaction_execution`
- Sensitive sink: transfer validity flags and account-state transition proof

## Impact Pattern

- Primary impact: authorization/integrity failure in proof constraints
- Secondary impact: unauthorized state transition risk if no redundant binding exists

## Short Reusable Lesson

- The circuit added an equality constraint between the operation signer public key and the source account public key, and included that boolean in transfer validity. The reusable shape is witness data used in a proof without being tied back to committed account state.
