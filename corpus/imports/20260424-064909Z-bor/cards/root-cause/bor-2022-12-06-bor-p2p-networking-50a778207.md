# Root-Cause Card

## Metadata

- ID: `bor-2022-12-06-bor-p2p-networking-50a778207`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `path-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `integrity validation of untrusted data before use`

## Violated Invariant

- Invariant: A node must authenticate, correlate, and validate peer-controlled protocol data before using it to advance handshake, sync, or peer-state decisions.

## Trust Boundary

- Boundary: remote peer to node networking boundary

## Attack Surface

- Entrypoint type: inbound p2p message, handshake, or sync response handler
- Sensitive sink: peer table mutation, sync scheduling, or message acceptance

## Impact Pattern

- Primary impact: unauthorized-file-access
- Secondary impact: low severity conditions

## Short Reusable Lesson

- The changed code accepted local path strings and used them directly for filesystem operations without a shared resolution step. The evidence supports that this was considered risky path handling, but it does not prove attacker reachability, a specific exploit path, or that the old behavior was independently vulnerable in practice.
