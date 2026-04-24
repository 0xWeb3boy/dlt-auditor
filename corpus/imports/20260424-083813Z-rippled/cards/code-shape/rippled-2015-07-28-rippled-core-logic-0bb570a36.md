# Code-Shape Card

## Metadata

- ID: `rippled-2015-07-28-rippled-core-logic-0bb570a36`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-ledger-compatibility`

## Code Shape Summary

- The patch adds ledger compatibility checks around consensus ledger handling. The strongest visible evidence is in NetworkOPs::checkLastClosedLedger, where the node now retrieves or acquires the proposed consensus ledger and refuses to switch to it if LedgerMaster::isCompatible... Reusable shape: check for consensus-safety-invariant was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-transition-or-core-validation-path missing exact consensus-safety-invariant check before ledger invariant, protocol state, or node safety decision
- Motif 2: security-sensitive path reaches ledger invariant, protocol state, or node safety decision before rejecting malformed, stale, or unauthorized input
- Motif 3: Centralize ledger compatibility checking and call it before switching to a candidate consensus ledger.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger invariant, protocol state, or node safety decision unless the consensus-safety-invariant gate runs before the state-changing branch.

## Patch Pattern

- Centralize ledger compatibility checking and call it before switching to a candidate consensus ledger.

## False Match Warnings

- No demonstrated exploit path is provided.
- No shown consensus fork, validation failure, or attacker-controlled input path is proven.
