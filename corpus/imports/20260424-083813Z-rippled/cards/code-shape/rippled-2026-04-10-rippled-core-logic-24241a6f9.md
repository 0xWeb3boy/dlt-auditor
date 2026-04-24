# Code-Shape Card

## Metadata

- ID: `rippled-2026-04-10-rippled-core-logic-24241a6f9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `asset-restriction-enforcement`

## Code Shape Summary

- The supported finding is a likely security fix for incomplete MPT and issued-asset restriction checks in specific CheckCreate and OfferCreate paths. Reusable shape: check for input-validation was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-transition-or-core-validation-path missing exact input-validation check before ledger invariant, protocol state, or node safety decision
- Motif 2: security-sensitive path reaches ledger invariant, protocol state, or node safety decision before rejecting malformed, stale, or unauthorized input
- Motif 3: Compose all relevant asset restriction checks at each transaction entry point and propagate the precise TER from shared helpers rather than treating authorization, freeze, lock, and transfer-disabled checks as interchangeable.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger invariant, protocol state, or node safety decision unless the input-validation gate runs before the state-changing branch.

## Patch Pattern

- Compose all relevant asset restriction checks at each transaction entry point and propagate the precise TER from shared helpers rather than treating authorization, freeze, lock, and transfer-disabled checks as interchangeable.

## False Match Warnings

- No advisory, issue text, or commit body explicitly states a security vulnerability.
- No proof that the prior behavior enabled theft, unauthorized minting or burning, or unauthorized asset movement.
