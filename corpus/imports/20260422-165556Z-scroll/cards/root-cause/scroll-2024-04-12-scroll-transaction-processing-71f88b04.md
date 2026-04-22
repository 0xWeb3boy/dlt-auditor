# Root-Cause Card

## Metadata

- ID: `scroll-2024-04-12-scroll-transaction-processing-71f88b04`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cryptographic-binding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `cryptographic-binding`

## Violated Invariant

- Invariant: A blob-backed proof challenge should bind the canonical versioned blob hash that corresponds to the exact data-availability blob handed to downstream verification.

## Trust Boundary

- Boundary: `blob-data-construction->proof-challenge`

## Attack Surface

- Entrypoint type: `data-availability-encoding`
- Sensitive sink: `challenge preimage and commitment material consumed by proof generation or verification`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- A blob-backed proof challenge should bind the canonical versioned blob hash that corresponds to the exact data-availability blob handed to downstream verification. The patch changes blob construction so it computes an EIP-4844 blob versioned hash, appends that hash to the challenge preimage, and returns it to callers. That is a real cryptographic-binding change in the DA encoding path. However, the supplied evidence does not show the downstream `piHash` use, verifier behavior, or any concrete acceptance flaw, so the material supports a security-relevant hardening/fix thesis only weakly and does not establish an actual vulnerability end to end. The robust fix is to return the canonical versioned blob hash from DA blob construction and include it explicitly in the challenge-binding data that downstream components consume.
