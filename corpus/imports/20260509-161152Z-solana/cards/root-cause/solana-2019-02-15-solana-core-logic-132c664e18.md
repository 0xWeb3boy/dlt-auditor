# Root-Cause Card

## Metadata

- ID: `solana-2019-02-15-solana-core-logic-132c664e18`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cross-program-state-mutation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authorization-and-privilege-check`

## Violated Invariant

- Protocol input must satisfy authorization and privilege check before it can reach account owner/write privilege, executable program state, or runtime syscall side effect.

## Trust Boundary

- Boundary: untrusted program instruction/CPI frame to runtime account and privilege enforcement

## Attack Surface

- Entrypoint type: native program, loader, SBF/BPF, or CPI invocation
- Sensitive sink: account owner/write privilege, executable program state, or runtime syscall side effect

## Root Cause

The rewards redemption path directly mutated vote-program-owned account userdata. This crossed the intended account ownership boundary, even though the supplied evidence does not prove an exploitable attack path.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Medium

## Short Reusable Lesson

The patch removes rewards-program writes to vote account userdata and adds a vote-program `clear_credits` path with an owner check. The strongest supported finding is state-integrity hardening around program ownership boundaries. The evidence does not establish reward theft, arbitrary account mutation, or consensus failure.
