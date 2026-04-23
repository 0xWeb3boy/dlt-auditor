# Root-Cause Card

## Metadata

- ID: `go-ethereum-2018-02-12-go-ethereum-p2p-networking-9123eceb0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-response-correlation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: UDP discovery pong handling should ideally correlate a pong to the specific ping that caused it by checking ReplyTok against the encoded ping hash. The patch implements that correlation, but the provided evidence does not establish that the prior behavior was exploitable or security-impacting.

## Trust Boundary

- Boundary: Untrusted RPC or debug request parameters reaching privileged node logic.

## Attack Surface

- Entrypoint type: `rpc method`
- Sensitive sink: `expensive RPC-side computation, allocation, or response construction`

## Impact Pattern

- Primary impact: `p2p-protocol-integrity`
- Secondary impact: `replay-resistance`

## Short Reusable Lesson

- The strongest grounded change is in p2p/discover/udp.go: ping handling moved from accepting any pong payload for the pending node to accepting only pongs whose ReplyTok matches the hash of the encoded ping.
