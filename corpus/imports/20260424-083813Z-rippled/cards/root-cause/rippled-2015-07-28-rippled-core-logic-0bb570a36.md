# Root-Cause Card

## Metadata

- ID: `rippled-2015-07-28-rippled-core-logic-0bb570a36`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-ledger-compatibility`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-safety-invariant`

## Violated Invariant

- Invariant: Consensus participants must only advance local safety or liveness state from messages that satisfy the current quorum, ordering, timing, and validator-role rules.

## Trust Boundary

- Boundary: protocol-controlled input -> core ledger/application invariant

## Attack Surface

- Entrypoint type: state-transition-or-core-validation-path
- Sensitive sink: ledger invariant, protocol state, or node safety decision

## Impact Pattern

- Primary impact: state-consistency, consensus-safety
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- The patch adds ledger compatibility checks around consensus ledger handling. The strongest visible evidence is in NetworkOPs::checkLastClosedLedger, where the node now retrieves or acquires the proposed consensus ledger and refuses to switch to it if LedgerMaster::isCompatible reports it is incompatible with the validated ledger.
