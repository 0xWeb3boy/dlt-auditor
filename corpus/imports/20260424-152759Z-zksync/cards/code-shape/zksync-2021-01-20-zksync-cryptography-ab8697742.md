# Code-Shape Card

## Metadata

- ID: `zksync-2021-01-20-zksync-cryptography-ab8697742`
- Bug family: `authz_and_role_gates`
- Bug class: `transaction-authentication-hardening`

## Code Shape Summary

- The transaction sender signature path rejects Ethereum signature data for CREATE2 accounts in single and batch checks, and a disabled Close transaction path returns an error instead of panicking. The reusable shape is accepting auth material that is inconsistent with the account authority model.

## Search Motifs

- CREATE2 account branch rejects provided eth_signature
- single and batch signature check paths both add auth-mode guard
- account_id extraction changed from panic to recoverable error for disabled tx type

## Typical Asymmetry

- The dangerous value originates outside the trusted state model, while the vulnerable code treats it as already canonical, authenticated, or uniquely identified.

## Patch Pattern

- Add explicit auth-mode rejection for account types that should not carry legacy signature data, and convert disabled transaction panic paths to typed errors.

## False Match Warnings

- If CREATE2 address derivation was already the only accepted authority, rejecting extra signatures may be cleanup.
- A panic in unreachable disabled transaction code is not automatically exploitable.
- Do not classify as cryptographic primitive failure without changed verification math.
