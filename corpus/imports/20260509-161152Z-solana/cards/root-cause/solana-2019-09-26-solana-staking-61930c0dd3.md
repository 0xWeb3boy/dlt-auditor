# Root-Cause Card

## Metadata

- ID: `solana-2019-09-26-solana-staking-61930c0dd3`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-check-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-and-signer-binding`

## Violated Invariant

- Protocol input must satisfy signature and signer binding before it can reach account owner/write privilege, executable program state, or runtime syscall side effect.

## Trust Boundary

- Boundary: untrusted program instruction/CPI frame to runtime account and privilege enforcement

## Attack Surface

- Entrypoint type: native program, loader, SBF/BPF, or CPI invocation
- Sensitive sink: account owner/write privilege, executable program state, or runtime syscall side effect

## Root Cause

The grounded root cause is an incomplete authority check in sensitive vote-program paths, especially withdrawal: authorization was tied to the vote account signer instead of the role-specific authority stored in account state. Broader stake-state changes support explicit authority roles but are not established as the root cause by the provided evidence.

## Impact Pattern

- Primary impact: unauthorized-sensitive-operation
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

The evidence supports a likely authorization fix in Solana vote/stake authority handling. The strongest supported change is in vote withdrawal: the pre-patch path only required the vote account itself to be a signer, while the patched path loads VoteState and verifies vote_state.authorized_withdrawer against the vote account and other signers. Vote processing is also moved to shared verification of vote_state.authorized_voter. The stake changes appear t...
