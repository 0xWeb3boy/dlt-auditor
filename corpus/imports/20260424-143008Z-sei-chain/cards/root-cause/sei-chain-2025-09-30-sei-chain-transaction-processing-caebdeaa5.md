# Root-Cause Card

## Metadata

- ID: `sei-chain-2025-09-30-sei-chain-transaction-processing-caebdeaa5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-panic-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `panic-and-error-propagation`

## Violated Invariant

- Invariant: Consensus proposal and finalization paths must convert recoverable processing failures into explicit rejection or error results.

## Trust Boundary

- Boundary: submitted block proposal or transaction bytes -> consensus block processing

## Attack Surface

- Entrypoint type: process-proposal-or-finalizeblock
- Sensitive sink: accepting proposals or finalizing blocks after failed processing

## Impact Pattern

- Primary impact: liveness
- Secondary impact: availability-or-resource-control

## Short Reusable Lesson

- Add panic recovery and explicit error propagation in consensus block-processing paths, and ensure callers abort or return errors instead of ignoring failed processing results. Reduces risk that a panic in block processing escapes expected error handling. Prevents optimistic processing from treating failed ProcessBlock outputs as usable.
