# Root-Cause Card

## Metadata

- ID: `geth-arb-2015-03-25-go-ethereum-cryptography-de7af720d6`
- Bug family: `resource_accounting_and_limits`
- Bug class: `udp-reflection-amplification`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `request-response-cost-symmetry`

## Violated Invariant

- Invariant: A peer should not emit a larger UDP response or mutate peer-discovery state until the sender has proven reachability or bonding for the claimed source address.

## Trust Boundary

- Boundary: spoofable UDP discovery packet -> peer table lookup and neighbors response

## Attack Surface

- Entrypoint type: p2p discovery request handler
- Sensitive sink: amplified network response and peer-table mutation

## Impact Pattern

- Primary impact: network-amplification
- Secondary impact: denial-of-service
- Severity guide: medium-high

## Short Reusable Lesson

- The discovery handler could answer a small unauthenticated request with larger neighbor traffic before sender reachability was established. Require bonding or reachability proof before table lookup, table mutation, or neighbor response generation.
