# Root-Cause Card

## Metadata

- ID: `solana-2019-06-20-solana-cryptography-aacb38864c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invalid-fork-replay-handling`
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

Fatal replay failures were not shown to be consistently converted into dead-fork state before later replay decisions. The supported root cause is missing or incomplete dead-fork propagation between replay result handling, in-memory fork progress, and Blocktree dead-slot tracking.

## Impact Pattern

- Primary impact: consensus-integrity, replay-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch improves Solana replay-stage dead-fork handling by classifying some replay failures as fatal, marking the affected slot dead, and skipping forks already marked dead in replay progress. The evidence supports consensus-replay correctness and possible security relevance, but it does not establish an exploitable vulnerability, finalized consensus divergence, fund loss, or attacker control.
