# Root-Cause Card

## Metadata

- ID: `bor-2025-04-14-bor-p2p-networking-c5c75977a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-peer-churn`
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

- Primary impact: peer-isolation-risk
- Secondary impact: low severity conditions

## Short Reusable Lesson

- The supplied evidence supports a missing peer-churn mechanism when connection slots were saturated: incumbent peers could persist until timeout or protocol error, leaving limited turnover. The evidence does not show a stronger root cause such as an exploit primitive, authentication failure, or consensus issue.
