# Code-Shape Card

## Metadata

- ID: `zksync-2019-07-09-zksync-cryptography-3833fee9c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-circuit-constraint`

## Code Shape Summary

- The circuit added an equality constraint between the operation signer public key and the source account public key, and included that boolean in transfer validity. The reusable shape is witness data used in a proof without being tied back to committed account state.

## Search Motifs

- CircuitPubkey::equals added between op signer and account pubkey
- valid_flags push newly computed authorization equality
- witness signer field compared to committed account state

## Typical Asymmetry

- The dangerous value originates outside the trusted state model, while the vulnerable code treats it as already canonical, authenticated, or uniquely identified.

## Patch Pattern

- Add an explicit circuit equality check tying witness signer data to account state and feed the resulting boolean into the operation validity constraint set.

## False Match Warnings

- Do not count formatting-only circuit changes.
- If the same equality was already enforced in another mandatory constraint, the patch may be refactor or defense-in-depth.
- No liveness or malformed-input claim follows from a missing equality constraint alone.
