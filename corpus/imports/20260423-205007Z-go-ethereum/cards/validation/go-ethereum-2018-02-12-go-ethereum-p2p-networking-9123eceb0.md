# Validation Card

## Metadata

- ID: `go-ethereum-2018-02-12-go-ethereum-p2p-networking-9123eceb0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-response-correlation`

## What Confirmed The Issue

- Evidence 1: p2p/discover/udp.go changed the pending pong predicate from always true to bytes.Equal(p.(*pong).ReplyTok, hash).
- Evidence 2: The patch now encodes the ping before registering the pending response so the request-derived hash can be used as the expected reply token.

## What Could Have Invalidated It

- Compensating control 1: Classify only the ReplyTok validation as security hardening.
- Compensating control 2: Do not claim a confirmed vulnerability or exploitability from the supplied evidence.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: low

## False-Positive Cautions

- Caution 1: Classify only the ReplyTok validation as security hardening.
- Caution 2: Do not claim a confirmed vulnerability or exploitability from the supplied evidence.
