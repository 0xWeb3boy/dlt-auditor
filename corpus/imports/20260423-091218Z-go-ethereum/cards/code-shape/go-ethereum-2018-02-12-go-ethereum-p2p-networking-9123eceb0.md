# Code-Shape Card

## Metadata

- ID: `go-ethereum-2018-02-12-go-ethereum-p2p-networking-9123eceb0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-response-correlation`

## Code Shape Summary

- A pending network callback accepted any reply of the right type for a peer, and the fix adds a request-derived token check so only the exact matching response clears the pending slot.

## Search Motifs

- Motif 1: Callback predicate is `true` or otherwise ignores reply token contents.
- Motif 2: Request is encoded first so its hash or nonce can be stored for later reply validation.
- Motif 3: Reply handler adds `bytes.Equal`, nonce comparison, or token matching against a pending entry.

## Typical Asymmetry

- The attacker can send many plausible-looking replies, while the defender only intended to accept the one reply cryptographically or structurally bound to the original request.

## Patch Pattern

- Capture a request-derived token before sending and validate that replies echo or derive from that token before updating peer state.

## False Match Warnings

- Broad networking cleanup is not enough; the key signal is explicit reply-token correlation.
- Do not match if the transport or session layer already authenticated and correlated replies before this function runs.
