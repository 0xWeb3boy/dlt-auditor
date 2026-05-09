# Code-Shape Card

## Metadata

- ID: `solana-2020-10-02-solana-storage-29af9d1a36`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow-accounting`

## Code Shape Summary

The evidence supports a likely security-relevant accounting fix in Solana Bank rent distribution. The patch changes validator rent-share computation from `u64` intermediate multiplication to feature-gated `u128` arithmetic, then asserts that no leftover lamports remain under the corrected path. The provided evidence does not establish remote exploitability, attacker control of the required values, or a demonstrated consensus split, so the finding should...

## Search Motifs

- search for integer overflow accounting checks near storage entrypoints
- compare validation before and after the checked-arithmetic-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where stake delegation, withdrawal, reward accounting, vote authority, or validator weight is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Use wider integer intermediates for proportional accounting arithmetic, gate the change for runtime rollout, and assert the corrected accounting invariant after distribution.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
