# Code-Shape Card

## Metadata

- ID: `solana-2021-03-11-solana-core-logic-cc38ae72e7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `writable-account-boundary-hardening`

## Code Shape Summary

The patch likely fixes a security-relevant writable-account boundary issue in Solana's BPF loader deserialization. The supplied evidence shows that the unaligned deserializer previously copied account fields such as lamports from the program output buffer for every non-duplicate account, with no shown writable-account condition. The patch threads a skip_ro_deserialization flag through the dispatcher and gates that copy-back path on keyed_account.is_writ...

## Search Motifs

- search for writable account boundary hardening checks near core-logic entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Thread an explicit readonly-deserialization policy flag to the deserialization copy-back point and enforce a writable-account gate before applying serialized account state.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
