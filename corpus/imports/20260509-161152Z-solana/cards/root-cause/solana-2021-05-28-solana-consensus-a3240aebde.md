# Root-Cause Card

## Metadata

- ID: `solana-2021-05-28-solana-consensus-a3240aebde`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `read-only-account-mutation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authorization-and-privilege-check`

## Violated Invariant

- Protocol input must satisfy authorization and privilege check before it can reach bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status.

## Trust Boundary

- Boundary: peer-provided ledger/vote evidence to local consensus and fork-choice state

## Attack Surface

- Entrypoint type: block replay, vote processing, fork-choice update, or duplicate-slot recovery
- Sensitive sink: bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status

## Root Cause

The supported root cause is inconsistent read-only account state handling in BPF/CPI execution paths: account lookup did not always prioritize the original pre-instruction account object, and BPF parameter deserialization could skip read-only account fields, weakening the runtime's ability to observe attempted modifications.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Medium

## Short Reusable Lesson

The patch is a security fix for Solana BPF/CPI account handling. It strengthens detection of programs modifying read-only accounts by changing account lookup to prefer pre-instruction account state and by removing a deserialization path that skipped read-only account fields.
