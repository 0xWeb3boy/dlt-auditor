# Root-Cause Card

## Metadata

- ID: `solana-2023-06-20-solana-consensus-20a7cdd43d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-exposure`
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

The apparent root cause was an API boundary issue: Bank exposed HardForks in a way that let internal callers obtain a lockable handle rather than only using Bank-mediated access. The provided evidence supports this as mutable state exposure, but not as a demonstrated externally exploitable flaw.

## Impact Pattern

- Primary impact: consensus-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch appears to harden Solana's Bank HardForks API by replacing direct lock-based access with copied hard-fork data and Bank-mediated mutation. The commit message says callers could previously obtain read/write access to HardForks and that this could cause inconsistent handling of valid hard forks. However, the supplied evidence does not establish that an untrusted actor could exploit this, that consensus divergence occurred, or that the changed ca...
