# Root-Cause Card

## Metadata

- ID: `solana-2019-06-10-solana-consensus-807c69d97c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `account-permission-invariant-hardening`
- Confidence tier: `tier_b_likely`

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

The evidence supports that the previous code lacked explicit post-instruction checks for the credit-only/non-debitable account permission class in the shown path. It does not prove that this omission was exploitable, only that the patch made the invariant explicit and propagated related credit metadata through storage.

## Impact Pattern

- Primary impact: runtime-authorization-hardening, account-state-integrity
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch adds explicit verification checks for non-debitable credit-only accounts and updates account storage to carry lamport-credit metadata. This is plausibly security relevant because it concerns runtime account authorization semantics, but the provided evidence does not establish a concrete vulnerability, exploit path, or production impact. It may be part of safely implementing or refactoring the credit-only account model.
