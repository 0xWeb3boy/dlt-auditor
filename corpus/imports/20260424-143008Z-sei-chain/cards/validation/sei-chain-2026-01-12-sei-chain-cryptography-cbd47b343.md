# Validation Card

## Metadata

- ID: `sei-chain-2026-01-12-sei-chain-cryptography-cbd47b343`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `traffic-analysis-hardening`

## What Confirmed The Issue

- Evidence 1: Commit body explicitly says constant-size frames are needed to defend against message length analysis.
- Evidence 2: SecretConnection.Write now buffers caller data into sendState.data instead of immediately constructing frames per write loop.

## What Could Have Invalidated It

- Compensating control 1: The protocol does not attempt to hide message sizes.
- Compensating control 2: Transport framing already pads or batches writes below this layer.

## Severity Guidance

- Expected impact band: confidentiality-or-key-lifecycle-hardening
- Expected severity band: low_or_informational

## False-Positive Cautions

- Caution 1: The protocol does not attempt to hide message sizes.
- Caution 2: Transport framing already pads or batches writes below this layer.
