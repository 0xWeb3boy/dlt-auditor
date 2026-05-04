# Prompt Family: ZK Circuit Witness And Public Data Binding

## Use This For

- ZK rollup circuits and proof-generation code.
- Witness builders, public input builders, pubdata or calldata encoders, and verifier input construction.
- Transaction families where signatures, nonces, account keys, amounts, fees, roots, or operation arguments appear in more than one representation.

## Prompt

```text
Hunt for bugs where a proof can be generated or accepted over witness data that is not constrained to the transaction, signature, public data, or committed state that the protocol intends.

Build a field matrix for each operation family:
- external transaction object,
- SDK or wallet signed payload,
- account or storage state consumed by execution,
- witness struct fields,
- public inputs, pubdata, calldata, or event data,
- circuit allocated variables,
- validity flags and final boolean constraints,
- verifier or contract inputs.

Search patterns:
- Byte messages, signatures, commitments, or encrypted-record fields converted into field elements inside a circuit. Check that the circuit also constrains length, domain separator, and message boundaries.
- Signed or balance-like circuit values represented both as native integers and field elements. Equality in the field must be paired with explicit range, sign, or non-negativity constraints where the protocol relies on integer semantics.
- signer, account id, public key, address, token, amount, fee, nonce, recipient, or operation type appears in witness data but is not constrained equal to the committed account state or canonical transaction field.
- signature verification uses allocated or witness-provided message bytes, but the circuit does not reconstruct the canonical message from constrained transaction fields and compare them.
- nonce, chain/domain, batch hash, fee, time range, or operation type is present in SDK or transaction code but missing from witness, pubdata, or constraints.
- public data or calldata is emitted from helper fields that are not constrained to the same values used for state transition.
- validity flags are computed but not included in the final enforced boolean, or are enforced only for one chunk/branch of a multi-chunk operation.
- Merkle, accumulator, or commitment-tree membership checks whose setup, ledger construction, witness generation, and circuit constraints use different parameter objects, such as an underlying hash parameter in one layer and the full tree parameter in another.
- conditional membership, nullifier, dummy-entry, noop, or placeholder checks that are computed or present in comments but do not feed into the final enforced validity condition for every non-dummy path.
- one operation variant, legacy path, offchain path, create-account path, or batch path has weaker constraints than the normal path.
- witness builders silently fill defaults, zeroes, or derived values when required protocol fields are absent.
- circuit tests check successful proof generation but not negative cases with mismatched witness fields.

Questions to answer:
1. What exact fields authorize the operation?
2. Which fields are signed by the user or account key?
3. Which fields are read from committed state?
4. Which fields are exposed as public inputs or pubdata?
5. Where does the circuit constrain equality between all representations?
6. Are nonce, signer, account id, token, amount, fee, recipient, operation type, and domain bound on every variant?
7. Does every computed validity flag feed into the final constraint?
8. Could a prover choose one value for the signature message and another value for the state transition?
9. Could public data describe a different operation than the constrained private witness?
10. Are negative tests present for mismatched signer, nonce, pubdata, and operation arguments?
11. For Merkle or accumulator membership, do ledger setup, witness generation, and circuit allocation all use the same parameter namespace, root, path, and non-dummy gating semantics?

False-positive filters:
- Do not report a missing local equality if a shared mandatory helper enforces the same binding on all paths before final validity.
- Do not treat witness-generation refactors as security issues unless the changed field affects proof acceptance, public data, or state transition.
- Do not infer theft or forged state unless verifier acceptance and attacker-controlled witness construction are demonstrated.
- Keep likely hardening when the patch tightens circuit constraints but exploitability is not shown.

Severity guidance:
- High if unconstrained witness/signature/public-data mismatch can authorize an invalid state transition or accepted proof.
- Medium for likely hardening where a sensitive constraint is added but redundant checks or exploitability remain unclear.
- Low for tooling-only witness generation changes that cannot affect accepted proofs or public data.
```
