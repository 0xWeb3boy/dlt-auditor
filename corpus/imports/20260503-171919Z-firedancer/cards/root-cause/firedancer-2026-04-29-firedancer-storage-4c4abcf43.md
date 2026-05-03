# Root-Cause Card

## Metadata

- ID: `firedancer-2026-04-29-firedancer-storage-4c4abcf43`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `http-content-length-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `strict-positive-content-length-validation`

## Violated Invariant

- Invariant: Snapshot restore should only trust strictly valid, positive Content-Length metadata before accepting or allocating around a response body.

## Trust Boundary

- Boundary: HTTP response headers and snapshot size metadata crossing into restore logic.

## Attack Surface

- Entrypoint type: snapshot HTTP header parser
- Sensitive sink: snapshot size metadata and restore-state transitions

## Impact Pattern

- Primary impact: snapshot restore integrity
- Secondary impact: input validation hardening

## Short Reusable Lesson

- Restore logic used permissive Content-Length parsing and accepted zero or malformed values as if they were valid snapshot sizes.
