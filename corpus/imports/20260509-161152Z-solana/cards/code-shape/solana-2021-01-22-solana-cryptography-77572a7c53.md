# Code-Shape Card

## Metadata

- ID: `solana-2021-01-22-solana-cryptography-77572a7c53`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cpi-writable-privilege-tracking`

## Code Shape Summary

The patch is likely a security fix for CPI writable privilege tracking. The supplied evidence shows caller account writability being captured in the BPF loader syscall path and passed into runtime account verification, but it does not include the full PreAccount::verify logic, a regression test, or a concrete exploit, so the draft's confirmed/high-confidence claim should be downgraded.

## Search Motifs

- search for cpi writable privilege tracking checks near cryptography entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Capture caller-derived privileges at the CPI boundary and thread them into post-instruction account verification so writable checks are based on effective caller authority.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
