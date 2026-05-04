# Root-Cause Card

## Metadata

- ID: `stellar-core-2019-11-14-stellar-core-storage-57d10fae4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-archive-verification`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `complete-archive-artifact-verification`

## Violated Invariant

- Invariant: A complete catchup or archive-verification mode must verify every archive artifact type that can affect replay, audit, or ledger-result integrity for the selected range.

## Trust Boundary

- Boundary: remote-history-archive -> local-catchup-verification-state

## Attack Surface

- Entrypoint type: state-sync-or-catchup
- Sensitive sink: accepted history archive data and catchup verification result
- Attacker capability: Provide or tamper with remote history archive files used by a catching-up node.
- Main precondition: Complete offline verification excludes transaction result archive files.

## Impact Pattern

- Primary impact: state-sync-integrity
- Secondary impact: archive-integrity, auditability
- Severity guess: medium because Archive verification gaps can affect trust in catchup data, but this finding is scoped to optional complete verification and does not prove live consensus impact.

## Short Reusable Lesson

- Completeness claims in state-sync verification are security properties; every artifact type in the trusted range needs an explicit verification step.
