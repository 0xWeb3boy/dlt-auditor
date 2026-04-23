# Code-Shape Card

## Metadata

- ID: `reth-2024-04-25-reth-rpc-client-api-33e7e0208`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-bad-peer-penalization`

## Code Shape Summary

- The block-bodies response path failed to mark suspect responses and could immediately reuse a bad peer. The patch classifies empty or failed responses as likely bad, records that state, blocks immediate follow-up, and dispatches queued work through best-peer selection.

## Search Motifs

- response handler ignores empty result before followup_request
- next_peer used where next_best_peer exists
- headers path penalizes bad responses but bodies path does not

## Typical Asymmetry

- The code has one path that performs the expected validation, accounting, or quality update while a nearby special-case, cache-hit, early-return, or alternate response path omits it.

## Patch Pattern

- Propagate response-quality classification into peer state, prevent immediate reuse after suspect output, and choose future work using the quality-aware peer selector.

## False Match Warnings

- Empty responses can be benign at protocol edges.
- Peer ranking internals must actually consume the bad-response flag.
- No DoS claim without evidence of queue growth, resource exhaustion, or repeated attacker control.
