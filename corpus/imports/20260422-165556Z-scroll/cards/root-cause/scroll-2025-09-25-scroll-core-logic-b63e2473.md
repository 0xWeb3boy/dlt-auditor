# Root-Cause Card

## Metadata

- ID: `scroll-2025-09-25-scroll-core-logic-b63e2473`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verifier-configuration-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `configuration-binding`

## Violated Invariant

- Invariant: Verifier initialization should derive versioned configuration from the same fork and mode metadata that governs the proof being checked.

## Trust Boundary

- Boundary: `proof-task-metadata->verifier-initialization`

## Attack Surface

- Entrypoint type: `query-verification-path`
- Sensitive sink: `selected verifier configuration used for PI-hash checks or proof verification`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Verifier initialization should derive versioned configuration from the same fork and mode metadata that governs the proof being checked. The supplied evidence supports a correctness fix in verifier initialization and configuration plumbing: version is now carried explicitly and can be derived from fork name plus validium mode. That is plausibly relevant to PI-hash checking, but the snippets do not establish a concrete vulnerability, exploit path, or even whether the pre-fix behavior caused false accepts rather than only false rejects or misconfiguration. The robust fix is to carry explicit version metadata through verifier configuration objects and derive it canonically from fork name plus validium mode when constructing verifier state.
