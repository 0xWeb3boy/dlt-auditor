# Root-Cause Card

## Metadata

- ID: `solana-2022-06-20-solana-cryptography-e71f56c3f2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unchecked-packet-slice-access`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `input-shape-validation`

## Violated Invariant

- Protocol input must satisfy input shape validation before it can reach consensus, accounting, or authorization-sensitive state.

## Trust Boundary

- Boundary: untrusted external input to protocol enforcement layer

## Attack Surface

- Entrypoint type: protocol input or state-transition entrypoint
- Sensitive sink: consensus, accounting, or authorization-sensitive state

## Root Cause

Packet bytes come from a network boundary, but some parsing paths relied on raw indexing and manual offset checks. That made safe handling of malformed offsets depend on each call site performing complete validation correctly.

## Impact Pattern

- Primary impact: denial-of-service
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch likely security-hardens Solana packet ingress and sigverify parsing by replacing raw packet byte indexing with a `Packet::data(...)` accessor that returns `Option`, forcing call sites to handle invalid offsets explicitly. The evidence supports bounds-checking hardening, not a proven signature bypass, replay flaw, memory corruption issue, or confirmed exploitable crash.
