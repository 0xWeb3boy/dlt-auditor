# Root-Cause Card

## Metadata

- ID: `solana-2021-06-01-solana-cryptography-b000d490ce`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-mitigation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting-and-bounds`

## Violated Invariant

- Protocol input must satisfy resource accounting and bounds before it can reach stake delegation, withdrawal, reward accounting, vote authority, or validator weight.

## Trust Boundary

- Boundary: signed stake/vote instruction to stake-weighted accounting state

## Attack Surface

- Entrypoint type: stake or vote program instruction
- Sensitive sink: stake delegation, withdrawal, reward accounting, vote authority, or validator weight

## Root Cause

The grounded issue is the absence, in the provided banking-stage evidence, of admission-time cost tracking tied to estimated transaction cost and shared block/account limits. The evidence does not prove that this absence was exploitable as a denial-of-service vulnerability.

## Impact Pattern

- Primary impact: denial-of-service
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch introduces cost-based transaction admission and accounting in Solana's banking stage. It adds CostModel/CostTracker plumbing, filters over-limit transactions into a retryable/unprocessed path, and accounts cost only for processed transactions. The evidence supports resource-management hardening, not a confirmed vulnerability fix, signature-validation fix, or replay fix.
