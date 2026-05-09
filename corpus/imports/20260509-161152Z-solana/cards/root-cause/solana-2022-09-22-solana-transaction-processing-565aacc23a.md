# Root-Cause Card

## Metadata

- ID: `solana-2022-09-22-solana-transaction-processing-565aacc23a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-account-mutability-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `account-mutability-enforcement`

## Violated Invariant

- Protocol input must satisfy account mutability enforcement before it can reach account owner/write privilege, executable program state, or runtime syscall side effect.

## Trust Boundary

- Boundary: untrusted program instruction/CPI frame to runtime account and privilege enforcement

## Attack Surface

- Entrypoint type: native program, loader, SBF/BPF, or CPI invocation
- Sensitive sink: account owner/write privilege, executable program state, or runtime syscall side effect

## Root Cause

The earlier instruction shape and validation path were centered on the ProgramData account. Based on the supplied evidence, the loader did not clearly require the associated Program account to be writable even though extending ProgramData changes executable state associated with that Program account.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch likely hardens Solana's upgradeable BPF loader by changing the extension flow from a ProgramData-centered instruction to a Program-centered instruction and adding a runtime check that rejects the operation when the Program account is not writable. The evidence supports a missing writable-account enforcement issue, but does not establish a concrete exploit such as arbitrary ProgramData modification or privilege escalation.
