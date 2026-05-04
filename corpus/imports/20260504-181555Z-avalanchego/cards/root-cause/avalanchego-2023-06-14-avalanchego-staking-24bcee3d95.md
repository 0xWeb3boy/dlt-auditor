# Root-Cause Card

## Metadata

- ID: `avalanchego-2023-06-14-avalanchego-staking-24bcee3d95`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `management-key-authorization`

## Violated Invariant

- Invariant: Lifecycle operations on validator or staking objects must be authorized by the explicit management authority of the target object.

## Trust Boundary

- Boundary: A submitted staking management transaction crosses from user-controlled transaction data into validator lifecycle state changes.

## Attack Surface

- Entrypoint type: staking stop-management transaction verification
- Sensitive sink: stopping or modifying an active continuous staker

## Impact Pattern

- Primary impact: unauthorized-staker-stop, validator-lifecycle-integrity
- Secondary impact: medium_or_low_hardening

## Root Cause

- The prior StopStakerTx authorization path was tied to ownership fields derived from the target transaction type rather than the management key associated with a continuous staker. Based on the patch, that was not the intended authority for stopping continuous stakers. ## Walkthrough 1. verifyStopStakerTx syntactically verifies the signed StopStakerTx. 2.

## Short Reusable Lesson

- Stop-staker authorization was changed to require the target continuous staker management key. The reusable shape is a lifecycle operation that previously authorized against adjacent owner fields instead of the object-specific management authority.
