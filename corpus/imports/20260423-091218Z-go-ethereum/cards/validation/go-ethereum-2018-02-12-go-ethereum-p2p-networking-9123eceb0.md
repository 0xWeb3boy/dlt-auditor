# Validation Card

## Metadata

- ID: `go-ethereum-2018-02-12-go-ethereum-p2p-networking-9123eceb0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-response-correlation`

## What Confirmed The Issue

- Evidence 1: The pending pong callback changed from unconditional acceptance to checking `ReplyTok` against the encoded ping hash.
- Evidence 2: The code now computes and keeps a request-derived token before the packet is sent, which is a classic reply-correlation hardening pattern.

## What Could Have Invalidated It

- Compensating control 1: Another layer already authenticated and correlated replies, making the callback check redundant.
- Compensating control 2: The pending reply result never influenced any trust, liveness, or routing-table decision.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Keep the classification at likely hardening unless exploitability or misuse is actually demonstrated.
- Caution 2: The surrounding discovery-table changes are mostly reliability work; do not attribute them all to the security claim.
