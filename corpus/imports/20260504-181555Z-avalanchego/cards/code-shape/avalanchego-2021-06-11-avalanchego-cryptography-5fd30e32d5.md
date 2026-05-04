# Code-Shape Card

## Metadata

- ID: `avalanchego-2021-06-11-avalanchego-cryptography-5fd30e32d5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-canonicalization-mismatch`

## Code Shape Summary

- Signing and verification-sensitive code used inconsistent proposer block header fields and key sources. The reusable shape is a consensus object with duplicate internal/exported fields where signing, serialization, and lookup must all bind the same canonical representation.

## Search Motifs

- signing code that clears or writes one signature field while serialization reads another
- parent or block ID lookup using exported fields when validation uses internal fields
- staking certificate private key paths split from consensus block signing paths

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- Collapse signing, parent lookup, and serialization-sensitive mutation onto the canonical internal header representation and sign with the intended staking private key.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- Pure field renames without a signed serialization boundary are likely non-security
- If tests prove both representations are normalized before signing, the mismatch may be cosmetic
- Do not infer signature forgery without evidence that verification accepted noncanonical bytes
