# Signature Canonicalization And Duplicate Persistence

## Family Objective

Find bugs where cryptographic validity is checked correctly, but later duplicate, conflict, slashability, persistence, replay, or finalization logic compares raw bytes or incomplete identity instead of canonical semantic signer/message/proof identity.

## Hunt Steps

1. Enumerate all signed, attested, certified, or proof-bearing objects. Include transactions, votes, vote extensions, aggregate votes, checkpoint signatures, bridge attestations, validator-set updates, slashing evidence, execution payload approvals, and operator registrations.
2. For each object, write a semantic identity tuple: signer or prover, signed message, domain, chain, height, round, block hash/root, validator set or epoch, object type, and any fork or feature context.
3. Write a byte identity tuple: signature bytes, encoded public key, serialized vote/proof bytes, aggregate root, envelope bytes, and persistence key.
4. Search for algorithms or dependencies where multiple valid byte encodings may represent the same semantic identity: ECDSA high/low-S variants, recoverable-signature `v` variants, DER/raw conversion, compressed/uncompressed public keys, alternative proof encodings, or equivalent serialized envelopes.
5. Trace every duplicate/conflict check after initial verification. Look for raw byte comparisons, signature-byte inequality, root-only uniqueness, aggregate-root uniqueness, serialized-object equality, or database keys missing signer/message context.
6. Compare proposal validation, block finalization, replay, recovery, state sync, slashing, and query/export paths. A semantic duplicate rejected in one path must not become a raw-byte conflict or persistent duplicate in another.
7. If the code claims the library canonicalizes, locate the exact canonicalization or rejection point and verify all paths use it before persistence and finalization.
8. Design the smallest proof: two byte-different but valid signatures or proofs for the same semantic object, inserted through the earliest untrusted path that reaches the duplicate/conflict sink.
9. Check whether the duplicate causes:
  - finalization or block import failure,
  - proposal rejection loop,
  - missed duplicate evidence or slashability,
  - duplicated voting power or quorum accounting,
  - retained useless state,
  - replay or cleanup failure.

## Candidate Requirements

For every candidate, include:

- signed or proof-bearing object;
- semantic identity tuple;
- byte identity tuple;
- verifier or cryptographic library used;
- where alternate encodings are accepted or not canonicalized;
- duplicate, conflict, persistence, or finalization sink;
- exact attacker-controlled path to introduce both encodings;
- impact and a minimal canonicalization test.

## False-Positive Controls

- Do not report malleability if all untrusted paths reject non-canonical encodings before application logic sees them.
- Do not report byte-different signatures without a downstream duplicate, conflict, persistence, accounting, or liveness consequence.
- Do not assume one duplicate check covers all sinks; prove the exact sink being claimed uses semantic identity.
- Treat dependency behavior as unknown until a source check, documentation reference, or tiny test establishes acceptance or rejection of alternate encodings.
