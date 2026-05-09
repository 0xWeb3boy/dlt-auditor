# Root-Cause Card

## Metadata

- ID: `solana-2019-10-29-solana-staking-a587d05098`
- Bug family: `staking_registry_and_accountability`
- Bug class: `stake-redelegation-invariant-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-state-transition-invariant`

## Violated Invariant

- Protocol input must satisfy consensus state transition invariant before it can reach bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status.

## Trust Boundary

- Boundary: peer-provided ledger/vote evidence to local consensus and fork-choice state

## Attack Surface

- Entrypoint type: block replay, vote processing, fork-choice update, or duplicate-slot recovery
- Sensitive sink: bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status

## Root Cause

The redelegation logic did not explicitly reject a second delegate change in the same epoch, and the tests encoded repeated redelegation as valid behavior. The supplied evidence does not prove that this led to exploitable corruption, fund loss, slashing bypass, or consensus divergence.

## Impact Pattern

- Primary impact: protocol-integrity, slashing-accounting-integrity
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch changes Solana stake redelegation so a stake cannot be redelegated again when its recorded `voter_pubkey_epoch` equals the current `clock.epoch`. This replaces a looser `epoch: Epoch` parameter with the runtime clock and adds a `TooSoonToRedelegate` failure for same-epoch redelegation. The evidence supports a behavioral fix to redelegation rules, but not a confirmed or likely vulnerability.
