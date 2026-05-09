# Root-Cause Card

## Metadata

- ID: `solana-2022-06-28-solana-cryptography-348fe9ebe2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `late-network-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `stake-accountability-invariant`

## Violated Invariant

- Protocol input must satisfy stake accountability invariant before it can reach stake delegation, withdrawal, reward accounting, vote authority, or validator weight.

## Trust Boundary

- Boundary: signed stake/vote instruction to stake-weighted accounting state

## Attack Surface

- Entrypoint type: stake or vote program instruction
- Sensitive sink: stake delegation, withdrawal, reward accounting, vote authority, or validator weight

## Root Cause

Basic shred-header validation was performed later or split across the ingress pipeline, so some invalid packets could reach more expensive downstream work before being rejected. The supplied evidence supports late validation and wasted work, not state corruption or acceptance of invalid shreds into consensus state.

## Impact Pattern

- Primary impact: resource-exhaustion
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch moves basic shred discard checks into the fetch stage so malformed, stale, out-of-range, wrong-version, or out-of-bounds-index shreds are dropped earlier. The evidence supports a resource-saving validation change on network input, but it does not establish a concrete vulnerability, exploit path, consensus bypass, or demonstrated denial-of-service condition.
