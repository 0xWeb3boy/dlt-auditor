# Root-Cause Card

## Metadata

- ID: `solana-2021-10-06-solana-cryptography-db85d659b9`
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

The evidence supports an incomplete resource-accounting design before this rollout, not a demonstrated vulnerability root cause. It does not show a specific attacker-controlled input, consensus failure, state corruption, or cryptographic flaw.

## Impact Pattern

- Primary impact: denial-of-service
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch is a broad Solana cost-model rollout across banking, replay, runtime execution, blockstore persistence, and tooling. It appears to add resource accounting and block/transaction cost limits, with some security-relevant motivation, but the supplied evidence does not prove that it fixes a specific vulnerability.
