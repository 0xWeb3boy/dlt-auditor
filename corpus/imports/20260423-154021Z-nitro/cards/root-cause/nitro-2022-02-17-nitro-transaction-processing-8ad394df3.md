# Root-Cause Card

## Metadata

- ID: `nitro-2022-02-17-nitro-transaction-processing-8ad394df3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `challenge-boundary-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `challenge-boundary-consistency`

## Violated Invariant

- Invariant: Challenge setup should derive machine state and boundaries from canonical genesis-relative indices and reject special cases that would point outside the valid dispute range.

## Trust Boundary

- Boundary: `challenge metadata->machine lookup and dispute initialization`

## Attack Surface

- Entrypoint type: `challenge-construction-or-dispute-initialization`
- Sensitive sink: `generating challenge state, ranges, or proof inputs`

## Impact Pattern

- Primary impact: `challenge-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Challenge setup should derive machine state and boundaries from canonical genesis-relative indices and reject special cases that would point outside the valid dispute range. The patch fixes correctness bugs in validator challenge setup and machine initialization around genesis-relative indexing and boundary handling. The shown evidence supports dispute-path correctness hardening, but it does not establish a concrete exploitable vulnerability. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
