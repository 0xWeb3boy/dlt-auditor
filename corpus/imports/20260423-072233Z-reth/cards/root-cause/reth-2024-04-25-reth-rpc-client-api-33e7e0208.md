# Root-Cause Card

## Metadata

- ID: `reth-2024-04-25-reth-rpc-client-api-33e7e0208`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-bad-peer-penalization`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `bad-response-peer-penalization`

## Violated Invariant

- Invariant: Schedulers that consume untrusted peer responses must feed bad-response signals back into peer selection before assigning follow-up work.

## Trust Boundary

- Boundary: Remote block-response data crossing into the local fetch scheduler and peer ranking state.

## Attack Surface

- Entrypoint type: p2p-response-handler
- Sensitive sink: Queued request dispatch and immediate follow-up scheduling.

## Impact Pattern

- Primary impact: Misbehaving peers are less likely to receive repeated fetch work.
- Secondary impact: Scheduler behavior becomes consistent across similar response types.

## Short Reusable Lesson

- The block-bodies response path failed to mark suspect responses and could immediately reuse a bad peer. The patch classifies empty or failed responses as likely bad, records that state, blocks immediate follow-up, and dispatches queued work through best-peer selection.
