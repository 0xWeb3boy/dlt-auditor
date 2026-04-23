# Root-Cause Card

## Metadata

- ID: `go-ethereum-2020-12-04-go-ethereum-transaction-processing-15339cf1c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signed-vulnerability-advisory-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: The geth vulnerability checker should rely only on advisory feed data authenticated by trusted signing keys before using that data to warn about locally vulnerable versions.

## Trust Boundary

- Boundary: Caller-controlled signing or account-management requests crossing into wallet-held authority.

## Attack Surface

- Entrypoint type: `wallet or signing api`
- Sensitive sink: `transaction or message signing under local account authority`

## Impact Pattern

- Primary impact: `advisory-integrity`
- Secondary impact: `vulnerability-detection`

## Short Reusable Lesson

- The commit adds a cmd/geth vulnerability-check mechanism with signed advisory-feed verification and tests.
