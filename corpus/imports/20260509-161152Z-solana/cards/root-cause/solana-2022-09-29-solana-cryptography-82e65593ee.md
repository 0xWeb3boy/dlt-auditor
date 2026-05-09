# Root-Cause Card

## Metadata

- ID: `solana-2022-09-29-solana-cryptography-82e65593ee`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invalid-transaction-forwarding`
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

The forwarding code did not consistently share an explicit pre-forwarding filter/sanitization path for packets that failed sanitization, were too old, or were already processed. Based on the evidence, this is best characterized as forwarding eligibility and buffer-consistency logic, not as a demonstrated security root cause.

## Impact Pattern

- Primary impact: resource-exhaustion, replay-hygiene
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch filters or sanitizes invalid transaction and vote packets before adding them to forwarding batches, and updates buffer removal logic and tests around already-processed transactions. The evidence supports a correctness and resource-hygiene improvement in the forwarding path. It does not prove crashability, signature bypass, transaction forgery, downstream acceptance of invalid packets, or consensus failure.
