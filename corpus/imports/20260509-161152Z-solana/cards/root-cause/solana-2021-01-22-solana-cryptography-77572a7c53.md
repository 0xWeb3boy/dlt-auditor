# Root-Cause Card

## Metadata

- ID: `solana-2021-01-22-solana-cryptography-77572a7c53`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cpi-writable-privilege-tracking`
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

The likely root cause was that CPI post-account verification lacked explicit caller-derived writability context, allowing verification to depend on the callee message's account writability rather than the caller's effective writable privilege. This is an inference from the added caller_privileges plumbing; the supplied evidence does not show the vulnerable PreAccount::verify behavior directly.

## Impact Pattern

- Primary impact: access-control, state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch is likely a security fix for CPI writable privilege tracking. The supplied evidence shows caller account writability being captured in the BPF loader syscall path and passed into runtime account verification, but it does not include the full PreAccount::verify logic, a regression test, or a concrete exploit, so the draft's confirmed/high-confidence claim should be downgraded.
