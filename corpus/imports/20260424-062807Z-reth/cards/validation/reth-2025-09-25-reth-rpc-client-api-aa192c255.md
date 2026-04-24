# Validation Card

## Metadata

- ID: `reth-2025-09-25-reth-rpc-client-api-aa192c255`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-auth-header-parsing`

## What Confirmed The Issue

- get_bearer processes the Authorization header before JWT validation.
- The old code accepted Bearer anywhere in the header via find(prefix).

## What Could Have Invalidated It

- No proof that a malformed header could bypass authentication without a valid JWT
- No evidence of downstream parser disagreement or request smuggling impact

## Severity Guidance

- Expected impact band: auth_or_access_control
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that a malformed header could bypass authentication without a valid JWT
- No evidence of downstream parser disagreement or request smuggling impact
