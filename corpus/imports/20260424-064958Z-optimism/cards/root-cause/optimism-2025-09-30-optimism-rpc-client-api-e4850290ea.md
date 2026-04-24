# Root-Cause Card

## Metadata

- ID: `optimism-2025-09-30-optimism-rpc-client-api-e4850290ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `race-condition`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: EngineController operations that read or mutate forkchoice-related heads and retry flags should observe one coherent controller state while deciding whether to send forkchoice updates or perform backup-unsafe reorgs.

## Trust Boundary

- Boundary: RPC/API caller -> node service

## Attack Surface

- Entrypoint type: rpc-handler or API validation path
- Sensitive sink: backend forwarding, access-list approval, or service state derived from caller input

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- EngineController operations that read or mutate forkchoice-related heads and retry flags should observe one coherent controller state while deciding whether to send forkchoice updates or perform backup-unsafe reorgs. Similar bugs appear when rpc-handler or API validation path code treats partially checked input as authoritative and lets it reach backend forwarding, access-list approval, or service state derived from caller input. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
