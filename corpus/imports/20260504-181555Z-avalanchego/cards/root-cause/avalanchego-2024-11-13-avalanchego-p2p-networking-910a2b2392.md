# Root-Cause Card

## Metadata

- ID: `avalanchego-2024-11-13-avalanchego-p2p-networking-910a2b2392`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-protocol-message-verification`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-message-verification`

## Violated Invariant

- Invariant: Cross-chain or protocol-extension messages must be verified against network identity, validator state, and the relevant chain height before they affect transaction or block acceptance.

## Trust Boundary

- Boundary: Messages embedded in transactions or blocks cross from peer/builder input into PlatformVM state transition.

## Attack Surface

- Entrypoint type: PlatformVM transaction packing, manager verification, and block verification
- Sensitive sink: acceptance of transactions or blocks carrying unverified Warp messages

## Impact Pattern

- Primary impact: protocol-integrity, cross-chain-message-integrity
- Secondary impact: medium_or_low_hardening

## Root Cause

- The grounded issue is an implementation gap: the shown PlatformVM paths did not yet include explicit Warp message verification at transaction and block verification ingress points. The evidence does not prove state corruption, consensus failure, remote exploitability, or production reachability of invalid Warp messages. ## Walkthrough 1.

## Short Reusable Lesson

- Warp message verification was wired into transaction and block acceptance paths. The reusable shape is an extension message whose validity depends on external network and validator context and must be checked everywhere the enclosing object is accepted.
