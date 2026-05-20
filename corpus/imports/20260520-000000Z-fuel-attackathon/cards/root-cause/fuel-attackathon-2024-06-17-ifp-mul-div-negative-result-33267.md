# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-mul-div-negative-result-33267`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-multiply-divide-sign-misbinding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `operand-sign-comparison`

## Violated Invariant

- Signed fixed-point multiply/divide must return negative output when exactly one operand is negative.

## Trust Boundary

- Boundary: `contract-input->financial-math-library`
- Entrypoint type: `library-function`
- Sensitive sink: `IFP64/IFP128/IFP256 multiply or divide result`

## Attack Surface

- Pass one negative operand to multiply or divide.
- Use the result in user-facing contract math.

## Exploit Preconditions

- The non_negative expression never examines the second operand's sign.
- The result controls value, eligibility, or liveness.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `asset-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Duplicated arithmetic code across widths should share tested sign logic or generated test vectors.
