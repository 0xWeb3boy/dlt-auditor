# Root-Cause Card

## Metadata

- ID: `solana-2021-05-28-solana-consensus-2f7f243022`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `read-only-account-modification-bypass`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `account-mutability-enforcement`

## Violated Invariant

- Protocol input must satisfy account mutability enforcement before it can reach bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status.

## Trust Boundary

- Boundary: peer-provided ledger/vote evidence to local consensus and fork-choice state

## Attack Surface

- Entrypoint type: block replay, vote processing, fork-choice update, or duplicate-slot recovery
- Sensitive sink: bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status

## Root Cause

The root cause was a validation gap in the BPF loader/CPI account handling path: read-only account changes could be missed when read-only deserialization was skipped, and account lookup did not first anchor checks to the pre-invocation account snapshot.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Medium

## Short Reusable Lesson

The patch fixes Solana BPF invocation permission enforcement so attempted modifications to read-only accounts are not hidden by deserialization behavior or account lookup source selection.
