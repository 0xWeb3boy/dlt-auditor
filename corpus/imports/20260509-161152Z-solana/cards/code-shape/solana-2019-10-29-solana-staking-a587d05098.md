# Code-Shape Card

## Metadata

- ID: `solana-2019-10-29-solana-staking-a587d05098`
- Bug family: `staking_registry_and_accountability`
- Bug class: `stake-redelegation-invariant-hardening`

## Code Shape Summary

The patch changes Solana stake redelegation so a stake cannot be redelegated again when its recorded `voter_pubkey_epoch` equals the current `clock.epoch`. This replaces a looser `epoch: Epoch` parameter with the runtime clock and adds a `TooSoonToRedelegate` failure for same-epoch redelegation. The evidence supports a behavioral fix to redelegation rules, but not a confirmed or likely vulnerability.

## Search Motifs

- search for stake redelegation invariant hardening checks near staking entrypoints
- compare validation before and after the consensus-state-transition-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add an explicit state-transition guard using authoritative runtime epoch data before mutating stake delegate history.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
