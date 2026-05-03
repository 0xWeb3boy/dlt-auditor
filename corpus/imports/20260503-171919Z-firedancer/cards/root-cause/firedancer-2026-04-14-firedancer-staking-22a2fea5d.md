# Root-Cause Card

## Metadata

- ID: `firedancer-2026-04-14-firedancer-staking-22a2fea5d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-owner-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `owner-program-validation`

## Violated Invariant

- Invariant: Account contents must not be interpreted as vote-state data unless the owning program matches the expected vote program.

## Trust Boundary

- Boundary: Runtime account metadata crossing into staking refresh logic.

## Attack Surface

- Entrypoint type: account refresh and vote-account validation helper
- Sensitive sink: vote-state parsing inside a stake refresh path

## Impact Pattern

- Primary impact: state integrity
- Secondary impact: authorization hardening

## Short Reusable Lesson

- The refresh path trusted account shape and initialization state before checking the owner program, so non-vote accounts could be interpreted as vote-state data.
