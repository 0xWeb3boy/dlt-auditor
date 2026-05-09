# Root-Cause Card

## Metadata

- ID: `solana-2019-03-01-solana-staking-db825b6e26`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-check`
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

The supported issue is misplaced or implicit authorization enforcement: process_vote depended on callers, such as the native entrypoint, to enforce its signer precondition. The evidence does not prove an externally reachable bypass of that precondition in normal execution.

## Impact Pattern

- Primary impact: authorization-bypass, state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: High

## Short Reusable Lesson

The patch moves a signer check from a blanket native vote entrypoint guard into sdk/src/vote_program.rs::process_vote, immediately before VoteState is deserialized, mutated, and serialized. This is security-relevant authorization hardening, but the provided evidence does not establish that unsigned votes were accepted through the normal runtime path before the patch, because the old entrypoint already rejected unsigned keyed_accounts[0] before dispatch.
