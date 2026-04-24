# Root-Cause Card

## Metadata

- ID: `sui-2024-03-19-sui-rpc-client-api-f553732753`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rpc-epoch-filter-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-transition-invariant`

## Violated Invariant

- Invariant: Consensus and checkpoint state must advance only from inputs bound to the correct epoch, quorum, ordering, and finalized state.

## Trust Boundary

- Boundary: remote client/proxy request or response -> node API trust decision

## Attack Surface

- Entrypoint type: rpc-handler
- Sensitive sink: advancing consensus, checkpoint, epoch, or finalized state

## Impact Pattern

- Primary impact: network-request-filtering
- Secondary impact: consensus-epoch-isolation

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The supported finding is narrow: the patch adds an epoch-based authorization/filter layer to Sui's Anemo consensus RPC router. The evidence shows the pre-patch route had peer authorization via `AllowedPeers` and the patched route additionally applies `AllowedEpoch`, which rejects missing or mismatched `epoch` headers.
