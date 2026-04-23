# Code-Shape Card

## Metadata

- ID: `reth-2023-11-29-reth-transaction-processing-2c5a748c5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-malleability`

## Code Shape Summary

- The evidence shows a security-relevant API split in transaction signature recovery: a new checked `recover_signer` explicitly rejects high-s signatures, while `recover_signer_unchecked` is documented as a compatibility path for old signatures. That supports hardening around the EIP-2 low-s invariant, but the provided excerpts do not establish that a previously reachable validation path was actually accepting forbidden signatures, so the vulnerability claim should be downgraded to unclear.

## Search Motifs

- Motif 1: TODO
- Motif 2: TODO
- Motif 3: TODO

## Typical Asymmetry

- TODO

## Patch Pattern

- TODO

## False Match Warnings

- TODO
