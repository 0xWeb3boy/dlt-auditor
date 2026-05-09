# Root-Cause Card

## Metadata

- ID: `solana-2021-10-06-solana-cryptography-1dd6dc3709`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-accounting-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting-and-bounds`

## Violated Invariant

- Protocol input must satisfy resource accounting and bounds before it can reach bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status.

## Trust Boundary

- Boundary: peer-provided ledger/vote evidence to local consensus and fork-choice state

## Attack Surface

- Entrypoint type: block replay, vote processing, fork-choice update, or duplicate-slot recovery
- Sensitive sink: bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status

## Root Cause

The supported root cause is incomplete or newly introduced resource-accounting coverage across transaction packing, execution timing feedback, learned program-cost state, and block cost enforcement. The evidence does not prove a concrete vulnerability trigger or exploit path.

## Impact Pattern

- Primary impact: availability, resource-exhaustion
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The evidence supports a conservative security-hardening classification for Solana's cost-model/resource-accounting subsystem. The commit broadly introduces and wires cost tracking, execution-cost feedback, bounded cost-table state, persistence, and block cost rejection. It does not establish a specific exploit, cryptographic flaw, or proven prior consensus violation.
