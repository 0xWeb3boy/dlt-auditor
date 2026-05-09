# Root-Cause Card

## Metadata

- ID: `solana-2021-03-11-solana-core-logic-cc38ae72e7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `writable-account-boundary-hardening`
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

The evidenced unaligned BPF loader deserialization path did not distinguish readonly from writable accounts before copying serialized output back into runtime account state. This could violate the writable-account privilege boundary if readonly deserialization skipping is enabled and no other path prevented the mutation.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch likely fixes a security-relevant writable-account boundary issue in Solana's BPF loader deserialization. The supplied evidence shows that the unaligned deserializer previously copied account fields such as lamports from the program output buffer for every non-duplicate account, with no shown writable-account condition. The patch threads a skip_ro_deserialization flag through the dispatcher and gates that copy-back path on keyed_account.is_writ...
