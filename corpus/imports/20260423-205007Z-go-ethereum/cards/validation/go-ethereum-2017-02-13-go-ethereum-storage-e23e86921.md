# Validation Card

## Metadata

- ID: `go-ethereum-2017-02-13-go-ethereum-storage-e23e86921`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-content-integrity-check`

## What Confirmed The Issue

- Evidence 1: Incoming store-request handling now computes a hash over req.SData and compares it with req.Key.
- Evidence 2: Invalid incoming chunks are logged and ignored instead of being accepted into the normal chunk update path.

## What Could Have Invalidated It

- Compensating control 1: Validated only as Swarm chunk integrity hardening, not as a proven high-impact vulnerability fix.
- Compensating control 2: Do not claim transaction validation, consensus safety, or Ethereum core protocol impact.

## Severity Guidance

- Expected impact band: low
- Expected severity band: low

## False-Positive Cautions

- Caution 1: Validated only as Swarm chunk integrity hardening, not as a proven high-impact vulnerability fix.
- Caution 2: Do not claim transaction validation, consensus safety, or Ethereum core protocol impact.
