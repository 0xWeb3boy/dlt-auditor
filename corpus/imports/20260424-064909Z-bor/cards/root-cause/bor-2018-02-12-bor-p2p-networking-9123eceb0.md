# Root-Cause Card

## Metadata

- ID: `bor-2018-02-12-bor-p2p-networking-9123eceb0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-request-response-correlation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `network peer authenticity and protocol state validation`

## Violated Invariant

- Invariant: A node must authenticate, correlate, and validate peer-controlled protocol data before using it to advance handshake, sync, or peer-state decisions.

## Trust Boundary

- Boundary: remote peer to node networking boundary

## Attack Surface

- Entrypoint type: inbound p2p message, handshake, or sync response handler
- Sensitive sink: peer table mutation, sync scheduling, or message acceptance

## Impact Pattern

- Primary impact: discovery-integrity
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The clearest pre-patch issue in the evidence is that ping/pong handling did not correlate the accepted pong to the exact sent ping; the callback accepted any pong for that pending request. The remaining changes address initialization timing, revalidation, and routing-table hygiene, but the provided excerpts do not establish them as the root cause of a specific security flaw.
