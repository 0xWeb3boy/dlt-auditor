# Validation Card

## Metadata

- ID: `solana-2019-10-29-solana-staking-a587d05098`
- Bug family: `staking_registry_and_accountability`
- Bug class: `stake-redelegation-invariant-hardening`

## What Confirmed The Issue

- Adds an explicit `TooSoonToRedelegate` guard when `self.voter_pubkey_epoch == clock.epoch`.
- Replaces a standalone `epoch` argument with `&sysvar::clock::Clock`, tying redelegation checks to runtime epoch data.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: defense_in_depth_or_input_hardening
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
