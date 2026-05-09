# Root-Cause Card

## Metadata

- ID: `solana-2021-01-09-solana-staking-4470afceaa`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `authority-model-hardening`
- Confidence tier: `tier_b_likely`

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

No exploitable root cause is demonstrated by the provided evidence. The most grounded pre-patch gap is that the shown SetAuthority path did not include explicit Buffer-state authority handling, while the patch adds Buffer authority semantics and immutable-buffer rejection. The write helper changes appear to be support/refactor for separating byte mutation from caller-side authorization, not evidence of an independent vulnerability.

## Impact Pattern

- Primary impact: access-control
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The evidence supports a BPF upgradeable loader change that adds explicit Buffer authority handling and immutable-buffer rejection, with related CLI routing for setting buffer authority. It does not support the heuristic baseline's staking, panic, denial-of-service, or consensus claims. This may be security-relevant authority-model work, but the vulnerability thesis is not established from the supplied hunks.
