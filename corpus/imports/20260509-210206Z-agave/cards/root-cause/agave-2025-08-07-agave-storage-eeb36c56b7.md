# Root-Cause Card

## Metadata

- ID: `agave-2025-08-07-agave-storage-eeb36c56b7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `allocation-bound-by-concrete-input`

## Violated Invariant

- Invariant: Temporary buffers for untrusted or semi-trusted archive unpacking should be bounded by concrete input size and configured limits, not by a larger abstract output limit alone.

## Trust Boundary

- Boundary: `snapshot-or-genesis-archive->node-filesystem`

## Attack Surface

- Entrypoint type: `archive-unpack-path`
- Sensitive sink: temporary unpack write-buffer allocation
- Attacker capability: Provide, mirror, or influence archive files that a node unpacks.
- Key precondition: The node unpacks an attacker-influenced or untrusted archive.

## Impact Pattern

- Primary impact: `resource-exhaustion`
- Secondary impact: `node-availability`
- Severity guidance: `low` because The change reduces unnecessary memory/backlog exposure, but no exploit path, crash, OOM, or attacker-controlled distribution channel was proven.

## Short Reusable Lesson

- Archive unpacking chooses temporary write-buffer sizes from broad configured output limits, including a forced minimum, instead of the smaller actual archive size.
- Structural fix: Compute unpack buffers from min(input archive size, effective unpack limit), cap them, and adjust downstream buffer handling for smaller bounded writes.
