# Root-Cause Card

## Metadata

- ID: `sei-chain-2026-02-19-sei-chain-consensus-4d45fcdc8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-consensus-state-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `verified-certificate-gating`

## Violated Invariant

- Invariant: Consensus state mutation must use only quorum certificates that were needed and verified for the current transition.

## Trust Boundary

- Boundary: incoming consensus certificate/block metadata -> local Autobahn data state

## Attack Surface

- Entrypoint type: quorum-certificate-push-handler
- Sensitive sink: updating stored QC ranges, headers, and block-match state

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: local-availability

## Short Reusable Lesson

- Use the same validation predicate for both verification and mutation, and validate dependent data against canonical locally stored verified state rather than untrusted incoming metadata. Protects consensus data state from stale QC mutation. Prevents update notifications from unneeded QCs. Avoids trusting headers from an unverified incoming QC for block matching.
