# Code-Shape Card

## Metadata

- ID: `solana-2019-02-15-solana-core-logic-132c664e18`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cross-program-state-mutation`

## Code Shape Summary

The patch removes rewards-program writes to vote account userdata and adds a vote-program `clear_credits` path with an owner check. The strongest supported finding is state-integrity hardening around program ownership boundaries. The evidence does not establish reward theft, arbitrary account mutation, or consensus failure.

## Search Motifs

- search for cross program state mutation checks near core-logic entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Move account state mutation to the owning program boundary and guard it with an owner check.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
