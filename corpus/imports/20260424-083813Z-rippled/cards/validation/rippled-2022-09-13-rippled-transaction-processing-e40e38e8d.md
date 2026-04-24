# Validation Card

## Metadata

- ID: `rippled-2022-09-13-rippled-transaction-processing-e40e38e8d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unauthorized-resource-consumption`

## What Confirmed The Issue

- Evidence 1: Commit body explicitly says the tfTrustLine feature could be used to attack the NFToken issuer.
- Evidence 2: Added comments state TrustLines could be added to the issuer without explicit issuer permission.

## What Could Have Invalidated It

- Compensating control 1: The supplied snippets do not show the full final conditional logic in NFTokenMint::preflight.
- Compensating control 2: The exact exploit transaction sequence is described in comments but not demonstrated in provided tests.

## Severity Guidance

- Expected impact band: security-impact: resource-exhaustion, economic-denial-of-service
- Expected severity band: high

## False-Positive Cautions

- Caution 1: The supplied snippets do not show the full final conditional logic in NFTokenMint::preflight.
- Caution 2: The exact exploit transaction sequence is described in comments but not demonstrated in provided tests.
